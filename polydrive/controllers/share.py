from flask import request
from flask_login import login_required, current_user

from polydrive import app
from polydrive.config import db
from polydrive.models import Resource, User, Role, role_type
from polydrive.services import resource_action
from polydrive.services.messages import ok, created, conflict, bad_request
from polydrive.services.middleware import resource_middleware, user_middleware


@app.route('/res/shared', methods=['GET'])
@login_required
def shared_get():
    """
    Get all resources shared with the user.

    :return: the list of shared files, with complete hierarchy
    """
    return ok('OK', [r.resource.deep for r in current_user.roles])


@app.route('/res/share/<int:res_id>/<int:user_id>', methods=['POST'])
@app.route('/res/share/<int:res_id>/<int:user_id>/<r_type>', methods=['POST'])
@login_required
@resource_middleware(action=resource_action.write)
@user_middleware
def share_resource(res_id, user_id, r_type=role_type.view):
    """
    Share a resource with a user.

    :param res_id: resource's id
    :param user_id: user's id
    :param r_type: type of sharing (edit or view)
    :return: created link
    """
    if r_type not in role_type.values():
        return bad_request('Invalid sharing type')
    res = Resource.query.get(res_id)
    user = User.query.get(user_id)
    role = Role.link(res, user, r_type)
    if role is None:
        return conflict('Resource already shared with user.')
    db.session.commit()
    return created('Resource shared.', role.deep)
