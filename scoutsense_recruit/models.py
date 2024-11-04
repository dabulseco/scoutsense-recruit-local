from pydantic import BaseModel
from typing import List, Literal


class SkillProficiencyMatch(BaseModel):
    exceeds_requirements: List[str]
    meets_requirements: List[str]
    below_requirements: List[str]


class TechnicalSkills(BaseModel):
    required_skills_present: List[str]
    missing_critical_skills: List[str]
    skill_proficiency_match: SkillProficiencyMatch


class ExperienceMatch(BaseModel):
    years_required: str
    candidate_years: str
    experience_quality: Literal["Exceeds", "Meets", "Below"]
    relevant_projects: List[str]


class KeyResponsibilitiesMatch(BaseModel):
    can_perform: List[str]
    needs_development: List[str]
    gap_areas: List[str]


class Recommendation(BaseModel):
    decision: Literal["Strong Yes", "Yes", "Maybe", "No", "Strong No"]
    justification: str
    suggested_role_level: Literal["Junior", "Mid", "Senior", "Lead"]


class EvaluationSummary(BaseModel):
    strengths: List[str]
    concerns: List[str]
    candidate_speciality: Literal["Natural Language Processing", "Computer Vision"]
    overall_fit_score: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    recommendation: Recommendation


class RoleRequirementsMatch(BaseModel):
    technical_skills: TechnicalSkills
    experience_match: ExperienceMatch
    key_responsibilities_match: KeyResponsibilitiesMatch


class CandidateEvaluation(BaseModel):
    role_requirements_match: RoleRequirementsMatch
    evaluation_summary: EvaluationSummary
