"""
NyayaSetu — API Routes
"""
import logging
from flask import Blueprint, request, jsonify
from services.ai_service import AIService

logger = logging.getLogger("nyayasetu.api")
api_bp = Blueprint("api", __name__)
ai     = AIService()

REQUIRED_FIELDS = ["age", "gender", "state", "occupation", "income", "category"]


@api_bp.route("/api/check", methods=["POST"])
def check_eligibility():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400

        missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
        if missing:
            return jsonify({
                "success": False,
                "error":   f"Missing fields: {', '.join(missing)}"
            }), 400

        try:
            age = int(data["age"])
            if not (1 <= age <= 110):
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid age"}), 400

        logger.info(f"Eligibility check: {data.get('occupation')} / {data.get('state')}")
        result = ai.check_eligibility(data)

        return jsonify({
            "success": result["success"],
            "mode":    result.get("mode", "live"),
            "data":    result.get("data", {})
        })

    except Exception as e:
        logger.error(f"Eligibility endpoint error: {e}")
        return jsonify({"success": False, "error": "Server error. Please try again."}), 500


@api_bp.route("/api/letter", methods=["POST"])
def generate_letter():
    try:
        data    = request.get_json(force=True, silent=True)
        profile = data.get("profile") if data else None
        scheme  = (data.get("scheme") or "").strip() if data else ""

        if not profile or not scheme:
            return jsonify({"success": False, "error": "Missing profile or scheme"}), 400

        result = ai.generate_letter(profile, scheme)
        return jsonify({
            "success": result["success"],
            "mode":    result.get("mode", "live"),
            "letter":  result.get("letter", "")
        })

    except Exception as e:
        logger.error(f"Letter endpoint error: {e}")
        return jsonify({"success": False, "error": "Could not generate letter."}), 500
