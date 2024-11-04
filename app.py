import os, sys
from os.path import dirname as up

sys.path.append(os.path.abspath(os.path.join(up(__file__), os.pardir)))

from langchain_core.pydantic_v1 import BaseModel, Field
import typing_extensions as typing
from typing import List, Dict, Literal

from utilities import extract_text

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

import typing_extensions as typing

    
_ = load_dotenv()

class Recipe(typing.TypedDict):
    recipe_name: str
    ingredients: list[str]

class SkillProficiencyMatch(typing.TypedDict):
    exceeds_requirements: List[str] = Field(
        default_factory=list, description="Skills where candidate exceeds requirements"
    )
    meets_requirements: List[str] = Field(
        default_factory=list, description="Skills where candidate meets requirements"
    )
    below_requirements: List[str] = Field(
        default_factory=list, description="Skills where candidate is below requirements"
    )


class TechnicalSkills(typing.TypedDict):
    required_skills_present: List[str] = Field(
        default_factory=list, description="Required skills found in candidate's profile"
    )
    missing_critical_skills: List[str] = Field(
        default_factory=list,
        description="Required skills missing from candidate's profile",
    )
    skill_proficiency_match: SkillProficiencyMatch


class ExperienceMatch(typing.TypedDict):
    years_required: str = Field(
        ..., description="Years of experience required for the role"
    )
    candidate_years: str = Field(
        ..., description="Years of relevant experience the candidate has"
    )
    experience_quality: Literal["Exceeds", "Meets", "Below"] = Field(
        ..., description="Quality of candidate's experience relative to requirements"
    )
    relevant_projects: List[str] = Field(
        default_factory=list,
        description="Relevant projects from candidate's experience",
    )


class KeyResponsibilitiesMatch(typing.TypedDict):
    can_perform: List[str] = Field(
        default_factory=list,
        description="Responsibilities candidate can perform based on experience",
    )
    needs_development: List[str] = Field(
        default_factory=list, description="Areas where candidate needs development"
    )
    gap_areas: List[str] = Field(
        default_factory=list, description="Critical gaps in candidate's capabilities"
    )


class Recommendation(typing.TypedDict):
    decision: Literal["Strong Yes", "Yes", "Maybe", "No", "Strong No"] = Field(
        ..., description="Final hiring recommendation"
    )
    justification: str = Field(..., description="Explanation for the recommendation")
    interview_recommendations: List[str] = Field(
        default_factory=list,
        description="Suggested areas to focus on during interviews",
    )
    suggested_role_level: Literal["Junior", "Mid", "Senior", "Lead"] = Field(
        ..., description="Recommended level for the candidate"
    )


class EvaluationSummary(typing.TypedDict):
    strengths: List[str] = Field(
        default_factory=list, description="Candidate's key strengths"
    )
    concerns: List[str] = Field(default_factory=list, description="Areas of concern")
    overall_fit_score: int = Field(
        ..., ge=1, le=10, description="Overall fit score on a scale of 1-10"
    )
    recommendation: Recommendation


class CandidateEvaluation(typing.TypedDict):
    """Complete evaluation of a candidate's fit for a technical role"""

    role_requirements_match: Dict[str, typing.TypedDict] = Field(
        ...,
        description={
            "technical_skills": TechnicalSkills,
            "experience_match": ExperienceMatch,
            "key_responsibilities_match": KeyResponsibilitiesMatch,
        },
    )
    evaluation_summary: EvaluationSummary


PROMPT_TEMPLATE = """You are an experienced Technical Hiring Manager with deep expertise in evaluating technical talent. 
Based on the provided job requirements and candidate's resume, assess the candidate's suitability for the role.

Job Requirements:
{job_requirements}

Candidate Resume:
{candidate_resume}

Provide an objective assessment based solely on the provided information. Focus on technical capabilities, 
relevant experience, and role-specific requirements.
"""
import google.generativeai as genai
import typing_extensions as typing

# model = ChatOpenAI(model="gpt-4o", temperature=0)
job_requirements = extract_text(source="https://www.linkedin.com/jobs/view/3891667565")
candidate_resume = extract_text(source="data/raw/isham_rashik_resume.pdf")

model = genai.GenerativeModel("gemini-1.5-pro-latest")
result = model.generate_content(
    PROMPT_TEMPLATE.format(job_requirements=job_requirements, candidate_resume=candidate_resume),
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json", response_schema=list[CandidateEvaluation]
    ),
)
print(result)