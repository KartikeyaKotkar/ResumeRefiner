/**
 * ResumeRefiner Frontend Logic
 */


const SAMPLE_RESUMES = [
    {
        role: "Senior Software Engineer",
        text: `John Doe
Senior Software Engineer
(555) 123-4567 | john.doe@email.com | San Francisco, CA

SUMMARY
Highly skilled Senior Software Engineer with 8+ years of experience in full-stack development. Proven track record of designing and implementing scalable web applications. Expertise in Python, JavaScript, and Cloud Technologies.

EXPERIENCE
Tech Solutions Inc. - San Francisco, CA
Senior Software Engineer | Jan 2018 - Present
- Led a team of 5 engineers in migrating a monolithic architecture to microservices, improving deployment frequency by 40%.
- Designed and built a real-time analytics dashboard using React and Node.js, handling over 100k requests per second.
- Mentored junior developers and conducted code reviews to ensure code quality and best practices.

Innovate Corp. - Austin, TX
Software Engineer | Jun 2014 - Dec 2017
- Developed and maintained critical backend services using Django and PostgreSQL.
- Optimized database queries, reducing API latency by 30%.
- Collaborated with product managers to define requirements and deliver features on time.

EDUCATION
University of Texas at Austin
B.S. in Computer Science | May 2014

SKILLS
- Languages: Python, JavaScript, Java, SQL
- Frameworks: React, Node.js, Django, Flask
- Tools: Docker, Kubernetes, AWS, Git`
    },
    {
        role: "Product Manager",
        text: `Jane Smith
Product Manager
(555) 987-6543 | jane.smith@email.com | New York, NY

SUMMARY
Results-oriented Product Manager with 5 years of experience in B2B SaaS products. diverse background in market research, product strategy, and agile methodologies. Passionate about building products that solve real customer problems.

EXPERIENCE
SaaS Dynamics - New York, NY
Product Manager | Mar 2019 - Present
- Defined the product roadmap and strategy for a flagship CRM tool, resulting in a 25% increase in user retention.
- Conducted user research and usability testing to identify pain points and validate new feature ideas.
- Worked closely with engineering and design teams to launch 3 major product updates within one year.

Market Insights - Boston, MA
Associate Product Manager | Jul 2016 - Feb 2019
- Analyzed market trends and competitor landscape to inform product positioning.
- Managed the product backlog and prioritized user stories for sprint planning.
- Assisted in the launch of a mobile app feature that gained 10k downloads in the first month.

EDUCATION
Boston University
B.A. in Business Administration | May 2016

SKILLS
- Product Strategy, Roadmap Planning, Agile/Scrum
- Market Research, User Testing, Data Analysis
- Tools: Jira, Confluence, Figma, Google Analytics`
    },
    {
        role: "Data Analyst",
        text: `Alex Johnson
Data Analyst
(555) 555-5555 | alex.johnson@email.com | Chicago, IL

SUMMARY
Detail-oriented Data Analyst with a strong foundation in statistics and data visualization. Proficient in SQL, Python, and Tableau. Eager to leverage analytical skills to drive business insights.

EXPERIENCE
Retail Giants - Chicago, IL
Data Analysis Intern | Jun 2023 - Aug 2023
- Analyzed sales data to identify seasonal trends and optimize inventory levels.
- Created interactive dashboards in Tableau to visualize key performance indicators (KPIs) for the marketing team.
- Automated data cleaning processes using Python scripts, saving 5 hours of manual work per week.

University Research Lab
Research Assistant | Sep 2022 - May 2023
- Collected and processed large datasets for a sociology research project.
- Performed statistical analysis using R to test hypotheses and draw conclusions.
- Presented findings at a university undergraduate research conference.

EDUCATION
University of Chicago
B.S. in Statistics | May 2024

SKILLS
- SQL, Python (Pandas, NumPy), R
- Data Visualization: Tableau, Power BI, Matplotlib
- Statistical Analysis, Data Cleaning, Excel`
    }
];

let currentAbortController = null;

// Initialize components
document.addEventListener('DOMContentLoaded', () => {
    setupDragAndDrop();
    initializeTheme();
});

