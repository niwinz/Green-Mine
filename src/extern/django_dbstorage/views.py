from itertools import chain
import mimetypes
import posixpath
import re
import urllib
import urlparse

from django.core.files.storage import get_storage_class
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.template import loader, Context, Template, TemplateDoesNotExist
from django.views.static import DEFAULT_DIRECTORY_INDEX_TEMPLATE


def is_dir(path):
    """Returns true if *path* refers to a directory."""
    head, part = posixpath.split(path)
    return part in ('', posixpath.curdir, posixpath.pardir)


def validate_path(request, path):
    """
    Clean up given *path* to only allow serving files below document_root.

    Returns a clean path, if there are no weird path elements.

    Otherwise, returns an HttpResponsePermanentRedirect to a clean path.

    Inspired by django.views.static.serve.
    """
    safepath = urllib.unquote(path)
    newpath = posixpath.normpath(safepath).lstrip(posixpath.sep)
    if newpath in (posixpath.curdir, posixpath.sep):
        newpath = ''
    elif newpath and is_dir(path):
        # Fix up ``newpath`` by appending ``/`` at the end, to make
        # it look like a directory.
        newpath += posixpath.sep
    # Redirect if there are weird *path* elements that were collapsed
    # out, or if ``newpath`` is attempted to go further up the tree.
    if newpath != safepath or \
       posixpath.pardir in newpath.split(posixpath.sep):
        # Figure out what the root URL is, by stripping out *path*
        # from the end of ``request.path``.
        root = re.sub(pattern=(r'(.*)' + re.escape(path)), repl=r'\1',
                      string=request.path)
        redirect = urlparse.urljoin(root, newpath)
        # Strip out any extraneous ``/..`` elements in the front of
        # ``redirect``, because you can't go too far up the host tree.
        newpath = re.sub(pattern=('^(?:%s%s)+' %
                                  (re.escape(posixpath.sep),
                                   re.escape(posixpath.pardir))),
                         repl=r'', string=redirect)
        return HttpResponsePermanentRedirect(newpath)
    return newpath


def serve(request, path, document_root=None, show_indexes=False,
          storage_class=None):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$',
         'django_dbstorage.views.serve',
         {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.

    Inspired by django.views.static.serve.
    """
    # Validate that the path is not malicious.
    path = validate_path(request, path)
    if isinstance(path, HttpResponse):
        # ``path`` is actually an HttpResponse and should be served.
        return path
    # Get the storage class, assuming that it's a DocumentStorage class.
    # If storage_class is None, we use settings.DEFAULT_FILE_STORAGE
    storage = get_storage_class(storage_class)(location=document_root)
    # Serve directory listings
    if is_dir(path):
        if show_indexes:
            try:
                return directory_index(storage, path)
            except OSError:
                pass
        raise Http404('Directory indexes are not allowed here.')
    # Serve the file directly out of DatabaseStorage
    try:
        contents = storage.open(path).read()
    except OSError:
        pass
    else:
        mimetype = (mimetypes.guess_type(path)[0] or
                    'application/octet-stream')
        response = HttpResponse(contents, mimetype=mimetype)
        response["Content-Length"] = len(contents)
        return response
    raise Http404('"%s" does not exist' % request.path)


def directory_index(storage, path):
    """
    Inspired by django.views.static.serve.
    """
    try:
        t = loader.select_template(['static/directory_index.html',
                                    'static/directory_index'])
    except TemplateDoesNotExist:
        t = Template(DEFAULT_DIRECTORY_INDEX_TEMPLATE,
                     name='Default directory index template')
    directories, files = storage.listdir(path)
    file_list = chain((f + '/' for f in directories if not f.startswith('.')),
                      (f for f in files if not f.startswith('.')))
    c = Context({
        'directory': path.rstrip('/') + '/',
        'file_list': file_list,
    })
    return HttpResponse(t.render(c))
