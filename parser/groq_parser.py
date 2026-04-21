"""
groq_parser.py
3-layer fallback resume parser:
  Layer 1 → Groq LLaMA 3.3 70B   (built-in key)
  Layer 2 → Gemini 1.5 Flash      (add key to unlock)
  Layer 3 → Regex                  (offline, always works)
"""

import json
import re

# ── API Keys ──────────────────────────────────────────────────────
GROQ_API_KEY   = "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"   # ← paste your Groq key here
GEMINI_API_KEY = "AIzaSyArxyibYuc54M3XDbC-z8IaVamQP0AaSlQ"                          # ← optional: paste Gemini key to enable
# ─────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert resume parser. Extract information from the provided resume text and return ONLY a valid JSON object with no markdown, no preamble, and no explanation.

Return exactly this structure:
{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "+1 234 567 8900",
  "location": "City, Country",
  "summary": "Professional summary in 2-3 sentences",
  "skills": ["Skill1", "Skill2"],
  "experience": [
    {
      "company": "Company Name",
      "role": "Job Title",
      "duration": "Jan 2020 - Dec 2022",
      "description": "Key responsibilities and achievements"
    }
  ],
  "education": [
    {
      "institution": "University Name",
      "degree": "Bachelor of Science in Computer Science",
      "year": "2019"
    }
  ],
  "certifications": ["Cert 1", "Cert 2"]
}

Rules:
- Use empty string "" for missing text fields
- Use empty array [] for missing list fields
- Never return null
- Return ONLY the JSON object, nothing else
"""


def _clean_json(raw: str) -> dict | None:
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


# ── Layer 1: Groq ─────────────────────────────────────────────────
def _parse_with_groq(raw_text: str) -> dict | None:
    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        print("[Groq] No key set, skipping.")
        return None
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Parse this resume:\n\n{raw_text[:12000]}"}
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        return _clean_json(response.choices[0].message.content)
    except Exception as e:
        print(f"[Groq] Failed: {e}")
        return None


# ── Layer 2: Gemini ───────────────────────────────────────────────
def _parse_with_gemini(raw_text: str) -> dict | None:
    if not GEMINI_API_KEY:
        print("[Gemini] No key set, skipping.")
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"{SYSTEM_PROMPT}\n\nParse this resume:\n\n{raw_text[:12000]}"
        response = model.generate_content(prompt)
        return _clean_json(response.text)
    except Exception as e:
        print(f"[Gemini] Failed: {e}")
        return None


# ── Layer 3: Regex (offline) ──────────────────────────────────────
def _parse_with_regex(raw_text: str) -> dict:
    email_m = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", raw_text)
    email   = email_m.group(0) if email_m else ""

    phone_m = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", raw_text)
    phone   = phone_m.group(0).strip() if phone_m else ""

    name = ""
    for line in raw_text.splitlines():
        line = line.strip()
        if (line and 2 < len(line) < 60
                and not re.search(r"[@:/\\]", line)
                and not re.match(r"[\d\s\-+(]+$", line)):
            name = line
            break

    skill_keywords = [
        "python","java","javascript","react","node","sql","html","css",
        "c++","c#","typescript","aws","azure","docker","kubernetes","git",
        "linux","excel","power bi","tableau","machine learning","deep learning",
        "tensorflow","pytorch","django","flask","fastapi","mongodb",
        "postgresql","mysql","figma","android","ios","swift","kotlin",
        "flutter","rust","go","scala","r","matlab","spark","hadoop",
        "selenium","junit","spring","hibernate","redis","graphql"
    ]
    found_skills = []
    text_lower = raw_text.lower()
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.title())

    edu_pattern = re.compile(
        r"(bachelor|master|b\.?sc|m\.?sc|b\.?e|m\.?e|phd|diploma|degree|"
        r"university|college|institute|school)", re.IGNORECASE
    )
    education = []
    for line in raw_text.splitlines():
        if edu_pattern.search(line) and len(line.strip()) > 5:
            education.append({"institution": line.strip(), "degree": "", "year": ""})
        if len(education) >= 4:
            break

    exp_pattern = re.compile(
        r"(engineer|developer|manager|analyst|designer|intern|lead|"
        r"consultant|architect|director|officer|executive|specialist)", re.IGNORECASE
    )
    experience = []
    for line in raw_text.splitlines():
        if exp_pattern.search(line) and len(line.strip()) > 5:
            experience.append({"company":"","role":line.strip(),"duration":"","description":""})
        if len(experience) >= 5:
            break

    loc_m = re.search(
        r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2,}|[A-Z][a-z]+)\b", raw_text
    )
    location = loc_m.group(0) if loc_m else ""

    return {
        "name": name, "email": email, "phone": phone, "location": location,
        "summary": "", "skills": found_skills, "experience": experience,
        "education": education, "certifications": []
    }


# ── Public Entry Point ────────────────────────────────────────────
def parse_resume_with_groq(raw_text: str, api_key: str = None) -> tuple:
    """
    Try Groq → Gemini → Regex in order.
    Returns (parsed_dict, method_label).
    """
    result = _parse_with_groq(raw_text)
    if result:
        return result, "Groq LLaMA 3.3 70B ✅"

    result = _parse_with_gemini(raw_text)
    if result:
        return result, "Gemini 1.5 Flash ✅"

    result = _parse_with_regex(raw_text)
    return result, "Regex Fallback ⚡ (offline)"
