import streamlit as st
import os
import json
from dotenv import load_dotenv
load_dotenv()

from parser.extractor import extract_text
from parser.groq_parser import parse_resume_with_groq, GROQ_API_KEY, GEMINI_API_KEY

# ── Page Config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ Parser",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --gochujang: #780000;
    --crimson:   #C1121F;
    --varden:    #FFF8E1;
    --cosmos:    #003049;
    --marble:    #669BBC;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--varden);
    color: var(--cosmos);
}
#MainMenu, footer, header { visibility: hidden; }
.stApp { background-color: var(--varden); }

[data-testid="stSidebar"] {
    background-color: var(--cosmos) !important;
    border-right: 4px solid var(--crimson);
}
[data-testid="stSidebar"] * { color: var(--varden) !important; }

.hero-header {
    background: linear-gradient(135deg, var(--gochujang) 0%, var(--crimson) 60%, var(--cosmos) 100%);
    padding: 40px 48px;
    border-radius: 16px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 400px; height: 400px;
    border-radius: 50%;
    background: rgba(102,155,188,0.15);
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 42px; font-weight: 700;
    color: var(--varden); margin: 0; line-height: 1.1;
}
.hero-sub {
    font-size: 16px; color: var(--marble);
    margin-top: 8px; font-weight: 300; letter-spacing: 0.5px;
}

.section-card {
    background: white;
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 20px;
    border-left: 5px solid var(--crimson);
    box-shadow: 0 2px 12px rgba(0,48,73,0.08);
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 18px; font-weight: 600;
    color: var(--gochujang);
    text-transform: uppercase; letter-spacing: 1.5px;
    margin-bottom: 14px;
    border-bottom: 1px solid rgba(102,155,188,0.3);
    padding-bottom: 10px;
}
.info-item {
    display: flex; align-items: center; gap: 10px;
    margin: 8px 0; font-size: 15px; color: var(--cosmos);
}
.info-label {
    font-weight: 600; color: var(--crimson);
    min-width: 80px; font-size: 13px;
    text-transform: uppercase; letter-spacing: 0.5px;
}
.skill-badge {
    display: inline-block;
    background: var(--cosmos); color: var(--varden);
    padding: 4px 14px; border-radius: 20px;
    font-size: 13px; margin: 4px; font-weight: 500;
}
.exp-block {
    border-left: 3px solid var(--marble);
    padding-left: 16px; margin: 14px 0;
}
.exp-company { font-weight: 700; color: var(--cosmos); font-size: 15px; }
.exp-role    { color: var(--crimson); font-size: 14px; font-weight: 500; }
.exp-duration{ color: #888; font-size: 13px; margin-bottom: 6px; }
.exp-desc    { color: #444; font-size: 14px; line-height: 1.6; }
.edu-block   { margin: 10px 0; }
.edu-degree  { font-weight: 600; color: var(--cosmos); }
.edu-inst    { color: var(--marble); font-size: 14px; }

.export-card {
    background: white;
    border-radius: 12px;
    padding: 28px 32px;
    margin-top: 24px;
    border-left: 5px solid var(--cosmos);
    box-shadow: 0 2px 12px rgba(0,48,73,0.08);
}
.export-title {
    font-family: 'Playfair Display', serif;
    font-size: 20px; font-weight: 600;
    color: var(--cosmos);
    margin-bottom: 6px;
}
.export-subtitle {
    font-size: 13px; color: #888; margin-bottom: 20px;
}
.field-row {
    display: flex; align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid rgba(102,155,188,0.15);
}
.preview-val {
    font-size: 13px; color: #666;
    white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis; max-width: 300px;
}
.method-badge {
    display: inline-block;
    background: rgba(0,48,73,0.08);
    color: var(--cosmos);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 8px;
}
.fallback-warn {
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
    color: #856404;
    margin-bottom: 16px;
}

.stButton > button {
    background: linear-gradient(135deg, var(--crimson), var(--gochujang));
    color: var(--varden); border: none;
    padding: 12px 32px; border-radius: 8px;
    font-weight: 600; font-size: 15px;
    letter-spacing: 0.5px; cursor: pointer;
    transition: all 0.3s; width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, var(--gochujang), var(--cosmos));
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(120,0,0,0.3);
}
.stDownloadButton > button {
    background: var(--cosmos) !important;
    color: var(--varden) !important;
    border: none; border-radius: 8px;
    font-weight: 600; width: 100%;
}
[data-testid="stMetric"] {
    background: white; border-radius: 10px;
    padding: 16px; border-top: 3px solid var(--crimson);
    box-shadow: 0 2px 8px rgba(0,48,73,0.06);
}
[data-testid="stMetricValue"] {
    color: var(--gochujang) !important;
    font-family: 'Playfair Display', serif;
    font-size: 28px !important;
}
[data-testid="stMetricLabel"] {
    color: var(--cosmos) !important;
    font-weight: 500; font-size: 13px;
    text-transform: uppercase; letter-spacing: 0.5px;
}
[data-testid="stFileUploader"] {
    background: white; border-radius: 12px; padding: 10px;
}
.stTextArea textarea {
    background-color: white;
    border: 1px solid var(--marble);
    border-radius: 8px; font-size: 13px; color: var(--cosmos);
}
hr { border-color: rgba(102,155,188,0.3); }
</style>
""", unsafe_allow_html=True)


# ── Sidebar: API Status ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System Status")
    st.markdown("---")
    groq_ok   = bool(GROQ_API_KEY and GROQ_API_KEY != "YOUR_GROQ_API_KEY_HERE")
    gemini_ok = bool(GEMINI_API_KEY)
    st.markdown(f"{'✅' if groq_ok   else '❌'} **Groq** (Layer 1)")
    st.markdown(f"{'✅' if gemini_ok else '⚠️'} **Gemini** (Layer 2{'—add key to enable' if not gemini_ok else ''})")
    st.markdown("✅ **Regex** (Layer 3 — always on)")
    st.markdown("---")
    st.markdown("**Supported Formats**")
    st.markdown("📄 PDF · 📝 DOCX · 📃 DOC · 📋 TXT · 🖼️ Scanned PDF")
    st.markdown("---")
    st.markdown("<small style='color:#669BBC;'>ResumeIQ · 3-Layer AI Parser</small>", unsafe_allow_html=True)


# ── Hero ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <p class="hero-title">ResumeIQ Parser</p>
    <p class="hero-sub">3-layer AI extraction · Groq → Gemini → Regex · Multi-format · Smart Export</p>
</div>
""", unsafe_allow_html=True)