// --- Theme Management ---
function toggleTheme() {
    const html = document.documentElement;
    const themeIcon = document.getElementById('themeIcon');
    const isDark = html.getAttribute('data-theme') === 'dark';

    if (isDark) {
        html.removeAttribute('data-theme');
        themeIcon.textContent = '☀️';
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'dark');
        themeIcon.textContent = '🌙';
        localStorage.setItem('theme', 'dark');
    }
}

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('themeIcon');
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        themeIcon.textContent = '🌙';
    }
}

// --- File Handling & PDF Extraction ---
function toggleTextInput() {
    const textSection = document.getElementById('textInputSection');
    textSection.classList.toggle('hidden');
    if (!textSection.classList.contains('hidden')) {
        document.getElementById('pdfUpload').value = '';
    }
}

document.getElementById('pdfUpload').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handlePDFUpload(file);
});

async function handlePDFUpload(file) {
    const formData = new FormData();
    formData.append('pdf', file);

    try {
        const response = await fetch('http://localhost:5000/extract_pdf', {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error('Upload failed');

        const data = await response.json();
        document.getElementById('resumeText').value = data.text;
        document.getElementById('textInputSection').classList.remove('hidden');
    } catch (error) {
        alert('Error processing PDF. Please paste text manually.');
    }
}

function fillSampleResume() {
    const randomResume = SAMPLE_RESUMES[Math.floor(Math.random() * SAMPLE_RESUMES.length)];

    document.getElementById('resumeText').value = randomResume.text;
    document.getElementById('targetRole').value = randomResume.role;

    // Ensure text area is visible
    const textSection = document.getElementById('textInputSection');
    if (textSection.classList.contains('hidden')) {
        textSection.classList.remove('hidden');
    }

    // Clear any file upload
    document.getElementById('pdfUpload').value = '';

    // Scroll to text area
    textSection.scrollIntoView({ behavior: 'smooth' });
}

// --- Core AI Logic ---
async function enhanceResume() {
    const resumeText = document.getElementById('resumeText').value.trim();
    const targetRole = document.getElementById('targetRole').value.trim();

    if (!resumeText) {
        alert('Please provide resume content first.');
        return;
    }

    // Cancel existing request if user clicks again
    if (currentAbortController) currentAbortController.abort();
    currentAbortController = new AbortController();

    // UI State: Loading
    const enhanceBtn = document.getElementById('enhanceBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('results');

    loadingSpinner.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    enhanceBtn.disabled = true;

    try {
        const response = await fetch('http://localhost:5000/enhance_resume', {
            method: 'POST',
            signal: currentAbortController.signal,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                resume_text: resumeText,
                target_role: targetRole || undefined
            })
        });

        if (!response.ok) throw new Error('AI Enhancement failed');

        const data = await response.json();

        // Update UI with results
        document.getElementById('improvedText').value = data.improved_text;
        const suggestionsList = document.getElementById('suggestionsList');
        suggestionsList.innerHTML = data.suggestions
            .map(s => `<li>${s}</li>`)
            .join('');

        document.getElementById('downloadLatex').classList.remove('hidden');
        resultsSection.classList.remove('hidden');

    } catch (error) {
        if (error.name === 'AbortError') return;
        console.error(error);
        alert('An error occurred. Please try again.');
    } finally {
        loadingSpinner.classList.add('hidden');
        enhanceBtn.disabled = false;
    }
}

// --- Utilities ---
async function copyToClipboard(elementId, btn) {
    const element = document.getElementById(elementId);
    try {
        await navigator.clipboard.writeText(element.value);
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = originalText; }, 2000);
    } catch (err) {
        console.error('Clipboard failed', err);
    }
}

// --- Drag and Drop Logic ---
function setupDragAndDrop() {
    const dropZone = document.querySelector('.upload-label');
    if (!dropZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(name => {
        dropZone.addEventListener(name, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(name => {
        dropZone.addEventListener(name, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(name => {
        dropZone.addEventListener(name, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            document.getElementById('pdfUpload').files = e.dataTransfer.files;
            handlePDFUpload(file);
        }
    }, false);
}