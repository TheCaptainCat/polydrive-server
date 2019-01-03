from flask import request
from flask_login import login_required, current_user

from polydrive import app
from polydrive.config import db
from polydrive.models import Resource, User, Role, role_type
from polydrive.services.messages import ok, created, conflict
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
@login_required
@resource_middleware
@user_middleware
def share_resource(res_id, user_id):
    """
    Share a resource with a user.

    :param res_id: resource's id
    :param user_id: user's id
    :return: created link
    """
    content = request.get_json()
    if content is None:
        content = {}
    r_type = content.get('type', role_type.view)
    res = Resource.query.get(res_id)
    user = User.query.get(user_id)
    role = Role.query.filter_by(res_id=res.id, user_id=user.id).first()
    if role is not None:
        return conflict('Resource already shared with user.')
    role = Role.link(res, user, r_type)
    db.session.commit()
    return created('Resource shared.', role.deep)
