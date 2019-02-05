from polydrive.services import resource_action
from polydrive.models import role_type, Resource


def check_resource_rights(res, user, action):
    """
    Check if a user can access a resource.

    :param res: resource to check
    :param user: user accessing the resource
    :param action: ongoing action's type
    :return: if the user can perform the action
    """
    if res is not None:
        if res.owner_id == user.id:
            return True
        role = Resource.get_rights(res, user)
        if role is not None:
            if action == resource_action.read:
                return True
            if action == resource_action.write:
                return role.type == role_type.edit
    return False
