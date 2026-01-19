/**
 * ResumeRefiner Frontend Logic
 */

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