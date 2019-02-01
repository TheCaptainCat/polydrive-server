def check_resource_rights(res, user):
    if res is not None:
        return res.owner_id == user.id
    return False
