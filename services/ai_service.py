"""
NyayaSetu — AI Service
Handles Gemini API with retry, exponential backoff, and demo fallback
"""

import os
import time
import json
import logging
import google.generativeai as genai
from config.settings import Config
from services.fallback import FallbackService

logger = logging.getLogger("nyayasetu.ai")


class AIService:
    def __init__(self):
        self.api_key   = Config.GEMINI_API_KEY
        self.model_name = Config.PRIMARY_MODEL
        self.fallback  = FallbackService()
        self._model    = None
        self._init_model()

    def _init_model(self):
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini model initialised: {self.model_name}")
            except Exception as e:
                logger.warning(f"Model init failed: {e}")
                self._model = None
        else:
            logger.warning("No GEMINI_API_KEY — running in DEMO mode")

    def api_available(self) -> bool:
        return self._model is not None and bool(self.api_key)

    # ── CORE GENERATE WITH RETRY ──────────────
    def _generate(self, prompt: str) -> str:
        if not self.api_available():
            raise RuntimeError("API not available")

        last_error = None
        for attempt in range(Config.MAX_RETRIES):
            try:
                logger.info(f"AI request attempt {attempt + 1}/{Config.MAX_RETRIES}")
                response = self._model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=1500,
                    )
                )
                result = response.text.strip()
                logger.info("AI response received successfully")
                return result

            except Exception as e:
                last_error = e
                err_str = str(e).lower()

                # 429 quota error → exponential backoff
                if "429" in str(e) or "quota" in err_str or "rate" in err_str:
                    wait = Config.RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limit hit. Waiting {wait}s before retry...")
                    time.sleep(wait)

                # Auth error → no point retrying
                elif "403" in str(e) or "401" in str(e) or "api key" in err_str:
                    logger.error("Authentication error — invalid API key")
                    raise RuntimeError("Invalid API key") from e

                # Other errors → short wait and retry
                else:
                    logger.warning(f"AI error (attempt {attempt+1}): {e}")
                    time.sleep(1)

        logger.error(f"All {Config.MAX_RETRIES} attempts failed: {last_error}")
        raise RuntimeError(f"AI service unavailable after {Config.MAX_RETRIES} retries")

    # ── CLEAN JSON FROM RESPONSE ──────────────
    def _clean_json(self, raw: str) -> dict:
        if "```" in raw:
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

    # ══════════════════════════════════════════
    # PUBLIC METHODS
    # ══════════════════════════════════════════

    def chat(self, message: str, history: list = None) -> dict:
        """
        Main chat endpoint for legal queries.
        Falls back to demo mode if API fails.
        """
        logger.info(f"Chat request: {message[:80]}...")

        prompt = self._build_chat_prompt(message, history or [])

        try:
            raw = self._generate(prompt)
            return {
                "success":  True,
                "mode":     "live",
                "response": self._parse_chat_response(raw),
                "raw":      raw
            }
        except Exception as e:
            logger.warning(f"Live AI failed, switching to demo mode: {e}")
            return {
                "success":  True,
                "mode":     "demo",
                "response": self.fallback.get_legal_response(message),
                "note":     "Running in demo mode"
            }

    def check_eligibility(self, profile: dict) -> dict:
        """
        Welfare scheme eligibility check.
        Falls back to demo mode if API fails.
        """
        logger.info(f"Eligibility check: {profile.get('occupation')} / {profile.get('state')}")

        prompt = self._build_eligibility_prompt(profile)

        try:
            raw  = self._generate(prompt)
            data = self._clean_json(raw)
            return {"success": True, "mode": "live", "data": data}
        except json.JSONDecodeError:
            logger.warning("JSON parse error — attempting raw response")
            return {"success": True, "mode": "live", "data": {"raw_response": raw if 'raw' in dir() else "Error"}}
        except Exception as e:
            logger.warning(f"Eligibility AI failed, demo mode: {e}")
            return {
                "success": True,
                "mode":    "demo",
                "data":    self.fallback.get_eligibility_response(profile)
            }

    def generate_letter(self, profile: dict, scheme: str) -> dict:
        """Generate application letter with fallback."""
        prompt = self._build_letter_prompt(profile, scheme)
        try:
            letter = self._generate(prompt)
            return {"success": True, "mode": "live", "letter": letter}
        except Exception as e:
            logger.warning(f"Letter generation failed: {e}")
            return {
                "success": True,
                "mode":    "demo",
                "letter":  self.fallback.get_letter(profile, scheme)
            }

    # ══════════════════════════════════════════
    # PROMPT BUILDERS
    # ══════════════════════════════════════════

    def _build_chat_prompt(self, message: str, history: list) -> str:
        history_text = ""
        if history:
            for h in history[-4:]:  # last 4 exchanges only
                history_text += f"User: {h.get('user', '')}\nAssistant: {h.get('assistant', '')}\n\n"

        return f"""
You are NyayaSetu, an expert AI legal assistant for Indian citizens.
You provide clear, accurate information about Indian laws, rights, and legal procedures.

IMPORTANT RULES:
- Always clarify you provide legal INFORMATION, not official legal ADVICE
- Be specific to Indian law (IPC, CrPC, Constitution, specific Acts)
- Use simple English — write for someone with no legal background
- Be empathetic and practical
- Always suggest next steps

CONVERSATION HISTORY:
{history_text}

USER QUESTION: {message}

Respond in this EXACT format:

**Legal Context**
[Brief explanation of the relevant law or right in 2-3 sentences]

**Your Rights**
[Bullet points of specific rights the person has in this situation]

**Suggested Action**
[Step-by-step what they should do — numbered list, very specific]

**Important Note**
[One sentence disclaimer + suggestion to consult a registered lawyer for official advice]
"""

    def _parse_chat_response(self, raw: str) -> dict:
        """Parse structured chat response into sections."""
        sections = {
            "legal_context":    "",
            "your_rights":      "",
            "suggested_action": "",
            "important_note":   "",
            "full_response":    raw
        }
        current = None
        lines   = raw.split("\n")
        buffer  = []

        mapping = {
            "legal context":    "legal_context",
            "your rights":      "your_rights",
            "suggested action": "suggested_action",
            "important note":   "important_note",
        }

        for line in lines:
            clean = line.strip().lower().replace("**", "").replace("*", "")
            matched = False
            for key, field in mapping.items():
                if key in clean:
                    if current and buffer:
                        sections[current] = "\n".join(buffer).strip()
                    current = field
                    buffer  = []
                    matched = True
                    break
            if not matched and current and line.strip():
                buffer.append(line.strip())

        if current and buffer:
            sections[current] = "\n".join(buffer).strip()

        return sections

    def _build_eligibility_prompt(self, p: dict) -> str:
        return f"""
You are NyayaSetu, an AI welfare rights navigator for Indian citizens.

CITIZEN PROFILE:
- Age: {p.get('age')}, Gender: {p.get('gender')}
- State: {p.get('state')}, Occupation: {p.get('occupation')}
- Monthly Income: {p.get('income')}, Category: {p.get('category')}

Identify exactly 3 real, active Indian government schemes this person qualifies for.
Use simple English. Prioritize highest financial impact schemes.

Return ONLY valid JSON — no markdown, no extra text:
{{
  "greeting": "Warm one sentence (max 12 words)",
  "missed_insight": "What they may have missed — emotional (max 18 words)",
  "schemes": [
    {{
      "name": "Official scheme name",
      "benefit": "Exact benefit with amounts (1 sentence)",
      "why_eligible": "Why this person qualifies (1 sentence)",
      "documents": ["Doc 1", "Doc 2", "Doc 3"],
      "steps": ["Step 1", "Step 2", "Step 3"],
      "apply_at": "Exact website or office"
    }}
  ],
  "urgent_action": "Most important thing to do this week (1 sentence)"
}}
"""

    def _build_letter_prompt(self, p: dict, scheme: str) -> str:
        return f"""
Write a formal application letter for an Indian citizen.
Applicant: Age {p.get('age')}, {p.get('gender')}, {p.get('occupation')},
Income {p.get('income')}, Category {p.get('category')}, State {p.get('state')}
Scheme: {scheme}
Format: Date, To authority, Subject line, 3 paragraphs, Yours faithfully [YOUR NAME].
Under 220 words. Respectful, simple English. Return only the letter text.
"""
