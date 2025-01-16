from openai import OpenAI
import google.generativeai as genai
import streamlit as st
from typing import Optional, Dict, Any
from utils.config import config
import httpx
import http.client

class AIAnalyzer:
    def __init__(self):
        """Initialize the analyzer without any API keys."""
        self.openai_client = None
        http.client.HTTPConnection.debuglevel = 0

    def _initialize_openai_client(self, api_key: str):
        """Initialize OpenAI client with API key."""
        try:
            # Create transport with proxy settings if they exist
            proxy_settings = config.get_proxy_settings() if hasattr(config, 'get_proxy_settings') else None
            client_params = {'timeout': 60.0}
            
            if proxy_settings:
                transport = httpx.HTTPTransport(proxy=proxy_settings)
                client_params['transport'] = transport
            
            http_client = httpx.Client(**client_params)
            self.openai_client = OpenAI(api_key=api_key, http_client=http_client)
            return True
            
        except Exception as e:
            st.error(f"Error initializing OpenAI client: {str(e)}")
            return False


    def _get_analysis_prompt(self, resume_text: str, job_description: str) -> str:
        """Generate the analysis prompt for AI models."""
        return f"""
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

    def analyze_with_gemini(self, resume_text: str, job_description: str, model_key: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Analyze resume using Gemini models."""
        try:
            genai.configure(api_key=api_key)  # Use the provided API key
                
            # Get model configuration
            model_config = config.get_model_config(model_key)
            if not model_config:
                st.error(f"Configuration not found for model: {model_key}")
                return None
            
            # Extract valid generation config parameters
            generation_config = {
                'temperature': model_config['temperature'],
                'top_p': model_config.get('top_p', 1),
                'top_k': model_config.get('top_k', 1),
                'max_output_tokens': model_config.get('max_output_tokens', 2048),
            }
            
            model = genai.GenerativeModel(
                model_name=model_config['model_id'],
                generation_config=generation_config,
                safety_settings=model_config.get('safety_settings', [])
            )

            prompt = self._get_analysis_prompt(resume_text, job_description)
            response = model.generate_content(prompt)
            
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

    def analyze_with_gpt(self, resume_text: str, job_description: str, model_key: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Analyze resume using GPT models."""
        try:
            if not self.openai_client or self.openai_client.api_key != api_key:
                if not self._initialize_openai_client(api_key):
                    return None
            
            if not self.openai_client:
                st.error("Failed to initialize OpenAI client")
                return None

            # Get model configuration
            model_config = config.get_model_config(model_key)
            if not model_config:
                st.error(f"Configuration not found for model: {model_key}")
                return None

            prompt = self._get_analysis_prompt(resume_text, job_description)
            response = self.openai_client.chat.completions.create(
                model=model_config['model_id'],
                messages=[
                    {"role": "system", "content": model_config['system_role']},
                    {"role": "user", "content": prompt}
                ],
                temperature=model_config['temperature'],
                max_tokens=model_config['max_tokens']
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
            st.error(f"Error analyzing with GPT: {str(e)}")
            return None

    def analyze_resume(self, resume_text: str, job_description: str, model_key: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Analyze resume using the selected AI model."""
        model_config = config.get_model_config(model_key)
        if not model_config:
            st.error(f"Configuration not found for model: {model_key}")
            return None

        if 'gpt' in model_key:
            return self.analyze_with_gpt(resume_text, job_description, model_key, api_key)
        else:
            return self.analyze_with_gemini(resume_text, job_description, model_key, api_key)