# ── Upload ───────────────────────────────────────────────────────
col_upload, col_info = st.columns([2, 1])
with col_upload:
    uploaded_file = st.file_uploader(
        "Drop your resume here",
        type=["pdf", "docx", "doc", "txt"],
        help="Supports PDF (text & scanned), DOCX, DOC, TXT"
    )
with col_info:
    if uploaded_file:
        size_kb = len(uploaded_file.getvalue()) / 1024
        st.metric("File", uploaded_file.name.split(".")[-1].upper())
        st.metric("Size", f"{size_kb:.1f} KB")


# ── Helper: field preview string ─────────────────────────────────
def _preview(value) -> str:
    if isinstance(value, list):
        if not value:
            return "—"
        if isinstance(value[0], dict):
            return f"{len(value)} entr{'y' if len(value)==1 else 'ies'}"
        joined = ", ".join(str(v) for v in value[:4])
        return joined + (f" +{len(value)-4} more" if len(value) > 4 else "")
    return str(value)[:80] if value else "—"


# ── Parse Button ─────────────────────────────────────────────────
FIELD_META = [
    ("name",           "Name",           "📛"),
    ("email",          "Email",          "📧"),
    ("phone",          "Phone",          "📞"),
    ("location",       "Location",       "📍"),
    ("summary",        "Summary",        "📝"),
    ("skills",         "Skills",         "🛠️"),
    ("experience",     "Experience",     "💼"),
    ("education",      "Education",      "🎓"),
    ("certifications", "Certifications", "🏅"),
]

