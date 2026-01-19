"""Utility functions for interacting with Google's Gemini API."""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def create_content_improvement_prompt(resume_text: str, target_role: str = None) -> str:
    """Create the prompt for content improvement before LaTeX formatting."""
    role_context = f" for the role of {target_role}" if target_role else ""
    return (
        "Act as an expert resume assistant. Analyze and enhance the following resume{role_context}. "
        "Apply these improvements:\n\n"
        "1. Grammar and Language:\n"
        "   - Fix all grammatical errors\n"
        "   - Use active voice and strong action verbs\n"
        "   - Ensure consistent tense throughout\n\n"
        "2. Content Enhancement:\n"
        "   - Add measurable achievements and metrics\n"
        "   - Highlight relevant skills and experiences\n"
        "   - Remove unnecessary or redundant information\n\n"
        "3. Role-Specific Optimization:\n"
        "   - Incorporate relevant industry keywords\n"
        "   - Align experiences with job requirements\n"
        "   - Emphasize transferable skills\n\n"
        "4. Professional Tone:\n"
        "   - Maintain formal, professional language\n"
        "   - Ensure clear and concise descriptions\n"
        "   - Use industry-standard terminology\n\n"
        "Resume:\n{text}"
    ).format(role_context=role_context, text=resume_text)

def create_latex_format_prompt(improved_content: str) -> str:
    """Create the prompt for LaTeX formatting of the improved content."""
    return (
        "Format the following improved resume content as a LaTeX document. "
        "Follow these guidelines:\n"
        "1. Use a modern, professional LaTeX resume structure\n"
        "2. Create clear sections for: Personal Information, Summary, Experience, Education, Skills\n"
        "3. Use \\section{} for main sections and \\subsection{} where appropriate\n"
        "4. Format contact information in a clean, professional layout\n"
        "5. Use itemize environments for lists of achievements and skills\n"
        "6. Ensure proper spacing and formatting throughout\n"
        "7. Include only the content that goes inside the document environment\n\n"
        "Content to format:\n{text}"
    ).format(text=improved_content)
    

def wrap_latex_content(content: str) -> str:
    """Wrap the LaTeX content in a complete document structure."""
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
    Enhance a resume using Gemini AI and format it in LaTeX.
    
    Args:
        resume_text (str): The original resume text
        target_role (str, optional): The target job role
    
    Returns:
        tuple[str, list[str]]: Improved text (in LaTeX format) and list of suggestions
    """
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Step 1: Improve content
        content_prompt = create_content_improvement_prompt(resume_text, target_role)
        content_response = await model.generate_content_async(content_prompt)
        improved_content = content_response.text
        
        # Step 2: Format as LaTeX
        latex_prompt = create_latex_format_prompt(improved_content)
        latex_response = await model.generate_content_async(latex_prompt)
        latex_content = latex_response.text
        
        # Wrap in complete LaTeX document
        final_latex = wrap_latex_content(latex_content)
        
        # Generate detailed suggestions
        suggestions_prompt = (
            "Based on the improvements made to the resume, provide a detailed list of 3-5 key enhancements, including:\n"
            "1. Grammar and language improvements\n"
            "2. Content additions or restructuring\n"
            "3. Role-specific optimizations\n"
            "4. Formatting improvements\n\n"
            "Format as bullet points and be specific about what was changed."
        )
        suggestions_response = await model.generate_content_async(suggestions_prompt)
        
        # Parse suggestions into a list
        suggestions = [
            s.strip('- ') for s in suggestions_response.text.split('\n')
            if s.strip('- ')
        ]
        
        return final_latex, suggestions
        
    except Exception as e:
        raise Exception(f"Error enhancing resume with Gemini: {str(e)}")
