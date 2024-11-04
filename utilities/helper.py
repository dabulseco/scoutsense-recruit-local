import os, sys
from os.path import dirname as up

sys.path.append(os.path.abspath(os.path.join(up(__file__), os.pardir)))

import re
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from typing import Dict

from langchain_community.document_loaders import WebBaseLoader

from urllib.parse import urlparse
from typing import Union, Tuple, List
import validators

from dotenv import load_dotenv

_ = load_dotenv()

from utilities.constants import (
    GEMINI_1_5_PRO,
    GEMINI_1_5_PRO_0827,
    GPT_4_O,
    GPT_4_O_MINI,
    GROQ_LLAMA_3_1_70B,
    GROQ_LLAMA_3_1_70B_VERSATILE,
    GROQ_MIXTRAL_8_7B,
)


def extract_pdf_text(file_path: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        file_path (str): Path to the PDF file

    Returns:
        str: Combined text content
    """
    loader = PDFPlumberLoader(file_path)
    document = " ".join([page.page_content for page in loader.load()])
    return document


def process_with_llm(model: str, prompt_template: PromptTemplate, input_dict: Dict):
    """
    Process input using specified LLM model.

    Args:
        model (str): Name of the LLM model to use
        prompt_template (PromptTemplate): Template for the prompt
        input_dict (Dict): Dictionary containing input parameters

    Returns:
        Dict: Model's output in JSON format
    """
    if model in [GEMINI_1_5_PRO, GEMINI_1_5_PRO_0827]:
        llm = ChatGoogleGenerativeAI(model=model)
    elif model in [GPT_4_O, GPT_4_O_MINI]:
        llm = ChatOpenAI(model=model)
    elif model in [
        GROQ_LLAMA_3_1_70B_VERSATILE,
        GROQ_LLAMA_3_1_70B,
        GROQ_MIXTRAL_8_7B,
    ]:
        llm = ChatGroq(model=model)

    chain = prompt_template | llm | JsonOutputParser()
    result = chain.invoke(input_dict)
    return result


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.

    Args:
        text (str): Raw text content to be cleaned

    Returns:
        str: Cleaned and normalized text
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]*?>", "", text)
    # Remove URLs
    text = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        text,
    )
    # Remove special characters
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    # Replace multiple spaces with a single space
    text = re.sub(r"\s{2,}", " ", text)
    # Trim leading and trailing whitespace
    text = text.strip()
    # Remove extra whitespace
    text = " ".join(text.split())
    return text


def extract_url_text(url: str) -> str:
    """
    Extract text content from a URL.

    Args:
        url (str): URL to extract content from

    Returns:
        str: Cleaned text content from URL
    """
    loader = WebBaseLoader([url])
    data = clean_text(loader.load().pop().page_content)
    return data


def detect_url(text: str) -> Tuple[bool, List[str]]:
    """
    Detect if text contains valid URLs and extract them.

    Args:
        text (str): Text that might contain URLs

    Returns:
        Tuple[bool, List[str]]: (True/False if valid URLs found, List of found URLs)
    """
    # Regular expression for URL detection
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

    # Find all potential URLs
    potential_urls = re.findall(url_pattern, text)

    # Validate each URL
    valid_urls = []
    for url in potential_urls:
        if validators.url(url):
            valid_urls.append(url)

    return bool(valid_urls), valid_urls


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url (str): String to check

    Returns:
        bool: True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def extract_source_type(source: str) -> Tuple[str, str]:
    """
    Determine if the source is a URL or file path and validate it.

    Args:
        source (str): Source string (URL or file path)

    Returns:
        Tuple[str, str]: ('url' or 'file', source string)

    Raises:
        ValueError: If source is invalid or empty
    """
    if not source:
        raise ValueError("Source cannot be empty")

    if is_valid_url(source):
        return "url", source
    else:
        # Assuming it's a file path if not a URL
        return "file", source


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract all valid URLs from a text string.

    Args:
        text (str): Text containing URLs

    Returns:
        List[str]: List of valid URLs found in text
    """
    _, urls = detect_url(text)
    return urls


# Modified version of your original extract_text function
def extract_text(source: str) -> str:
    """
    Extract text from either URL or file based on source type.

    Args:
        source (str): URL or file path

    Returns:
        str: Extracted text content

    Raises:
        ValueError: If source type is invalid or source is empty
    """
    source_type, source_path = extract_source_type(source)
    if source_type == "url":
        return extract_url_text(source_path)
    elif source_type == "file":
        # Assuming PDF for now, but could be extended for other file types
        if source_path.lower().endswith(".pdf") or source_path.lower().endswith(".txt"):
            return extract_pdf_text(source_path)
        else:
            raise ValueError(f"Unsupported file type: {source_path}")
    else:
        raise ValueError(f"Invalid source type: {source_type}")
