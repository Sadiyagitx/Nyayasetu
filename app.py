"""
NyayaSetu — AI Legal Assistant
Production-grade Flask application
"""

import os
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from config.settings import Config
from routes.api import api_bp
from routes.chat import chat_bp

# ── LOGGING SETUP ─────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("nyayasetu")

# ── APP FACTORY ───────────────────────────────
def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")
    app.config.from_object(Config)
    CORS(app)

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(chat_bp)

    # Serve frontend
    @app.route("/")
    def index():
        return send_from_directory("frontend", "index.html")

    # Health check
    @app.route("/health")
    def health():
        from flask import jsonify
        from services.ai_service import AIService
        ai = AIService()
        return jsonify({
            "status": "healthy",
            "service": "NyayaSetu API",
            "version": "2.0.0",
            "ai_mode": "live" if ai.api_available() else "demo",
            "endpoints": ["/chat", "/api/check", "/health"]
        })

    # Global 404
    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    # Global 500
    @app.errorhandler(500)
    def server_error(e):
        from flask import jsonify
        logger.error(f"Server error: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

    logger.info("NyayaSetu application started successfully")
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting NyayaSetu on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
