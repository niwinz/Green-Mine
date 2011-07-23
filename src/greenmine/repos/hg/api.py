# -*- coding: utf-8 -*-

from mercurial import commands, ui, hg
from mercurial.node import short
from mercurial.util import datestr
from mercurial.templater import templatepath

from django.conf import settings
from django.utils.translation import ugettext as _
#from django.core.exceptions import ImproperlyConfigured

import os, re

__all__ = (
    'create_repository',
    'clone_repository',
    'delete_repository',
    'get_last_changeset',
    'get_changeset_info',
    'is_template',
)

def setup_ui():
    u = ui.ui()
    u.setconfig('ui', 'report_untrusted', 'off')
    u.setconfig('ui', 'interactive', 'off')
    return u


def display_rev(ctx):
    return "%s:%s" % (ctx.rev(), short(ctx.node()))


def create_repository(location):
    """
    Creates a new mercurial repository at the specified location
    if it doesn't exist already.

    Can throw IOErrors or OSErrors if there are any problems creating
    the repository on disk.
    """

    repo_root = settings.REPO_ROOT
    if not os.path.isdir(os.path.join(location, ".hg")):
        if not os.path.exists(location):
            os.mkdir(location)

        u = setup_ui()
        commands.init(u, location)


def clone_repository(location, target):
    u = setup_ui()
    commands.clone(u, location, target, noupdate=True)


def delete_repository(location):
    """
    Deletes the repository at the specified location if
    the REPO_PERMANENT_DELETE setting is True
    """
    #if settings.REPO_PERMANENT_DELETE:
    import shutil
    shutil.rmtree(location)


def get_last_changeset(repo):
    """
    Returns a dictionary with information about 
    TODO: Get the last changeset info
    """
    return get_changeset_info(repo, 'tip')


def get_changeset_info(repo, changeset):
    """
    TODO: Get info in a dictionary about a specific changeset
    """
    repo = hg.repository(setup_ui(), repo)
    ctx = repo[changeset]
    return {
        'changeset': display_rev(ctx),
        'branch': ctx.branch(),
        'tags': ctx.tags(),
        'parents': [display_rev(p) for p in ctx.parents()],
        'user': ctx.user(),
        'date': datestr(ctx.date()),
        'summary': ctx.description().splitlines()[0],
    }


def is_template(template):
    #TODO: Load project mercurial styles
    if templatepath(template):
        return True
    else:
        return False

