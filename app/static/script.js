function toggleTextInput() {
    const textSection = document.getElementById('textInputSection');
    textSection.classList.toggle('hidden');
    
    // Clear the file input if text input is shown
    if (!textSection.classList.contains('hidden')) {
        document.getElementById('pdfUpload').value = '';
    }
}

// Handle drag and drop
function setupDragAndDrop() {
    const dropZone = document.querySelector('.upload-label');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const file = dt.files[0];
    
    if (file && file.type === 'application/pdf') {
        document.getElementById('pdfUpload').files = dt.files;
        handlePDFUpload(file);
    }
}

// Initialize drag and drop
document.addEventListener('DOMContentLoaded', setupDragAndDrop);

// Handle PDF file upload
document.getElementById('pdfUpload').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handlePDFUpload(file);
    }
});

async function handlePDFUpload(file) {
    const formData = new FormData();
    formData.append('pdf', file);
    
    try {
        const response = await fetch('http://localhost:5000/extract_pdf', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        document.getElementById('resumeText').value = data.text;
        document.getElementById('textInputSection').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing PDF. Please try uploading again or paste the text manually.');
    }
}

async function enhanceResume() {
    const resumeText = document.getElementById('resumeText').value.trim();
    const targetRole = document.getElementById('targetRole').value.trim();
    
    if (!resumeText) {
        alert('Please upload a PDF or paste your resume content.');
        return;
    }

    // Show loading spinner
    document.getElementById('loadingSpinner').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('enhanceBtn').disabled = true;

    try {
        const response = await fetch('http://localhost:5000/enhance_resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                resume_text: resumeText,
                target_role: targetRole || undefined
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Display results
        document.getElementById('improvedText').value = data.improved_text;
        
        const suggestionsList = document.getElementById('suggestionsList');
        suggestionsList.innerHTML = data.suggestions
            .map(suggestion => `<li>${suggestion}</li>`)
            .join('');
            
        // Enable download LaTeX button
        document.getElementById('downloadLatex').classList.remove('hidden');

        // Show results section
        document.getElementById('results').classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while enhancing your resume. Please try again.');
    } finally {
        // Hide loading spinner and re-enable button
        document.getElementById('loadingSpinner').classList.add('hidden');
        document.getElementById('enhanceBtn').disabled = false;
    }
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    document.execCommand('copy');
    
    // Visual feedback
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    setTimeout(() => {
        button.textContent = originalText;
    }, 2000);
}
