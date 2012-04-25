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

    if user.is_superuser or user.is_staff:
        return True

    user_role_object = has_project_role(project, user)
    if not user_role_object:
        return False

    # TODO: refactor required, temporary return True
    return True
