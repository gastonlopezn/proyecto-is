from flask import Blueprint, Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

api_questions_bp = Blueprint(
    "api_questions",
    __name__,
    url_prefix="/api/questions",
)


def _is_api_request() -> bool:
    return request.path == "/api" or request.path.startswith("/api/")


def register_api_error_handlers(app: Flask) -> None:
    """Registra manejadores de errores JSON para rutas bajo /api/*."""

    @app.errorhandler(400)
    def handle_bad_request(error: HTTPException):
        if _is_api_request():
            return jsonify({"error": error.description or "Bad request."}), 400
        return error

    @app.errorhandler(404)
    def handle_not_found(error: HTTPException):
        if _is_api_request():
            return jsonify({"error": error.description or "Resource not found."}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error: HTTPException):
        if _is_api_request():
            return jsonify({"error": error.description or "Method not allowed."}), 405
        return error


# --- Read endpoints (#89, #90) ---


# --- Create endpoint (#91) ---


# --- Update and Delete endpoints (#92, #93) ---
