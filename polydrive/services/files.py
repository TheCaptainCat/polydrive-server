from polydrive.models import File, User


def check_file_rights(file, user):
    if user is None or not isinstance(user, User) or file is None or not isinstance(file, File):
        return False
    if file is not None:
        return file.owner_id == user.id
    return False
