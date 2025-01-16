import streamlit as st

# Set page config first
st.set_page_config(
    page_title="Resume Rater",
    page_icon="📝",
    layout="centered"
)

import openai
import google.generativeai as genai
from dotenv import load_dotenv
import os
import PyPDF2
import docx
import requests
from bs4 import BeautifulSoup
import io
import json

# Load environment variables
_ = load_dotenv(".env")

# Configure API clients
openai.api_key = os.getenv('OPENAI_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

# Debug logging for API key configuration
if not google_api_key:
    st.error("Google API key not found in environment variables")
else:
    st.success("Google API key loaded successfully")

genai.configure(api_key=google_api_key)

# Utility functions
def extract_text_from_pdf(file_bytes):
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

def extract_text_from_docx(file_bytes):
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

def scrape_job_description(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        st.error(f"Error scraping job description: {str(e)}")
        return None

def analyze_with_gemini(resume_text, job_description):
    try:
        if not os.getenv('GOOGLE_API_KEY'):
            st.error("Google API key is not set")
            return None
            
        # Configure the model with safety settings
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        prompt = f"""
        Analyze the following resume and job description to:
        1. Rate the candidate's fit for the role on a scale of 0-10
        2. Provide detailed feedback
        3. If the rating is 7 or higher, generate 20 interview questions (5 easy, 5 intermediate, 5 difficult, 5 extremely difficult)

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Provide the response in Markdown format as follows:

        # Resume Analysis

        ## Score: [0-10]/10

        ## Detailed Feedback
        [Your detailed feedback here with proper markdown formatting, using bullet points where appropriate]

        ## Interview Questions
        (Only if score is 7 or higher)

        ### Easy Questions
        1. [Question 1]
        2. [Question 2]
        3. [Question 3]
        4. [Question 4]
        5. [Question 5]

        ### Intermediate Questions
        1. [Question 1]
        2. [Question 2]
        3. [Question 3]
        4. [Question 4]
        5. [Question 5]

        ### Difficult Questions
        1. [Question 1]
        2. [Question 2]
        3. [Question 3]
        4. [Question 4]
        5. [Question 5]

        ### Extremely Difficult Questions
        1. [Question 1]
        2. [Question 2]
        3. [Question 3]
        4. [Question 4]
        5. [Question 5]

        Use proper markdown formatting with headers, bullet points, and numbered lists.
        """

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        response_text = response.text if hasattr(response, 'text') else response.parts[0].text
        
        # Extract score for color coding
        try:
            score_line = [line for line in response_text.split('\n') if 'Score:' in line][0]
            score = float(score_line.split('/')[0].split(':')[1].strip())
            return {"score": score, "markdown_response": response_text}
        except Exception as e:
            st.error(f"Error extracting score: {str(e)}")
            return None
    except Exception as e:
        st.error(f"Error analyzing with Gemini: {str(e)}")
        return None

def analyze_with_gpt4(resume_text, job_description):
    try:
        prompt = f"""
        Analyze the following resume and job description to:
        1. Rate the candidate's fit for the role on a scale of 0-10
        2. Provide detailed feedback
        3. If the rating is 7 or higher, generate 20 interview questions (5 easy, 5 intermediate, 5 difficult, 5 extremely difficult)

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Provide the response in Markdown format as follows:

        # Resume Analysis

        ## Score: [0-10]/10

        ## Detailed Feedback
        [Your detailed feedback here with proper markdown formatting, using bullet points where appropriate]

        ## Interview Questions
        (Only if score is 7 or higher)

        ### Easy Questions
        1. [Question 1]
        2. [Question 2]
        3. [Question 3]
        4. [Question 4]
        5. [Question 5]

        ### Intermediate Questions
        1. [Question 1]
        2. [Question 2]
        3. [Question 3]
        4. [Question 4]
        5. [Question 5]

        ### Difficult Questions
        1. [Question 1]
        2. [Question 2]
        3. [Question 3]
        4. [Question 4]
        5. [Question 5]

        ### Extremely Difficult Questions
        1. [Question 1]
        2. [Question 2]
        3. [Question 3]
        4. [Question 4]
        5. [Question 5]

        Use proper markdown formatting with headers, bullet points, and numbered lists.
        """

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert HR professional and technical interviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        response_text = response.choices[0].message.content
        
        # Extract score for color coding
        try:
            score_line = [line for line in response_text.split('\n') if 'Score:' in line][0]
            score = float(score_line.split('/')[0].split(':')[1].strip())
            return {"score": score, "markdown_response": response_text}
        except Exception as e:
            st.error(f"Error extracting score: {str(e)}")
            return None
    except Exception as e:
        st.error(f"Error analyzing with GPT-4: {str(e)}")
        return None

# Main UI
st.title("📝 Resume Rater")
st.write("Upload your resume and provide a job description URL to get an AI-powered analysis")

# Model selection
model_choice = st.selectbox(
    "Select AI Model",
    ["GPT-4o-mini", "Gemini-1.5-Pro"],
    index=0
)

# Job URL input
job_url = st.text_input("Job Description URL", placeholder="https://example.com/job-posting")

# File upload
uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

if st.button("Analyze Resume") and uploaded_file and job_url:
    with st.spinner("Analyzing resume..."):
        # Log file information
        st.info(f"Processing file: {uploaded_file.name} (Type: {uploaded_file.type}, Size: {uploaded_file.size/1024:.2f} KB)")
        
        # Extract resume text
        file_content = uploaded_file.read()
        if uploaded_file.type == "application/pdf":
            st.info("Detected PDF format, attempting to extract text...")
            resume_text = extract_text_from_pdf(file_content)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            st.info("Detected DOCX format, attempting to extract text...")
            resume_text = extract_text_from_docx(file_content)
        else:
            st.error(f"Unsupported file type: {uploaded_file.type}")
            resume_text = None

        if not resume_text:
            st.error("Failed to extract text from the resume. Please ensure the file is not corrupted and contains text content.")
            st.stop()

        # Scrape job description
        job_desc_text = scrape_job_description(job_url)
        if not job_desc_text:
            st.error("Failed to scrape job description")
            st.stop()

        # Analyze resume
        if model_choice == "GPT-4":
            result = analyze_with_gpt4(resume_text, job_desc_text)
        else:
            result = analyze_with_gemini(resume_text, job_desc_text)

        if result and "markdown_response" in result:
            score_color = "green" if result["score"] >= 7 else "orange" if result["score"] >= 5 else "red"
            colored_response = result["markdown_response"].replace(
                f"Score: {result['score']}/10",
                f"Score: <span style='color:{score_color}'>{result['score']}/10</span>"
            )
            st.markdown(colored_response, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
