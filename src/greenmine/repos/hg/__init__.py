# -*- coding: utf-8 -*-

import cgi
from mercurial import util

class HgRequestWrapper(object):
    """
    request wrapper. The main purpose of this class
    is to wrap Djangos own `Httpresponse` object, so it
    behaves largely as a `WSGI` compliant request object,
    which is what `hgweb` expects.

    `hgweb` does lot of `.write()` operations on the request
    object given, and we simply stream them into Django.

    Notice the `set_user` method, which sets the environment
    variable `REMOTE_USER` to the user you just authenticated.
    This allows `hgweb` to pick up the username as well.

    Example::
        >>> response = Httpresponseonse()
        >>> hgr = _hgrequestWrap(request, response)
        >>> hgwebdir('path to config file').run_wsgi(hgr)
        >>> print response.content
        ...
    """
    def __init__(self, request, response, script_name):
        """
        Expects two parameters;

        Parameters::
         - `request`: The `request` object your view receives.
         - `response`: An instance of `Httpresponse`.
        """
        self.django_request = request
        self.env = request.META
        self._response = response
        # Remove the prefix so HG will think it's running on its own.
        self.env['SCRIPT_NAME'] = script_name
        self.env['PATH_INFO'] = self.env['PATH_INFO'].replace(self.env['SCRIPT_NAME'], "", 1)

        # Make sure there's a content-length.
        if not self.env.has_key('CONTENT_LENGTH'):
            self.env['CONTENT_LENGTH'] = 0

        self.err = self.env['wsgi.errors']
        self.inp = self.env['wsgi.input']
        self.headers = [ ]
        self.out = [ ]

        self.form = cgi.parse(self.inp, self.env, keep_blank_values=1)

    def __iter__(self):
        return iter([])

    def set_user(self, username):
        """
        Sets the username for the requestuest.
        `hgweb` picks up on this, call after you've authenticated.
        """
        self.env['REMOTE_USER'] = username

    def read(self, count= -1):
        return self.inp.read(count)

    def flush(self):
        """
        Doesn't do anything, but `WSGI` request requires it.
        """
        return None

    _responded = False
    def respond(self, code, content_type=None, path=None, length=0):
        """
        `hgweb` uses this for headers, and is necessary to have things
        like "Download tarball" working.
        """

        # Ignore respond calls after the first call since
        # correct behavior for wsgi response objects is respond
        # with the headers at this point and ignore subsequent calls.
        # hgweb sometimes calls respond multiple times which
        # would cause incorrect headers to get set.
        if not self._responded:
            self._response.status_code = code

            self._response['content-type'] = content_type

            if path is not None and length is not None:
                self._response['content-type'] = content_type
                self._response['content-length'] = length
                self._response['content-disposition'] = 'inline; filename=%s' % path

            for directive, value in self.headers:
                self._response[directive.lower()] = value

            self._responded = True

    def header(self, headers=[('Content-Type', 'text/html')]):
        """
        Set a header for the requestuest. `hgweb` uses this too.
        """
        self.headers.extend(headers)

    def write(self, *a):
        """
        Write content to a buffered stream. Can be a string
        or an iterator of strings.
        """
        for thing in a:
            if hasattr(thing, '__iter__'):
                for p in thing:
                    self.write(p)
            else:
                thing = str(thing)
                self._response.write(thing)

    def drain(self):
        '''
        Need to read all data from request, httplib is half-duplex
        '''
        length = int(self.env.get('CONTENT_LENGTH', 0))
        for s in util.filechunkiter(self.inp, limit=length):
            pass

