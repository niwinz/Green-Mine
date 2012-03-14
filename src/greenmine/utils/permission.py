# -*- coding: utf-8 -*-

from greenmine.models import ProjectUserRole

def has_project_role(project, user):
    try:
        user_role_object = ProjectUserRole.objects\
            .get(user=user, project=project)
    except ProjectUserRole.DoesNotExist:
        return False

    return user_role_object


def check_role(project, role, user):
    if project.owner == user:
        return True

    user_role_object = has_project_role(project, user)
    if not user_role_object:
        return False

    if isinstance(role, (list,tuple)) and user_role_object.role in role:
        return True

    elif isinstance(role, int) and user_role_object.role == role:
        return True
    
    return False
