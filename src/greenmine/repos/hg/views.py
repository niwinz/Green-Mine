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

def show_repo(request, pslug, rslug):
    project = get_object_or_404(Project, slug=pslug)
    repoobj = get_object_or_404(Repo, slug=rslug)
    repo_url = reverse('show-repo', args=[project.slug, repo.slug])

    from greenmine.core.utils import make_repo_location
    full_path, relative_path = make_repo_location(project)
    
    # Initial variables
    #hook.redirect(True)
    mtime = get_mtime(self.repo.spath)
    archives = 'zip', 'gz', 'bz2'
    stripecount = 1

    u = ui.ui()
    repo = hg.repository(u, full_path)
    repo.ui.setconfig('ui', 'report_untrusted', 'off')
    repo.ui.setconfig('ui', 'interactive', 'off')
    #repo.ui.setconfig('web', 'name', smart_str(project.name))
    #repo.ui.setconfig('web', 'description', smart_str(project.desc))
    #repo.ui.setconfig('web', 'contact', smart_str(project.owner.username))
    #repo.ui.setconfig('web', 'allow_archive', False)
    repo.ui.environ = request.META

    #realm = settings.AUTH_REALM
    #if requests.is_mercurial:
    #    authed = request.current_user.username
    #else:
    #    if not repo.can_read(request.current_user):
    #        raise PermissionDenied(_("You do not have access to this repository"))
    #    authed = request.current_user.username
    #
    #if not authed:
    #    response.status_code = 401
    #    response['WWW-Authenticate'] = '''Basic realm="%s"''' % realm
    #    if request.META['REQUEST_METHOD']=='POST' and request.META['QUERY_STRING'].startswith("cmd=unbundle"):
    #        # drain request, this is a fix/workaround for http://mercurial.selenic.com/btw/issue1876
    #        hgr.drain()
    #    return response
    #else:
    #    hgr.set_user(authed)

    #repo.ui.setconfig('web', 'baseurl', repo_url)
    #repo.ui.setconfig('web', 'allow_push', authed) #Allow push to the current user
    #repo.ui.setconfig('web', 'staticurl', settings.HGSTATIC_URL)
    #repo.ui.setconfig('web', 'push_ssl', 'false')
    request.url = request.META['PATH_I']

