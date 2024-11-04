import streamlit as st
import tempfile
import os

from scoutsense_recruit import CANDIDATE_EVALUATOR_PROMPT_TEMPLATE
from utilities import extract_text, process_with_llm
from utilities import GEMINI_1_5_PRO, GEMINI_1_5_PRO_0827, GPT_4_O, GPT_4_O_MINI, GROQ_LLAMA_3_1_70B, GROQ_LLAMA_3_1_70B_VERSATILE, GROQ_MIXTRAL_8_7B

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary location and return path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def main():
    st.set_page_config(page_title="📝 ScoutSense Recruit 💼", page_icon="📄")
    
    st.title("📝 ScoutSense Recruit 💼")
    
    # Sidebar inputs
    with st.sidebar:
        st.header("Inputs")
        
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=['pdf'])
        job_url = st.text_input("Job Posting URL")
        
        model = st.selectbox(
            "Select Model",
            [GEMINI_1_5_PRO, GEMINI_1_5_PRO_0827, GPT_4_O, GPT_4_O_MINI, GROQ_LLAMA_3_1_70B, GROQ_LLAMA_3_1_70B_VERSATILE, GROQ_MIXTRAL_8_7B]
        )
        
        process = st.button("Evaluate Resume")
    
    # Main content area
    if process:
        if not uploaded_file:
            st.error("Please upload a resume")
        elif not job_url:
            st.error("Please enter a job posting URL")
        else:
            try:
                with st.spinner("Processing..."):
                    # Save and process the uploaded file
                    temp_file_path = save_uploaded_file(uploaded_file)
                    
                    # Extract text from resume and job posting
                    job_requirements = extract_text(source=job_url)
                    candidate_resume = extract_text(source=temp_file_path)
                    
                    # Clean up temp file
                    os.unlink(temp_file_path)
                    
                    # Process with LLM
                    results = process_with_llm(
                        model=model,
                        prompt_template=CANDIDATE_EVALUATOR_PROMPT_TEMPLATE,
                        input_dict={
                            "candidate_resume": candidate_resume,
                            "job_requirements": job_requirements,
                        },
                    )
                    
                    # Display results
                    st.header("Results")
                    st.write(results)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()