if uploaded_file:
    if st.button("🚀 Parse Resume"):
        with st.spinner("Extracting text from document..."):
            raw_text, extract_method = extract_text(uploaded_file)

        if not raw_text.strip():
            st.error("Could not extract text. File may be corrupted or fully image-based without OCR support.")
        else:
            st.success(f"✅ Text extracted via **{extract_method}** — {len(raw_text):,} characters")

            with st.spinner("Parsing resume through AI layers..."):
                parsed, parse_method = parse_resume_with_groq(raw_text)

            st.session_state["parsed"]       = parsed
            st.session_state["raw_text"]     = raw_text
            st.session_state["parse_method"] = parse_method

# ── Results ───────────────────────────────────────────────────────
if "parsed" in st.session_state:
    parsed       = st.session_state["parsed"]
    parse_method = st.session_state["parse_method"]
    raw_text     = st.session_state["raw_text"]

    st.markdown("---")

    # Method badge
    is_fallback = "Regex" in parse_method
    method_color = "#856404" if is_fallback else "#003049"
    st.markdown(
        f"<span style='font-size:14px; font-weight:600; color:{method_color};'>"
        f"Parsed by: {parse_method}</span>",
        unsafe_allow_html=True
    )
    if is_fallback:
        st.markdown(
            "<div class='fallback-warn'>⚠️ Both AI APIs were unavailable — "
            "results are regex-extracted and may be less complete. "
            "Add your Groq key in <code>parser/groq_parser.py</code> for full accuracy.</div>",
            unsafe_allow_html=True
        )

    st.markdown("## 📊 Parsed Results")

    # Contact
    st.markdown(f"""
    <div class="section-card">
        <div class="section-title">👤 Contact Information</div>
        <div class="info-item"><span class="info-label">Name</span> {parsed.get('name','—')}</div>
        <div class="info-item"><span class="info-label">Email</span> {parsed.get('email','—')}</div>
        <div class="info-item"><span class="info-label">Phone</span> {parsed.get('phone','—')}</div>
        <div class="info-item"><span class="info-label">Location</span> {parsed.get('location','—')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Summary
    if parsed.get("summary"):
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">📝 Summary</div>
            <p style="line-height:1.7;color:#333;margin:0;">{parsed['summary']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Skills
    skills = parsed.get("skills", [])
    if skills:
        badges = "".join(f'<span class="skill-badge">{s}</span>' for s in skills)
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🛠️ Skills</div>
            <div>{badges}</div>
        </div>
        """, unsafe_allow_html=True)

    # Experience
    experience = parsed.get("experience", [])
    if experience:
        exp_html = ""
        for exp in experience:
            exp_html += f"""
            <div class="exp-block">
                <div class="exp-company">{exp.get('company','')}</div>
                <div class="exp-role">{exp.get('role','')}</div>
                <div class="exp-duration">🗓️ {exp.get('duration','')}</div>
                <div class="exp-desc">{exp.get('description','')}</div>
            </div>"""
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">💼 Work Experience</div>
            {exp_html}
        </div>
        """, unsafe_allow_html=True)

    # Education
    education = parsed.get("education", [])
    if education:
        edu_html = ""
        for edu in education:
            edu_html += f"""
            <div class="edu-block">
                <div class="edu-degree">{edu.get('degree','')}</div>
                <div class="edu-inst">🎓 {edu.get('institution','')} · {edu.get('year','')}</div>
            </div>"""
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🎓 Education</div>
            {edu_html}
        </div>
        """, unsafe_allow_html=True)

    # Certifications
    certs = parsed.get("certifications", [])
    if certs:
        cert_items = "".join(f"<li style='margin:6px 0'>{c}</li>" for c in certs)
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">🏅 Certifications</div>
            <ul style="margin:0;padding-left:20px;color:#333;">{cert_items}</ul>
        </div>
        """, unsafe_allow_html=True)

    # ── Export Builder ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Playfair Display',serif; font-size:24px;
                font-weight:700; color:#003049; margin-bottom:4px;">
        📋 Export Builder
    </div>
    <div style="font-size:14px; color:#888; margin-bottom:24px;">
        Choose which fields to include, preview their values, and optionally rename the keys before downloading.
    </div>
    """, unsafe_allow_html=True)

    # Column headers
    hc1, hc2, hc3, hc4 = st.columns([0.4, 1.5, 1.8, 2.8])
    hc1.markdown("<span style='font-size:12px;font-weight:700;color:#669BBC;text-transform:uppercase;letter-spacing:1px;'>Include</span>", unsafe_allow_html=True)
    hc2.markdown("<span style='font-size:12px;font-weight:700;color:#669BBC;text-transform:uppercase;letter-spacing:1px;'>Field</span>", unsafe_allow_html=True)
    hc3.markdown("<span style='font-size:12px;font-weight:700;color:#669BBC;text-transform:uppercase;letter-spacing:1px;'>Rename Key</span>", unsafe_allow_html=True)
    hc4.markdown("<span style='font-size:12px;font-weight:700;color:#669BBC;text-transform:uppercase;letter-spacing:1px;'>Preview</span>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:8px 0 16px 0;'>", unsafe_allow_html=True)

    selections = {}
    for field_key, field_label, field_icon in FIELD_META:
        value   = parsed.get(field_key)
        preview = _preview(value)
        nonempty = bool(value and value != [] and value != "")

        c1, c2, c3, c4 = st.columns([0.4, 1.5, 1.8, 2.8])
        selected  = c1.checkbox("", value=nonempty, key=f"sel_{field_key}")
        c2.markdown(
            f"<span style='font-size:15px;font-weight:600;color:#003049;'>"
            f"{field_icon} {field_label}</span>",
            unsafe_allow_html=True
        )
        new_name = c3.text_input(
            "rename", value=field_label, key=f"rename_{field_key}",
            label_visibility="collapsed"
        )
        c4.markdown(
            f"<span style='font-size:13px;color:#666;'>{preview}</span>",
            unsafe_allow_html=True
        )
        selections[field_key] = (selected, new_name.strip() or field_label)

    st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)

    # Build filtered JSON for download
    filtered_json = {}
    selected_count = 0
    for field_key, (selected, export_key) in selections.items():
        if selected:
            filtered_json[export_key] = parsed.get(field_key)
            selected_count += 1

    # Preview of what will be exported
    st.markdown(
        f"<span style='font-size:13px;color:#888;'>"
        f"Exporting <strong style='color:#003049;'>{selected_count}</strong> field(s)</span>",
        unsafe_allow_html=True
    )

    col_dl, col_raw = st.columns(2)
    with col_dl:
        st.download_button(
            label=f"⬇️ Download Filtered JSON ({selected_count} fields)",
            data=json.dumps(filtered_json, indent=2, ensure_ascii=False),
            file_name="resume_export.json",
            mime="application/json"
        )
    with col_raw:
        st.download_button(
            label="⬇️ Download Full JSON (all fields)",
            data=json.dumps(parsed, indent=2, ensure_ascii=False),
            file_name="resume_full.json",
            mime="application/json"
        )

    with st.expander("🔍 Preview Export JSON"):
        st.json(filtered_json)

    with st.expander("📄 View Raw Extracted Text"):
        st.text_area("Raw Text", raw_text, height=250)

else:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#aaa;">
        <div style="font-size:64px;margin-bottom:16px;">📂</div>
        <div style="font-size:18px;font-family:'Playfair Display',serif;color:#003049;">
            Upload a resume to get started
        </div>
        <div style="font-size:14px;margin-top:8px;color:#669BBC;">
            PDF · DOCX · DOC · TXT · Scanned Images via OCR
        </div>
    </div>
    """, unsafe_allow_html=True)
