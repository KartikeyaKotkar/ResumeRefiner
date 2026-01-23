"""Flask application for the ResumeRefiner service."""

import os
import logging.config
import tempfile
import subprocess
import pypdf
import requests
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from pythonjsonlogger import jsonlogger

# Import your utilities
from app.gemini_utils import enhance_resume_with_gemini
from app.docx_utils import generate_docx_file

# Logging Configuration
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
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)


@app.route("/extract_pdf", methods=["POST"])
async def extract_pdf():
    try:
        if "pdf" not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400

        pdf_file = request.files["pdf"]
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = "".join([page.extract_text() + "\n" for page in pdf_reader.pages])

        return jsonify({"text": text.strip()})
    except Exception as e:
        logger.error("PDF Extraction Error", extra={"error": str(e)})
        return jsonify({"error": str(e)}), 500


@app.route("/enhance_resume", methods=["POST"])
async def enhance_resume():
    try:
        data = request.get_json()
        if not data or "resume_text" not in data:
            return jsonify({"error": "Missing resume_text"}), 400

        resume_text = data["resume_text"]
        target_role = data.get("target_role")

        logger.info("Enhancing resume", extra={"target_role": target_role})

        # Call our updated Gemini utility
        result = await enhance_resume_with_gemini(resume_text, target_role)

        return jsonify(result)
    except Exception as e:
        logger.error("Enhancement Error", extra={"error": str(e)})
        return jsonify({"error": str(e)}), 500


@app.route("/generate_pdf", methods=["POST"])
def generate_pdf():
    try:
        data = request.get_json()
        latex_code = data.get("latex_code")

        with tempfile.TemporaryDirectory() as temp_dir:
            tex_file = os.path.join(temp_dir, "resume.tex")
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_code)

            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "resume.tex"],
                cwd=temp_dir,
                check=True,
                capture_output=True,
            )

            return send_file(
                os.path.join(temp_dir, "resume.pdf"),
                mimetype="application/pdf",
                as_attachment=True,
                download_name="resume.pdf",
            )
    except Exception as e:
        return jsonify({"error": "LaTeX failed", "details": str(e)}), 500


@app.route("/generate_docx", methods=["POST"])
def generate_docx():
    try:
        data = request.get_json()
        docx_stream = generate_docx_file(data.get("structured_data"))
        return send_file(
            docx_stream,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name="resume.docx",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    app.run(host="0.0.0.0", port=5000, debug=debug_mode)  # nosec B201
