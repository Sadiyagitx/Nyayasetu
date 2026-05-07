"""
NyayaSetu — Fallback Service
Intelligent pre-built responses when Gemini API is unavailable.
Ensures demo never crashes.
"""

import logging
import random

logger = logging.getLogger("nyayasetu.fallback")


class FallbackService:

    # ── LEGAL TOPIC DETECTION ─────────────────
    TOPICS = {
        "wage":        ["wage", "salary", "payment", "paid", "employer", "labour", "work"],
        "land":        ["land", "property", "zameen", "plot", "eviction", "house"],
        "domestic":    ["domestic", "violence", "abuse", "husband", "wife", "dowry"],
        "consumer":    ["consumer", "product", "refund", "defective", "cheated", "fraud"],
        "police":      ["fir", "police", "arrest", "complaint", "station", "custody"],
        "rti":         ["rti", "information", "government", "document", "transparency"],
        "employment":  ["fired", "dismissed", "terminated", "job", "employment"],
        "accident":    ["accident", "injury", "hospital", "compensation", "motor"],
        "rent":        ["rent", "landlord", "tenant", "evict", "deposit"],
        "general":     []
    }

    RESPONSES = {
        "wage": {
            "legal_context": "Under the Payment of Wages Act, 1936, every employer must pay wages on time. Withholding or delaying wages is a punishable offence under Indian labour law. The Minimum Wages Act also guarantees state-specific minimum pay.",
            "your_rights": "• Right to receive wages by the 7th of each month (establishments with <1000 workers)\n• Right to written wage slip every month\n• Right to equal pay for equal work\n• Protection against illegal deductions\n• Right to file complaint without fear of retaliation",
            "suggested_action": "1. Send written complaint to your employer via registered post (keep a copy)\n2. File complaint at District Labour Commissioner office — free and accessible\n3. Call Labour Helpline: 1800-11-4444 (toll-free)\n4. Gather evidence: salary slips, bank statements, offer letter\n5. If no response in 30 days → approach Labour Court",
            "important_note": "This is general legal information. For your specific case, consult a registered lawyer or your nearest District Legal Services Authority (DLSA) — they provide FREE legal aid."
        },
        "land": {
            "legal_context": "Land rights in India are governed by state-specific land laws and the Transfer of Property Act, 1882. The Right to Fair Compensation Act, 2013 protects landowners from arbitrary acquisition. Illegal eviction without court order is punishable.",
            "your_rights": "• Right to fair compensation if land is acquired\n• Right to challenge illegal eviction in court\n• Right to see land records (7/12 extract, Khasra-Khatoni)\n• Right to mutation of land records after inheritance\n• Women have equal inheritance rights under Hindu Succession Act",
            "suggested_action": "1. Collect all land documents: sale deed, 7/12 extract, mutation records\n2. Visit Tehsil/Taluka office to check official land records\n3. File complaint at Tahsildar if illegal possession\n4. Approach Revenue Court for land disputes\n5. Contact District Legal Services Authority for free legal help",
            "important_note": "Land disputes are complex and state-specific. Please consult a lawyer or your nearest DLSA office for personalised advice."
        },
        "domestic": {
            "legal_context": "The Protection of Women from Domestic Violence Act, 2005 provides comprehensive protection. IPC Section 498A covers cruelty by husband or relatives. The Dowry Prohibition Act, 1961 makes dowry demands illegal.",
            "your_rights": "• Right to protection order from Magistrate\n• Right to residence in shared household\n• Right to monetary relief and compensation\n• Right to free legal aid\n• Right to file FIR at any police station\n• Right to shelter home admission",
            "suggested_action": "1. Call Women Helpline: 181 (24/7, free) — IMMEDIATE help\n2. Call Police: 112 for emergency\n3. Contact Protection Officer in your district (appointed under DV Act)\n4. Visit nearest One Stop Centre (Sakhi Centre) — free shelter, legal, medical help\n5. File complaint at police station or directly approach Magistrate",
            "important_note": "Your safety is the priority. If you are in immediate danger, call 112 now. All legal aid is FREE for women under these laws."
        },
        "consumer": {
            "legal_context": "The Consumer Protection Act, 2019 gives strong rights to buyers. You can file complaint online at edaakhil.nic.in. Cases up to ₹50 lakh go to District Consumer Commission — filing fee is minimal.",
            "your_rights": "• Right to file complaint within 2 years of issue\n• Right to replacement, refund, or compensation\n• Right to compensation for physical/mental harassment\n• E-commerce platforms are also liable\n• Right to free legal aid if income is low",
            "suggested_action": "1. Send legal notice to seller/company via registered post\n2. File complaint online: edaakhil.nic.in (simple process)\n3. Keep all evidence: bills, screenshots, emails, delivery photos\n4. For urgent matters → approach District Consumer Commission directly\n5. National Consumer Helpline: 1800-11-4000",
            "important_note": "Consumer cases are relatively simple to file yourself. The Consumer Commission is designed to be accessible without a lawyer."
        },
        "police": {
            "legal_context": "Under CrPC Section 154, police MUST register an FIR for cognizable offences — they cannot refuse. If police refuse, you can approach Superintendent of Police or file complaint directly with Magistrate under Section 156(3).",
            "your_rights": "• Right to have FIR registered — police cannot refuse for cognizable offence\n• Right to free copy of FIR\n• Right to know grounds of arrest\n• Right to legal counsel immediately upon arrest\n• Right to inform family member of arrest\n• Right to medical examination if alleging assault",
            "suggested_action": "1. Go to police station and demand FIR in writing\n2. If refused — send complaint to Superintendent of Police by registered post\n3. File complaint with District Magistrate under Section 156(3) CrPC\n4. Approach State Human Rights Commission if police misconduct\n5. Call Police Complaint Helpline: 1090",
            "important_note": "Document everything — dates, officer names, badge numbers. Legal aid is available FREE through District Legal Services Authority."
        },
        "rti": {
            "legal_context": "The Right to Information Act, 2005 gives every citizen the right to request information from any government body. The Public Information Officer must respond within 30 days. Filing an RTI costs only ₹10.",
            "your_rights": "• Right to receive information within 30 days\n• Right to appeal if refused (First Appeal: 30 days, Second: Information Commission)\n• Below Poverty Line citizens are exempt from fees\n• Right to inspect government documents\n• Right to receive certified copies",
            "suggested_action": "1. Write RTI application to the Public Information Officer of the department\n2. Pay ₹10 fee (IPO/DD/cash) — BPL applicants are exempt\n3. File online at rtionline.gov.in for central government\n4. If no response in 30 days → file First Appeal with Appellate Authority\n5. Second Appeal → Central/State Information Commission",
            "important_note": "RTI is one of the most powerful tools for citizens. Use it to get information about any government scheme, your case status, or official documents."
        },
        "employment": {
            "legal_context": "The Industrial Disputes Act, 1947 protects workers from illegal dismissal. Retrenchment without proper notice and compensation is illegal. Workers in establishments with 100+ employees need government permission for retrenchment.",
            "your_rights": "• Right to written reason for termination\n• Right to notice period or pay in lieu\n• Right to gratuity after 5 years of service\n• Right to provident fund withdrawal\n• Right to challenge wrongful termination at Labour Court",
            "suggested_action": "1. Request written termination letter with reasons\n2. File complaint at Labour Commissioner within 3 years\n3. Apply for PF withdrawal at EPF portal: epfindia.gov.in\n4. Claim gratuity from employer in writing\n5. Approach Labour Court if amount > ₹1 lakh",
            "important_note": "Keep all employment documents: offer letter, appointment letter, salary slips, PF details. These are critical evidence."
        },
        "general": {
            "legal_context": "India has a comprehensive legal system with constitutional rights guaranteed to every citizen. The Legal Services Authorities Act, 1987 ensures free legal aid for those who cannot afford it. Every district has a DLSA providing free services.",
            "your_rights": "• Right to free legal aid if income is below ₹1 lakh/year\n• Right to approach any court in India\n• Right to fair and speedy trial\n• Right to legal representation\n• Constitutional right to equality before law (Article 14)",
            "suggested_action": "1. Identify which type of legal issue you have (civil, criminal, consumer, labour)\n2. Contact District Legal Services Authority — 100% free legal help\n3. Lok Adalat: for quick settlement of disputes out of court\n4. National Legal Helpline: 15100\n5. Visit nalsa.gov.in for all legal aid information",
            "important_note": "Please describe your specific situation for more targeted legal guidance. All information provided is general in nature."
        }
    }

    def _detect_topic(self, message: str) -> str:
        msg_lower = message.lower()
        for topic, keywords in self.TOPICS.items():
            if any(kw in msg_lower for kw in keywords):
                return topic
        return "general"

    def get_legal_response(self, message: str) -> dict:
        topic = self._detect_topic(message)
        r = self.RESPONSES.get(topic, self.RESPONSES["general"])
        logger.info(f"Fallback response for topic: {topic}")
        return {
            "legal_context":    r["legal_context"],
            "your_rights":      r["your_rights"],
            "suggested_action": r["suggested_action"],
            "important_note":   r["important_note"],
            "full_response":    f"**Legal Context**\n{r['legal_context']}\n\n**Your Rights**\n{r['your_rights']}\n\n**Suggested Action**\n{r['suggested_action']}\n\n**Important Note**\n{r['important_note']}"
        }

    def get_eligibility_response(self, profile: dict) -> dict:
        occ    = profile.get("occupation", "").lower()
        income = profile.get("income", "")
        state  = profile.get("state", "India")

        schemes = []

        # Ayushman Bharat — universal for low income
        if "below" in income or "10k" in income:
            schemes.append({
                "name": "Ayushman Bharat PM-JAY",
                "benefit": "Free health coverage up to ₹5 lakh per year for hospitalisation",
                "why_eligible": "Your income level qualifies you for this national health scheme",
                "documents": ["Aadhaar Card", "Ration Card", "Income Certificate"],
                "steps": [
                    "Visit pmjay.gov.in and check eligibility with your Aadhaar",
                    "Download Ayushman card from nearest CSC centre or hospital",
                    "Use card at any empanelled government or private hospital"
                ],
                "apply_at": "pmjay.gov.in or nearest Common Service Centre"
            })

        # MGNREGA for labourers
        if "labour" in occ or "farm" in occ or "worker" in occ:
            schemes.append({
                "name": "MGNREGA (Mahatma Gandhi National Rural Employment Guarantee)",
                "benefit": "Guaranteed 100 days of paid work per year at state-notified wages (₹200-350/day)",
                "why_eligible": "Your occupation as a rural worker makes you eligible for guaranteed employment",
                "documents": ["Aadhaar Card", "Bank Account Details", "Residence Proof"],
                "steps": [
                    "Register at your Gram Panchayat office with Aadhaar",
                    "Get Job Card issued (within 15 days)",
                    "Request work from Gram Rozgar Sahayak — work must start within 15 days"
                ],
                "apply_at": "Nearest Gram Panchayat office"
            })

        # PM Kisan for farmers
        if "farm" in occ:
            schemes.append({
                "name": "PM Kisan Samman Nidhi",
                "benefit": "₹6,000 per year (₹2,000 every 4 months) directly to bank account",
                "why_eligible": "As a farmer, you are entitled to this direct income support scheme",
                "documents": ["Aadhaar Card", "Land Records (Khasra/7-12)", "Bank Account Details"],
                "steps": [
                    "Visit pmkisan.gov.in and click 'New Farmer Registration'",
                    "Enter Aadhaar number and fill details",
                    "Get verified by local Patwari/Revenue officer"
                ],
                "apply_at": "pmkisan.gov.in or nearest CSC centre"
            })

        # PM Awas for low income
        if "below" in income or "10k" in income:
            schemes.append({
                "name": "PM Awas Yojana (Gramin)",
                "benefit": "₹1.2 lakh (plains) or ₹1.3 lakh (hilly areas) for house construction",
                "why_eligible": "Your income level qualifies you for housing assistance",
                "documents": ["Aadhaar Card", "BPL Certificate", "Bank Account", "Land Documents"],
                "steps": [
                    "Contact Gram Panchayat to check if your name is in Awaas+ list",
                    "If not listed, apply through local Block Development Office",
                    "Submit required documents and get approval"
                ],
                "apply_at": "Gram Panchayat or Block Development Office"
            })

        # Default if nothing matched
        if not schemes:
            schemes = [
                {
                    "name": "Ayushman Bharat PM-JAY",
                    "benefit": "Free health coverage up to ₹5 lakh per year",
                    "why_eligible": "Available for most Indian families based on socio-economic criteria",
                    "documents": ["Aadhaar Card", "Ration Card"],
                    "steps": ["Check eligibility at pmjay.gov.in", "Visit nearest empanelled hospital"],
                    "apply_at": "pmjay.gov.in"
                }
            ]

        return {
            "greeting": f"We found important schemes for you in {state}.",
            "missed_insight": "Many eligible citizens never claim these benefits — don't be one of them.",
            "schemes": schemes[:3],
            "urgent_action": "Visit your nearest Common Service Centre (CSC) this week with your Aadhaar card to start the process."
        }

    def get_letter(self, profile: dict, scheme: str) -> str:
        return f"""[DATE]

To,
The Concerned Authority,
Department of Social Welfare / Relevant Ministry,
Government of {profile.get('state', 'India')}

Subject: Application for {scheme}

Respected Sir/Madam,

I, the undersigned, am writing to formally apply for the {scheme}. I am a {profile.get('age')}-year-old {profile.get('gender', 'citizen')} residing in {profile.get('state')}, working as a {profile.get('occupation')} with a monthly income of approximately {profile.get('income')}.

I belong to the {profile.get('category', 'General')} category and meet all the eligibility criteria as prescribed for this scheme. I am committed to providing all required documents and completing any verification process as required by your department.

I humbly request you to kindly consider my application and process my enrollment at the earliest. I shall be grateful for your kind assistance.

Yours faithfully,

[YOUR FULL NAME]
[YOUR COMPLETE ADDRESS]
[YOUR CONTACT NUMBER]
[YOUR AADHAAR NUMBER]

Enclosures:
1. Aadhaar Card (copy)
2. Income Certificate
3. Relevant supporting documents
"""
