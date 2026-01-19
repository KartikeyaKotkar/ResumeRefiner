"""Flask application for the ResumeRefiner service."""

import logging.config
from flask import Flask, request, jsonify, send_from_directory
import PyPDF2
from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
from pythonjsonlogger import jsonlogger
from app.gemini_utils import enhance_resume_with_gemini

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
        improved_text, suggestions = await enhance_resume_with_gemini(
            resume_text, target_role
        )

        response = {"improved_text": improved_text, "suggestions": suggestions}

        logger.info(
            "Successfully enhanced resume", extra={"num_suggestions": len(suggestions)}
        )

        return jsonify(response)

    except Exception as e:
        logger.error("Error processing resume", extra={"error": str(e)}, exc_info=True)
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


if __name__ == "__main__":
    # Defaults to False if FLASK_DEBUG is not set
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", debug=debug_mode)  # nosec B104
