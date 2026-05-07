"""
NyayaSetu — Chat Routes
"""
import logging
from flask import Blueprint, request, jsonify
from services.ai_service import AIService

logger   = Blueprint_logger = logging.getLogger("nyayasetu.chat")
chat_bp  = Blueprint("chat", __name__)
ai       = AIService()


@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON body"}), 400

        message = (data.get("message") or "").strip()
        history = data.get("history", [])

        if not message:
            return jsonify({"success": False, "error": "Message cannot be empty"}), 400

        if len(message) > 2000:
            return jsonify({"success": False, "error": "Message too long (max 2000 chars)"}), 400

        logger.info(f"Chat: {message[:60]}...")
        result = ai.chat(message, history)

        return jsonify({
            "success":  result["success"],
            "mode":     result.get("mode", "live"),
            "response": result["response"],
            "message":  message
        })

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            "success":  False,
            "error":    "Something went wrong. Please try again.",
            "response": None
        }), 500
