"""Utility functions for interacting with Google's Gemini API."""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use System Instructions to keep the model focused and consistent
SYSTEM_INSTRUCTION = (
    "You are an expert career coach and LaTeX specialist. Your task is to analyze resumes, "
    "improve their content for ATS optimization, and format them into professional LaTeX code. "
    "You always respond in valid JSON format."
)

def get_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=SYSTEM_INSTRUCTION
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

async def enhance_resume_with_gemini(resume_text: str, target_role: str = None) -> tuple[str, list[str]]:
    """
    Performs content improvement, LaTeX formatting, and suggestion generation in a single call.
    """
    model = get_model()
    
    role_context = f"specifically for a {target_role} role" if target_role else ""
    
    prompt = f"""
    Analyze the following resume {role_context}:
    ---
    {resume_text}
    ---
    
    Tasks:
    1. Improve the content (action verbs, metrics, professional tone).
    2. Format the improved content as LaTeX (only provide the body commands like \\section, \\item, etc.).
    3. List 3-5 specific improvements made.

    Return the result as a JSON object with exactly these keys:
    {{
        "latex_body": "string containing LaTeX code",
        "suggestions": ["list", "of", "strings"]
    }}
    """

    try:
        # Generate content with JSON constraint
        response = await model.generate_content_async(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse the JSON response
        data = json.loads(response.text)
        
        final_latex = wrap_latex_content(data.get("latex_body", ""))
        suggestions = data.get("suggestions", ["Improved professional language", "Optimized formatting"])
        
        return final_latex, suggestions

    except Exception as e:
        print(f"Gemini Error: {e}")
        raise Exception(f"Error enhancing resume: {str(e)}")