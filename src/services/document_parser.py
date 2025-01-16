import PyPDF2
import docx
import io
import streamlit as st
from utils.config import config

class DocumentParser:
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extract text from PDF file bytes."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            if not text.strip():
                st.error("PDF appears to be empty or contains no extractable text")
                return None
            st.success("Successfully extracted text from PDF")
            return text
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            st.error("Debug info: File size: {:.2f} KB".format(len(file_bytes)/1024))
            return None

    @staticmethod
    def extract_text_from_docx(file_bytes: bytes) -> str:
        """Extract text from DOCX file bytes."""
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            if not text.strip():
                st.error("DOCX appears to be empty or contains no extractable text")
                return None
            st.success("Successfully extracted text from DOCX")
            return text
        except Exception as e:
            st.error(f"Error processing DOCX: {str(e)}")
            st.error("Debug info: File size: {:.2f} KB".format(len(file_bytes)/1024))
            return None

    @classmethod
    def parse_resume(cls, file_content: bytes, file_type: str) -> str:
        """Parse resume file based on its type."""
        file_types = config.file_types
        
        if file_type == file_types['mime_types']['pdf']:
            st.info("Detected PDF format, attempting to extract text...")
            return cls.extract_text_from_pdf(file_content)
        elif file_type == file_types['mime_types']['docx']:
            st.info("Detected DOCX format, attempting to extract text...")
            return cls.extract_text_from_docx(file_content)
        else:
            allowed_types = ', '.join(file_types['allowed'])
            st.error(f"Unsupported file type: {file_type}. Allowed types: {allowed_types}")
            return None
