# -*- coding: utf-8 -*-

from .models import Role, ProjectUserRole

def get_role(name):
    return Role.objects.get(slug=name)

def has_perm(user, project, loc, perm):
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


def has_perms(user, project, perms=[]):
    valid = True

    for pitem in perms:
        if len(pitem) != 2:
            # invalid permssion parameter
            continue

        loc, locperms = pitem
        
        if not isinstance(locperms, (list, tuple)):
            locperms = [locperms]
        
        for locperm in locperms:
            valid = has_perm(user, project, loc, locperm)
            
        if not valid:
            break
            
    return valid
