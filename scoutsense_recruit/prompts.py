import os, sys
from os.path import dirname as up

sys.path.append(os.path.abspath(os.path.join(up(__file__), os.pardir)))


CANDIDATE_EVALUATOR_PROMPT = """You are an experienced Technical Hiring Manager with deep expertise in evaluating technical talent. Based on the provided job requirements and candidate's resume, assess the candidate's suitability for the role.

Context:
Job Requirements:
{job_requirements}

Candidate Resume:
{candidate_resume}

Note: Provide objective assessment based solely on the provided information. Focus on technical capabilities, relevant experience, and role-specific requirements and return them in a structured format."""
