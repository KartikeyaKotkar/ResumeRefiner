"""Utility functions for interacting with Google's Gemini API."""

import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types  # Added for structured config

load_dotenv()

# 1. Initialize the Client (Replaces genai.configure)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTION = (
    "You are an expert career coach and LaTeX specialist. Your task is to analyze resumes, "
    "improve their content for ATS optimization, and format them into professional LaTeX code. "
    "You always respond in valid JSON format."
)


def wrap_latex_content(content: str) -> str:
    """Wrap the raw LaTeX body in a complete document structure."""
    return (
        "\\documentclass[11pt,a4paper]{article}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage{lmodern}\n"
        "\\usepackage[margin=1in]{geometry}\n"
        "\\usepackage{hyperref}\n"
        "\\usepackage{enumitem}\n"
        "\\usepackage{titlesec}\n"
        "\\usepackage{fontawesome}\n\n"
        "% Custom formatting\n"
        "\\titleformat{\\section}{\\Large\\bfseries}{}{0em}{}\n"
        "\\titlespacing*{\\section}{0pt}{12pt}{6pt}\n"
        "\\titleformat{\\subsection}{\\large\\bfseries}{}{0em}{}\n"
        "\\titlespacing*{\\subsection}{0pt}{8pt}{4pt}\n\n"
        "\\begin{document}\n\n"
        f"{content}\n\n"
        "\\end{document}"
    )


async def enhance_resume_with_gemini(resume_text: str, target_role: str = None) -> dict:
    """
    Performs content improvement, LaTeX formatting, and suggestion generation.
    """
    role_context = f"specifically for a {target_role} role" if target_role else ""

    prompt = f"""
    Analyze the following resume {role_context}:
    ---
    {resume_text}
    ---

    Tasks:
    1. Improve the content (action verbs, metrics, professional tone).
    2. Format the improved content as LaTeX (only provide the body commands like \\section, \\item, etc.).
    3. Provide an ATS-friendly plain text version.
    4. Provide structured data for DOCX generation.
    5. List 3-5 specific improvements made.

    Return the result as a JSON object with exactly these keys:
    {{
        "latex_body": "string",
        "plain_text": "string",
        "structured_data": {{
            "name": "string",
            "contact_info": "string",
            "summary": "string",
            "experience": [
                {{
                    "company": "string",
                    "role": "string",
                    "duration": "string",
                    "location": "string",
                    "points": ["string"]
                }}
            ],
            "education": [
                {{
                    "institution": "string",
                    "degree": "string",
                    "year": "string"
                }}
            ],
            "skills": ["string"]
        }},
        "suggestions": ["string"]
    }}
    """

    try:
        response = client.models.generate(
            model="gemini-1.5-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
            ),
        )

        # 3. Parse JSON
        data = json.loads(response.text)

        return {
            "latex": wrap_latex_content(data.get("latex_body", "")),
            "plain_text": data.get("plain_text", ""),
            "structured_data": data.get("structured_data", {}),
            "suggestions": data.get("suggestions", ["Improved professional language"]),
        }

    except Exception as e:
        print(f"Gemini Error: {e}")
        raise Exception(f"Error enhancing resume: {str(e)}")
