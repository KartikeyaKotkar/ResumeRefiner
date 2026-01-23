"""Utility functions for interacting with Google's Gemini API."""

import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"), http_options={"api_version": "v1beta"}
)

SYSTEM_INSTRUCTION = (
    "You are an expert career coach and LaTeX specialist. Your task is to analyze resumes, "
    "improve their content for ATS optimization, and format them into professional LaTeX code. "
    "You always respond in valid JSON format."
)


def wrap_latex_content(content: str) -> str:
    return (
        "\\documentclass[10pt,a4paper]{article}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage[margin=0.75in]{geometry}\n"
        "\\usepackage{titlesec}\n"
        "\\usepackage{enumitem}\n"
        "\\usepackage{xcolor}\n\n"
        "\\definecolor{primary}{RGB}{0, 0, 0}\n"
        "\\titleformat{\\section}{\\large\\bfseries\\uppercase}{}{0em}{}[\\titlerule]\n"
        "\\titlespacing*{\\section}{0pt}{10pt}{5pt}\n"
        "\\setlist[itemize]{noitemsep, topsep=0pt, leftmargin=1.5em}\n\n"
        "\\begin{document}\n"
        f"{content}\n"
        "\\end{document}"
    )


async def enhance_resume_with_gemini(resume_text: str, target_role: str = None) -> dict:
    role_context = f"specifically for a {target_role} role" if target_role else ""

    prompt = f"""Analyze the following resume {role_context}:
---
{resume_text}
---

Return a JSON object with exactly these keys:
{{
    "latex_body": "string (LaTeX body content without document preamble)",
    "plain_text": "string (enhanced plain text version)",
    "structured_data": {{
        "name": "string", "contact_info": "string", "summary": "string",
        "experience": [{{ "company": "string", "role": "string", "duration": "string", "location": "string", "points": ["string"] }}],
        "education": [{{ "institution": "string", "degree": "string", "year": "string" }}],
        "skills": ["string"]
    }},
    "suggestions": ["string (improvement suggestions)"]
}}"""

    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
            ),
        )

        data = json.loads(response.text)

        return {
            "latex": wrap_latex_content(data.get("latex_body", "")),
            "plain_text": data.get("plain_text", ""),
            "structured_data": data.get("structured_data", {}),
            "suggestions": data.get("suggestions", ["Improved professional language"]),
        }

    except Exception as e:
        print(f"Gemini Error: {e}")
        if "404" in str(e):
            raise Exception(
                "Model 1.5-pro not found. Try changing model to 'gemini-3-flash'."
            )
        raise Exception(f"Final Fix Error: {str(e)}")
