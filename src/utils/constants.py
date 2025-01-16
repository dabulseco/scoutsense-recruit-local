import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model Names
GPT4_MODEL = "gpt-4o"
GEMINI_MODEL = "gemini-1.5-pro"

# File Types
PDF_MIME_TYPE = "application/pdf"
DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

# Score Thresholds
HIGH_SCORE_THRESHOLD = 7
MEDIUM_SCORE_THRESHOLD = 5

# Score Colors
HIGH_SCORE_COLOR = "green"
MEDIUM_SCORE_COLOR = "orange"
LOW_SCORE_COLOR = "red"

# User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
