# ResumeIQ Parser 📄

AI-powered resume parser with a **3-layer fallback engine**, smart export builder, and a beautiful Streamlit UI.

---

## Color Palette

| Name          | Hex       |
|---------------|-----------|
| Gochujang Red | `#780000` |
| Crimson Blaze | `#C1121F` |
| Varden        | `#FFF8E1` |
| Cosmos Blue   | `#003049` |
| Blue Marble   | `#669BBC` |

---

## How It Works — 3-Layer Parsing Engine

Every resume goes through this chain automatically. If a layer fails, it silently falls to the next one.

```
Resume File
    ↓
Text Extraction
    ├── .txt  → Plain decode
    ├── .pdf  → pdfplumber → fallback to PaddleOCR
    ├── .docx → python-docx
    └── .doc  → antiword → fallback python-docx
    ↓
Raw Text
    ↓
┌─────────────────────────────────┐
│  Layer 1 · Groq LLaMA 3.3 70B  │  ← primary (built-in key)
└──────────────┬──────────────────┘
               │ fails?
┌──────────────▼──────────────────┐
│  Layer 2 · Gemini 1.5 Flash     │  ← add key to unlock
└──────────────┬──────────────────┘
               │ fails?
┌──────────────▼──────────────────┐
│  Layer 3 · Regex (offline)      │  ← always works, no API needed
└─────────────────────────────────┘
    ↓
Structured JSON
    {name, email, phone, skills, experience, education, certifications}
    ↓
Export Builder
    → pick fields → rename keys → download filtered JSON
```

---

## Supported Formats

| Format | Method | Notes |
|--------|--------|-------|
| PDF (text) | pdfplumber | Fast, accurate |
| PDF (scanned) | PaddleOCR | ~1GB model download on first use |
| DOCX | python-docx | Tables included |
| DOC (legacy) | antiword | Install antiword on Windows |
| TXT | Plain decode | UTF-8 / Latin-1 |

---

## Quick Start

```bash
# 1. Enter the project folder
cd ResumeParserFinal

# 2. Install dependencies (if not done already)
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

App opens at **http://localhost:8501**

---

## API Key Setup

Open `parser/groq_parser.py` and paste your keys:

```python
GROQ_API_KEY   = "gsk_your_groq_key_here"    # required — get free at console.groq.com
GEMINI_API_KEY = ""                            # optional — get free at aistudio.google.com
```

### Get a free Groq key (Layer 1)
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up → **API Keys** → Create new key
3. Free tier: 14,400 requests/day

### Get a free Gemini key (Layer 2 — optional)
1. Visit [aistudio.google.com](https://aistudio.google.com)
2. Sign in → **Get API key**
3. Free tier: 1,500 requests/day

> **No keys at all?** Layer 3 (Regex) kicks in automatically — no setup needed. Results will be less complete but always functional.

---

## Export Builder

After parsing, the **Export Builder** panel lets you:

- ✅ **Preview** every extracted field and its value
- ✅ **Select** only the fields you want (checkboxes, pre-ticked for non-empty fields)
- ✅ **Rename** any field key before export (e.g. `phone` → `mobile_number`)
- ✅ **Download Filtered JSON** — only your selected + renamed fields
- ✅ **Download Full JSON** — everything, as-is

---

## Project Structure

```
ResumeParserFinal/
├── app.py                  # Streamlit UI + Export Builder
├── parser/
│   ├── extractor.py        # Text extraction (PDF, DOCX, TXT, OCR)
│   ├── groq_parser.py      # 3-layer parsing engine (Groq → Gemini → Regex)
│   └── __init__.py
├── requirements.txt
├── setup.sh                # One-click setup (Git Bash)
└── README.md
```

---

## Requirements

```
streamlit>=1.32.0
python-dotenv
groq>=0.5.0
pdfplumber>=0.10.0
python-docx>=1.1.0
paddleocr>=2.7.0
paddlepaddle>=2.6.0
PyMuPDF>=1.23.0
Pillow>=10.0.0
numpy>=1.24.0
google-generativeai  # optional, for Gemini Layer 2
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## Notes

- **PaddleOCR** downloads ~1GB of models on first scanned-PDF use — subsequent runs are instant
- **`.doc` files on Windows** require [antiword](http://www.winfield.demon.nl/) added to PATH; DOCX, PDF, and TXT work without it
- The sidebar shows live status (✅/❌) of all three API layers
- A **yellow warning banner** appears in the UI when Layer 3 (Regex) fires, so you always know which engine was used

---

*Built with Groq · Gemini · PaddleOCR · Streamlit*
