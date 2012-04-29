# -*- coding: utf-8 -*-

from .models import Role, ProjectUserRole

def get_role(name):
    return Role.objects.get(slug=name)

def has_perm(user, project, loc, perm, pur=None):
    """
    Checks if a user has a concrete permission on
    a project.
    """
    
    if not pur:
        pur = ProjectUserRole.objects.get(project=project, user=user)

    return getattr(pur.role, \
            '%s_%s' % (loc.lower(), perm.lower()), False)


def has_perms(user, project, perms=[]):

    if user.is_superuser:
        return True

    if project.owner == user:
        return True

    pur = ProjectUserRole.objects.get(project=project, user=user)
    valid = True
    for pitem in perms:
        if len(pitem) != 2:
            continue

        loc, locperms = pitem
        if not isinstance(locperms, (list, tuple)):
            locperms = [locperms]
        
        for locperm in locperms:    
            valid = has_perm(user, project, loc, locperm, pur=pur)
            
        if not valid:
            break
            
    return valid
