import streamlit as st
import tempfile
import os

from scoutsense_recruit import CANDIDATE_EVALUATOR_PROMPT
from utilities import extract_text, process_with_llm
from utilities import (
    GPT_4_O,
    GPT_4_O_MINI,
)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary location and return path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name


def main():
    st.set_page_config(page_title="📝 ScoutSense Recruit 💼", page_icon="📄")

    st.title("📝 ScoutSense Recruit 💼")

    # Sidebar inputs
    with st.sidebar:
        st.header("Inputs")

        # Resume input section
        st.subheader("Resume Input")
        resume_input_type = st.radio(
            "Choose Resume Input Method",
            ["Upload PDF", "URL"],
            key="resume_input"
        )

        if resume_input_type == "Upload PDF":
            resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
            resume_url = None
        else:
            resume_file = None
            resume_url = st.text_input("Resume URL")

        # Job posting input section
        st.subheader("Job Posting Input")
        job_input_type = st.radio(
            "Choose Job Posting Input Method",
            ["Upload PDF", "URL"],
            key="job_input"
        )

        if job_input_type == "Upload PDF":
            job_file = st.file_uploader("Upload Job Posting (PDF)", type=["pdf"])
            job_url = None
        else:
            job_file = None
            job_url = st.text_input("Job Posting URL")

        model = st.selectbox("Select Model", [GPT_4_O, GPT_4_O_MINI])

        process = st.button("Evaluate Resume")

    # Main content area
    if process:
        try:
            with st.spinner("Processing..."):
                # Process Resume
                if resume_file:
                    temp_resume_path = save_uploaded_file(resume_file)
                    candidate_resume = extract_text(source=temp_resume_path)
                    os.unlink(temp_resume_path)
                elif resume_url:
                    candidate_resume = extract_text(source=resume_url)
                else:
                    st.error("Please provide a resume (either upload PDF or URL)")
                    return

                # Process Job Posting
                if job_file:
                    temp_job_path = save_uploaded_file(job_file)
                    job_requirements = extract_text(source=temp_job_path)
                    os.unlink(temp_job_path)
                elif job_url:
                    job_requirements = extract_text(source=job_url)
                else:
                    st.error("Please provide job posting details (either upload PDF or URL)")
                    return

                # Process with LLM
                results = process_with_llm(
                    model=model,
                    prompt=CANDIDATE_EVALUATOR_PROMPT,
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