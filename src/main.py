import streamlit as st
import yaml
from pathlib import Path
from services.document_parser import DocumentParser
from services.job_scraper import JobScraper
from services.ai_analyzer import AIAnalyzer
from utils.config import config

# Set page config first
st.set_page_config(**config.ui['page_config'])

# Initialize services
document_parser = DocumentParser()
job_scraper = JobScraper()
ai_analyzer = AIAnalyzer()

# Main UI
st.title(config.ui['title'])
st.write(config.ui['description'])

# Sidebar for configuration
with st.sidebar:
    st.header(config.ui['sidebar']['config_header'])
    
    # Model Configuration
    st.subheader(config.ui['sidebar']['model_section'])
    selected_model = st.selectbox(
        "Select AI Model",
        options=[model['display_name'] for model in config.models.values()],
        index=0
    )
    
    # Get model key from display_name
    model_key = next(
        (key for key, model in config.models.items() if model['display_name'] == selected_model),
        None
    )
    
    # API Keys
    st.subheader(config.ui['sidebar']['api_section'])
    if 'gpt' in model_key:
        openai_key = st.text_input("OpenAI API Key", value="", type="password")
        google_key = ""
    else:
        google_key = st.text_input("Google API Key", value="", type="password")
        openai_key = ""
    
    # Model-specific settings
    if model_key:
        model_config = config.get_model_config(model_key)
        temperature = st.slider(
            "🌡️ Temperature",
            min_value=0.0,
            max_value=1.0,
            value=float(model_config['temperature']),
            step=0.1,
            help="Higher values make the output more creative"
        )
        
        if 'gpt' in model_key:
            max_tokens = st.number_input(
                "📝 Max Output Tokens",
                min_value=1,
                max_value=4096,
                value=int(model_config['max_tokens']),
                help="Maximum length of the response"
            )
        else:
            max_tokens = st.number_input(
                "📝 Max Output Tokens",
                min_value=1,
                max_value=4096,
                value=int(model_config['max_output_tokens']),
                help="Maximum length of the response"
            )
        
        # Update config
        if st.button(config.ui['sidebar']['update_button']):
            config_path = Path(__file__).parent.parent / 'config.yaml'
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
            
            if 'gpt' in model_key:
                yaml_config['models'][model_key]['temperature'] = temperature
                yaml_config['models'][model_key]['max_tokens'] = max_tokens
            else:
                yaml_config['models'][model_key]['temperature'] = temperature
                yaml_config['models'][model_key]['max_output_tokens'] = max_tokens
            
            with open(config_path, 'w') as f:
                yaml.dump(yaml_config, f, default_flow_style=False)
            
            st.success("✅ Settings updated successfully!")

# Main content area
st.header(config.ui['main']['url_section'])
job_url = st.text_input("Enter URL", placeholder="https://example.com/job-posting")

st.header(config.ui['main']['upload_section'])
uploaded_file = st.file_uploader("Choose file", type=["pdf", "docx"])

if st.button(config.ui['main']['analyze_button']) and uploaded_file and job_url:
    # Check if API keys are provided
    if ('gpt' in model_key and not openai_key) or ('gemini' in model_key and not google_key):
        st.error("🔐 Please provide the required API key in the sidebar.")
        st.stop()
        
    with st.spinner("🔄 Analyzing resume..."):
        # Extract resume text
        resume_text = document_parser.parse_resume(uploaded_file.read(), uploaded_file.type)
        if not resume_text:
            st.error("❌ Failed to extract text from the resume. Please ensure the file is not corrupted and contains text content.")
            st.stop()

        # Scrape job description
        job_desc_text = job_scraper.scrape_job_description(job_url)
        if not job_desc_text:
            st.error("❌ Failed to scrape job description")
            st.stop()

        # Pass the appropriate API key based on the model
        api_key = openai_key if 'gpt' in model_key else google_key
        
        # Analyze resume
        print(f"🤖 Analyzing resume with model: {model_key}")
        result = ai_analyzer.analyze_resume(resume_text, job_desc_text, model_key, api_key)  # Modified line

        if result and "markdown_response" in result:
            st.header(config.ui['main']['results']['score'])
            score_color = config.get_score_color(result["score"])
            colored_response = result["markdown_response"].replace(
                f"Score: {result['score']}/10",
                f"Score: <span style='color:{score_color}'>{result['score']}/10</span>"
            )
            
            # Replace question section headers with emojis
            colored_response = colored_response.replace(
                "### Easy Questions",
                f"### {config.ui['main']['results']['levels']['easy']}"
            ).replace(
                "### Intermediate Questions",
                f"### {config.ui['main']['results']['levels']['intermediate']}"
            ).replace(
                "### Difficult Questions",
                f"### {config.ui['main']['results']['levels']['difficult']}"
            ).replace(
                "### Extremely Difficult Questions",
                f"### {config.ui['main']['results']['levels']['extremely_difficult']}"
            )
            
            st.markdown(colored_response, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit • Powered by Scout Sense 🎯")
