"""Route for retrieving tags of a dataset"""
from flask import (
    abort,
    jsonify,
    current_app
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from dtool_lookup_server import UnknownURIError
from dtool_lookup_server.blueprint import Blueprint
from dtool_lookup_server.schemas import TagSchema
import dtool_lookup_server.utils_auth
from dtool_lookup_server.utils import (
    url_suffix_to_uri,
    get_tags_from_uri_by_user
)

bp = Blueprint("tags", __name__, url_prefix="/tags")

@bp.route("/<path:uri>", methods=["GET"])
@bp.response(200, TagSchema)
@bp.alt_response(1, description=2)
@bp.alt_response(403, description="No permissions")
@bp.alt_response(404, description="Not found")
@jwt_required()
def manifest(uri):
    """Request the dataset manifest."""
    username = get_jwt_identity()
    if not dtool_lookup_server.utils_auth.user_exists(username):
        # Unregistered users should see 401.
        abort(401)

    uri = url_suffix_to_uri(uri)
    if not dtool_lookup_server.utils_auth.may_access(username, uri):
        # Authorization errors should return 400.
        abort(403)

    try:
        tags = get_tags_from_uri_by_user(username, uri)
    except UnknownURIError:
        current_app.logger.info("UnknownURIError")
        abort(404)

    return {"tags": tags}

