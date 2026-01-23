"""Flask application for the ResumeRefiner service."""

import logging.config
from flask import Flask, request, jsonify, send_from_directory, send_file
import PyPDF2
from werkzeug.utils import secure_filename
import os
import subprocess
import tempfile
import io
import requests
from flask_cors import CORS
from pythonjsonlogger import jsonlogger
from app.gemini_utils import enhance_resume_with_gemini
from app.docx_utils import generate_docx_file

# Configure logging
logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            }
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "json"},
            "file": {
                "class": "logging.FileHandler",
                "filename": "resume_refiner.log",
                "formatter": "json",
            },
        },
        "root": {"level": "INFO", "handlers": ["console", "file"]},
    }
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/")
def index():
    """Serve the main application page."""
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files."""
    return send_from_directory("static", path)


@app.route("/extract_pdf", methods=["POST"])
async def extract_pdf():
    """Extract text from uploaded PDF."""
    try:
        if "pdf" not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400

        pdf_file = request.files["pdf"]
        if pdf_file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not pdf_file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "File must be a PDF"}), 400

        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""

        # Extract text from all pages
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return jsonify({"text": text.strip()})

    except Exception as e:
        logger.error("Error processing PDF", extra={"error": str(e)}, exc_info=True)
        return jsonify({"error": "Error processing PDF file", "message": str(e)}), 500


@app.route("/enhance_resume", methods=["POST"])
async def enhance_resume():
    """
    Enhance a resume using Gemini AI.

    Expected JSON input:
    {
        "resume_text": "raw resume content",
        "target_role": "desired job title" (optional)
    }
    """
    try:
        data = request.get_json()

        if not data or "resume_text" not in data:
            return jsonify({"error": "Missing required field: resume_text"}), 400

        resume_text = data["resume_text"]
        target_role = data.get("target_role")  # Optional field

        logger.info(
            "Processing resume enhancement request", extra={"target_role": target_role}
        )

        # Process the resume
        result = await enhance_resume_with_gemini(resume_text, target_role)

        logger.info(
            "Successfully enhanced resume", extra={"num_suggestions": len(result.get("suggestions", []))}
        )

        return jsonify(result)

    except Exception as e:
        logger.error("Error processing resume", extra={"error": str(e)}, exc_info=True)
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    """Generate PDF from LaTeX code."""
    try:
        data = request.get_json()
        latex_code = data.get("latex_code")
        if not latex_code:
            return jsonify({"error": "Missing latex_code"}), 400

        # Create a temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, "resume.tex")
            
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_code)
                
            # Run pdflatex
            # Note: This assumes pdflatex is installed and in PATH
            try:
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "resume.tex"],
                    cwd=temp_dir,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except FileNotFoundError:
                return jsonify({"error": "PDF generation unavailable (pdflatex not found on server)"}), 503
            except subprocess.CalledProcessError as e:
                return jsonify({"error": "LaTeX compilation failed", "details": e.stderr.decode()}), 400
                
            pdf_path = os.path.join(temp_dir, "resume.pdf")
            if os.path.exists(pdf_path):
                # Send file back
                return send_file(
                    pdf_path,
                    mimetype="application/pdf",
                    as_attachment=True,
                    download_name="resume.pdf"
                )
            else:
                return jsonify({"error": "PDF file not generated"}), 500

    except Exception as e:
        logger.error("PDF generation error", extra={"error": str(e)})
        return jsonify({"error": str(e)}), 500


@app.route("/generate_docx", methods=["POST"])
def generate_docx():
    """Generate DOCX from structured data."""
    try:
        data = request.get_json()
        structured_data = data.get("structured_data")
        
        if not structured_data:
            return jsonify({"error": "Missing structured_data"}), 400
            
        docx_stream = generate_docx_file(structured_data)
        
        return send_file(
            docx_stream,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name="resume.docx"
        )
        
    except Exception as e:
        logger.error("DOCX generation error", extra={"error": str(e)})
        return jsonify({"error": str(e)}), 500


@app.route("/create_gist", methods=["POST"])
def create_gist():
    """Create a GitHub Gist with the resume text."""
    try:
        data = request.get_json()
        content = data.get("content")
        filename = data.get("filename", "resume.txt")
        
        if not content:
            return jsonify({"error": "Missing content"}), 400
            
        # Create public gist (anonymous if no token, but better to just use simple post)
        # Note: Github API v3 allows creating gists
        
        gist_payload = {
            "description": "Resume generated by ResumeRefiner",
            "public": True,
            "files": {
                filename: {
                    "content": content
                }
            }
        }
        
        # We need a token for this to work reliably, but let's try unauthenticated first?
        # Creating gists generally requires authentication now.
        # If no token, we might need to ask user for one or usage is limited.
        # For now, let's assume we might have a token in env, or return error if not.
        
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
             return jsonify({"error": "Server not configured for Gist creation (Missing GITHUB_TOKEN)"}), 503
             
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        resp = requests.post("https://api.github.com/gists", json=gist_payload, headers=headers)
        
        if resp.status_code == 201:
            return jsonify(resp.json())
        else:
            return jsonify({"error": "Failed to create gist", "details": resp.text}), resp.status_code
            
    except Exception as e:
        logger.error("Gist creation error", extra={"error": str(e)})
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Defaults to False if FLASK_DEBUG is not set
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", debug=debug_mode)  # nosec B104
