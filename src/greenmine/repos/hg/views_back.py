# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.http import urlquote
from django.utils.encoding import smart_str
from django.conf import settings
from django.template import RequestContext
from django.db.models import Q
from django.conf import settings

from . import HgRequestWrapper
from greenmine.core.modes import Repo, Project

#from hgwebproxy.utils import is_mercurial, basic_auth

from mercurial.hgweb import hgweb
from mercurial import templater
import os

def show_repo(request, pslug, rslug, other=''):
    """
    TODO:
      * control is current_user is authenticated.
      * urls for show-repo
    """

    project = get_object_or_404(Project, slug=pslug)
    repo = get_object_or_404(Repo, slug=rslug)
    repo_url = reverse('show-repo', args=[project.slug, repo.slug])

    response = HttpResponse()
    hgr = HgRequestWrapper(request, response, script_name=repo_url)

    realm = settings.AUTH_REALM
    if requests.is_mercurial:
        authed = request.current_user.username
    else:
        if not repo.can_read(request.current_user):
            raise PermissionDenied(_("You do not have access to this repository"))
        authed = request.current_user.username

    if not authed:
        response.status_code = 401
        response['WWW-Authenticate'] = '''Basic realm="%s"''' % realm
        if request.META['REQUEST_METHOD']=='POST' and request.META['QUERY_STRING'].startswith("cmd=unbundle"):
            # drain request, this is a fix/workaround for http://mercurial.selenic.com/btw/issue1876
            hgr.drain()
        return response
    else:
        hgr.set_user(authed)


    from greenmine.core.utils import make_repo_location
    full_path, relative_path = make_repo_location(project)

    hgserve = hgweb(full_path)
    hgserve.reponame = project.slug

    hgserve.repo.ui.setconfig('web', 'name', smart_str(hgserve.reponame))
    hgserve.repo.ui.setconfig('web', 'description', smart_str(project.description))
    hgserve.repo.ui.setconfig('web', 'contact', smart_str(project.owner.username))
    hgserve.repo.ui.setconfig('web', 'allow_archive', False)

    if os.path.exists(hgwebproxy_settings.STYLES_PATH):
        template_paths = templater.templatepath()
        template_paths.insert(0, settings.STYLES_PATH)
        hgserve.repo.ui.setconfig('web', 'templates', template_paths)
        hgserve.templatepath = hgserve.repo.ui.config('web', 'templates', template_paths)

    hgserve.repo.ui.setconfig('web', 'style', settings.DEFAULT_STYLE)
    hgserve.repo.ui.setconfig('web', 'baseurl', repo_url)
    hgserve.repo.ui.setconfig('web', 'allow_push', authed) #Allow push to the current user
    hgserve.repo.ui.setconfig('web', 'staticurl', settings.HGSTATIC_URL)
    hgserve.repo.ui.setconfig('web', 'push_ssl', 'false')

    # Catch hgweb error to show as Django Exceptions
    try:
        response.write(''.join(each for each in hgserve.run_wsgi(hgr)))
    except KeyError:
        return HttpResponseServerError('Mercurial has crashed', mimetype='text/html')

    if request.is_mercurial:
        return response

    # make sure we return the response without wrapping if content-type is
    # either a binary stream or text/plain (for raw changesets).
    if response['content-type'].split(';')[0] in ('application/octet-stream', 'text/plain'):
        return response

    context = {
        'content': response.content,
        'reponame' : hgserve.reponame,
        'static_url' : hgwebproxy_settings.STATIC_URL,
        'slugpath': request.path.replace(repo.get_absolute_url(), ''),
        'is_root': request.path == repo.get_absolute_url(),
        'repo': repo,
    }
    return render_to_response("hgwebproxy/wrapper.html", context, RequestContext(request))
