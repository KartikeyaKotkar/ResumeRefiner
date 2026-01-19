# ResumeRefiner

An AI-powered resume enhancement service that uses Google's Gemini API to improve and format resumes in LaTeX.

## Features

- PDF resume upload with drag & drop support
- Manual text input option
- Role-specific resume optimization
- LaTeX output with professional formatting
- Detailed improvement suggestions
- Modern, responsive web interface

## Technical Stack

- Backend: Flask (Python)
- AI: Google Gemini 1.5 Pro
- Frontend: HTML, CSS, JavaScript
- PDF Processing: PyPDF2
- Authentication: Environment-based API key

## Setup

1. Clone the repository:
```bash
git clone https://github.com/KartikeyaKotkar/ResumeRefiner.git
cd ResumeRefiner
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```
Edit `.env` and add your Gemini API key.

5. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:5000`.

## Docker Support

Run the application in a container ensuring consistent environments:

1. **Using Docker Compose** (Recommended):
```bash
docker-compose up -d
```

2. **Using standard Docker**:
```bash
# Build
docker build -t resume-refiner .

# Run
docker run -p 5000:5000 --env-file .env resume-refiner
```

3. **Using Makefile**:
```bash
make build
make run
```

## CI/CD Pipeline

This project uses **GitHub Actions** for automated testing and deployment assurance.
- **Linting**: Flake8 checks for code quality.
- **Security**: Bandit scans for python vulnerabilities.
- **Testing**: Pytest runs unit and integration tests.
- **Build**: Verifies Docker image creation.


## Usage

1. Upload your resume PDF or paste your resume text
2. (Optional) Specify your target role
3. Click "Enhance Resume"
4. Review the improved LaTeX version and suggestions
5. Download the LaTeX file or copy the content

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
