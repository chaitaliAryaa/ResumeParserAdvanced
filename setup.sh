#!/bin/bash

# ============================================================
#  ResumeIQ Parser - Setup & Run Script
#  Run this in Git Bash: bash setup.sh
# ============================================================

RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
GRAY='\033[0;90m'
NC='\033[0m'

echo ""
echo -e "${RED}╔══════════════════════════════════════════╗${NC}"
echo -e "${RED}║       ResumeIQ Parser · Setup Script     ║${NC}"
echo -e "${RED}║   3-Layer AI · Groq → Gemini → Regex     ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── [1/6] Check Python ───────────────────────────────────────────
echo -e "${CYAN}[1/6] Checking Python...${NC}"
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python not found. Install Python 3.9+ from python.org${NC}"
    exit 1
fi

PYTHON=python
if ! command -v python &> /dev/null; then PYTHON=python3; fi

VERSION=$($PYTHON --version 2>&1)
echo -e "${GREEN}✓ Found: $VERSION${NC}"

# ── [2/6] Create virtual environment ─────────────────────────────
echo ""
echo -e "${CYAN}[2/6] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}→ Already exists, skipping${NC}"
fi

# ── [3/6] Activate venv ──────────────────────────────────────────
echo ""
echo -e "${CYAN}[3/6] Activating virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo -e "${GREEN}✓ Activated${NC}"

# ── [4/6] Install core dependencies ──────────────────────────────
echo ""
echo -e "${CYAN}[4/6] Installing core dependencies...${NC}"
pip install --upgrade pip -q

pip install \
    streamlit \
    python-dotenv \
    groq \
    pdfplumber \
    python-docx \
    PyMuPDF \
    Pillow \
    numpy -q

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Core install failed. Check errors above.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Core packages installed${NC}"
fi

# ── [5/6] Optional: Gemini + PaddleOCR ───────────────────────────
echo ""
echo -e "${CYAN}[5/6] Installing optional packages...${NC}"

echo -e "${GRAY}  → google-generativeai (Gemini Layer 2)${NC}"
pip install google-generativeai -q
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Gemini support ready${NC}"
else
    echo -e "${YELLOW}  ⚠ Gemini install failed — Layer 2 will be skipped${NC}"
fi

echo -e "${GRAY}  → paddleocr + paddlepaddle (scanned PDF OCR)${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    pip install paddlepaddle -f https://www.paddlepaddle.org.cn/whl/windows/cpu/stable.html -q
else
    pip install paddlepaddle -q
fi
pip install paddleocr -q

if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ PaddleOCR ready (scanned PDF support)${NC}"
else
    echo -e "${YELLOW}  ⚠ PaddleOCR install failed — scanned PDFs will not work${NC}"
    echo -e "${YELLOW}    Text PDFs, DOCX, and TXT still work fine.${NC}"
fi

# ── API Key reminder ──────────────────────────────────────────────
echo ""
echo -e "${YELLOW}╔══════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║          ⚠  API Key Required             ║${NC}"
echo -e "${YELLOW}╠══════════════════════════════════════════╣${NC}"
echo -e "${YELLOW}║  Open parser/groq_parser.py and set:    ║${NC}"
echo -e "${YELLOW}║                                          ║${NC}"
echo -e "${YELLOW}║  GROQ_API_KEY = \"gsk_your_key_here\"      ║${NC}"
echo -e "${YELLOW}║                                          ║${NC}"
echo -e "${YELLOW}║  Free key → console.groq.com            ║${NC}"
echo -e "${YELLOW}║  (Gemini key optional → aistudio.google) ║${NC}"
echo -e "${YELLOW}╚══════════════════════════════════════════╝${NC}"

# ── [6/6] Launch ─────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[6/6] Launching ResumeIQ Parser...${NC}"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  App running at: http://localhost:8501   ║${NC}"
echo -e "${BLUE}║  Press Ctrl+C to stop                    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

streamlit run app.py --server.port 8501 --server.headless false
