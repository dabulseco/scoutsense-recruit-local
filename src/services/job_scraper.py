import requests
from bs4 import BeautifulSoup
import streamlit as st
from utils.config import config

class JobScraper:
    @staticmethod
    def scrape_job_description(url: str) -> str:
        """Scrape job description from given URL."""
        try:
            scraping_config = config.scraping
            headers = {
                'User-Agent': scraping_config['user_agent']
            }
            response = requests.get(
                url, 
                headers=headers, 
                timeout=scraping_config.get('timeout', 30)
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract and clean text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            if not text.strip():
                st.error("No text content found in the job description URL")
                return None
                
            st.success("Successfully scraped job description")
            return text
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error accessing URL: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Error scraping job description: {str(e)}")
            return None
