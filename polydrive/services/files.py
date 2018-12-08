

def check_file_rights(file, user):
    if file is not None:
        return file.owner_id == user.id
    return False
