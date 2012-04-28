# -*- coding: utf-8 -*-

from .models import Role, ProjectUserRole

def get_role(name):
    return Role.objects.get(slug=name)

def has_permission(user, project, loc, perm):
    """
    Checks if a user has a concrete permission on
    a project.
    """

    project_user = ProjectUserRole.objects.get(
        project = project,
        user = user
    )
    return getattr(project_user.role, \
            '%s_%s' % (loc.lower(), perm.lower()), False)
