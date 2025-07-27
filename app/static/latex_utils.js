function downloadLatexFile() {
    const latexContent = document.getElementById('improvedText').value;
    const blob = new Blob([latexContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'enhanced_resume.tex';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
