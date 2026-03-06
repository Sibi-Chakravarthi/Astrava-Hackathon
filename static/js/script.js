document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const dropArea = document.getElementById('drag-area');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const btnRemove = document.getElementById('btn-remove');
    const btnAnalyze = document.getElementById('btn-analyze');
    const uploadForm = document.getElementById('upload-form');
    
    const loader = document.getElementById('loader');
    const resultsPanel = document.getElementById('results-panel');
    const resultImage = document.getElementById('result-image');
    const predictionsContainer = document.getElementById('predictions-container');

    let currentFile = null;

    // --- File Upload Logic ---
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            handleFile(file);
        }
    });

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('active'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('active'), false);
    });

    dropArea.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        
        if (file && file.type.startsWith('image/')) {
            fileInput.files = dt.files; // assign to input
            handleFile(file);
        } else {
            alert('Please upload an image file.');
        }
    });

    function handleFile(file) {
        currentFile = file;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropArea.classList.add('hidden');
            previewContainer.classList.remove('hidden');
            btnAnalyze.disabled = false;
        };
        reader.readAsDataURL(file);
        
        // Hide previous results
        resultsPanel.classList.add('hidden');
    }

    btnRemove.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        imagePreview.src = '';
        previewContainer.classList.add('hidden');
        dropArea.classList.remove('hidden');
        btnAnalyze.disabled = true;
    });

    // --- Form Submission Logic ---
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!currentFile) return;

        const formData = new FormData();
        formData.append('file', currentFile);

        // UI States
        btnAnalyze.disabled = true;
        loader.classList.remove('hidden');
        resultsPanel.classList.add('hidden');

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Server error occurred');
            }

            // Display Results
            displayResults(data);

        } catch (error) {
            console.error('Error:', error);
            alert(`Error analyzing image: ${error.message}`);
        } finally {
            loader.classList.add('hidden');
            btnAnalyze.disabled = false;
        }
    });

    function displayResults(data) {
        // Set processed image
        resultImage.src = data.image;
        
        // Clear previous predictions
        predictionsContainer.innerHTML = '';

        if (!data.predictions || data.predictions.length === 0) {
            predictionsContainer.innerHTML = `
                <div class="prediction-card healthy">
                    <div class="pred-header">
                        <div class="pred-title">
                            <h4>No Diseases Detected</h4>
                        </div>
                    </div>
                    <p>No agricultural diseases were identified in the image.</p>
                </div>
            `;
        } else {
            // Render each prediction
            data.predictions.forEach(pred => {
                const isHealthy = pred.class_name.toLowerCase().includes('healthy');
                const cardClass = isHealthy ? 'healthy' : 'disease';
                
                // Determine severity styling
                let severityClass = 'severity-low';
                let severityText = `${pred.severity.toFixed(1)}%`;
                
                if (isHealthy) {
                    severityText = "N/A";
                } else if (pred.severity > 30) {
                    severityClass = 'severity-high';
                } else if (pred.severity > 10) {
                    severityClass = 'severity-med';
                }

                const sourceHtml = pred.source ? 
                    `<div class="pred-source">
                        <strong>Source:</strong> <a href="${pred.source}" target="_blank">View reference material</a>
                    </div>` : '';

                const cardHtml = `
                    <div class="prediction-card ${cardClass}">
                        <div class="pred-header">
                            <div class="pred-title">
                                <h4>${pred.class_name.replace(/_/g, ' ')}</h4>
                            </div>
                            <div class="pred-severity ${severityClass}">
                                Severity: ${severityText}
                            </div>
                        </div>
                        
                        <div class="pred-recommendation">
                            <h5><i class="fa-solid ${isHealthy ? 'fa-circle-check' : 'fa-prescription-bottle-medical'}"></i> Recommendation</h5>
                            <p>${pred.recommendation}</p>
                        </div>
                        ${sourceHtml}
                    </div>
                `;
                predictionsContainer.insertAdjacentHTML('beforeend', cardHtml);
            });
        }

        // Show panel
        resultsPanel.classList.remove('hidden');
        
        // Scroll to results on mobile
        if(window.innerWidth < 900) {
            resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
});
