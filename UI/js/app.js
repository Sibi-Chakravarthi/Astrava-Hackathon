// =============================================================================
// AgraVision — Frontend Application Logic
// Handles uploads, API calls, result rendering, and field heatmap
// =============================================================================

const API_BASE = '';  // Same origin — Flask serves both

// ===== STATE =====
let selectedFile = null;
let fieldFiles = [];

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    checkApiHealth();
    loadDiseaseList();
    setupUploadHandlers();
    setupFieldUploadHandlers();
    setupNavigation();
});

// ===== API HEALTH CHECK =====
async function checkApiHealth() {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');

    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();

        if (data.model_loaded) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Model Ready';
        } else {
            statusDot.className = 'status-dot demo';
            statusText.textContent = 'Demo Mode';
        }
    } catch {
        statusDot.className = 'status-dot';
        statusText.textContent = 'Offline';
    }
}

// ===== NAVIGATION =====
function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

// ===== SINGLE IMAGE UPLOAD =====
function setupUploadHandlers() {
    const zone = document.getElementById('upload-zone');
    const input = document.getElementById('file-input');
    const btnAnalyze = document.getElementById('btn-analyze');
    const btnChange = document.getElementById('btn-change-image');

    // Click to upload
    zone.addEventListener('click', () => input.click());

    // Drag & drop
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    // File input change
    input.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Analyze button
    btnAnalyze.addEventListener('click', analyzeImage);

    // Change image
    btnChange.addEventListener('click', () => {
        input.value = '';
        input.click();
    });
}

function handleFileSelect(file) {
    selectedFile = file;

    // Show preview
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const uploadZone = document.getElementById('upload-zone');
    const previewFilename = document.getElementById('preview-filename');

    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewFilename.textContent = file.name;
        uploadZone.style.display = 'none';
        previewContainer.style.display = 'flex';
    };
    reader.readAsDataURL(file);

    // Hide previous results
    document.getElementById('results-container').style.display = 'none';
}

async function analyzeImage() {
    if (!selectedFile) return;

    const overlay = document.getElementById('preview-overlay');
    const btnAnalyze = document.getElementById('btn-analyze');

    overlay.classList.add('active');
    btnAnalyze.disabled = true;
    btnAnalyze.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px"></div> Analyzing...';

    try {
        const formData = new FormData();
        formData.append('image', selectedFile);

        const res = await fetch(`${API_BASE}/api/predict`, {
            method: 'POST',
            body: formData
        });

        const data = await res.json();

        if (data.success) {
            renderResults(data);
            showToast('Analysis complete!', 'success');
        } else {
            showToast(data.error || 'Analysis failed', 'error');
        }
    } catch (err) {
        showToast('Could not connect to server. Is app.py running?', 'error');
        console.error(err);
    } finally {
        overlay.classList.remove('active');
        btnAnalyze.disabled = false;
        btnAnalyze.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg> Analyze Image`;
    }
}

// ===== RENDER RESULTS =====
function renderResults(data) {
    const container = document.getElementById('results-container');
    container.style.display = 'grid';

    // Scroll to results
    setTimeout(() => container.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);

    const pred = data.prediction;
    const sev = data.severity;
    const rec = data.recommendation;

    const isHealthy = rec.is_healthy;

    // --- Prediction Card ---
    document.getElementById('result-crop').textContent = rec.crop;
    document.getElementById('result-disease').textContent = rec.disease;
    document.getElementById('inference-time').textContent = `${data.metadata.inference_time_seconds}s`;

    // Confidence ring animation
    const confValue = pred.confidence;
    const circle = document.getElementById('confidence-circle');
    const circumference = 2 * Math.PI * 52; // r=52
    const offset = circumference - (confValue / 100) * circumference;

    setTimeout(() => {
        circle.style.strokeDashoffset = offset;
        document.getElementById('confidence-value').textContent = `${confValue}%`;
    }, 100);

    // Top 5 predictions
    const top5Container = document.getElementById('top5-container');
    top5Container.innerHTML = pred.top5.map(p => `
        <div class="top5-item">
            <span class="top5-name">${formatClassName(p.class)}</span>
            <div class="top5-bar-container">
                <div class="top5-bar" style="width: 0%"></div>
            </div>
            <span class="top5-conf">${p.confidence}%</span>
        </div>
    `).join('');

    // Animate bars
    setTimeout(() => {
        top5Container.querySelectorAll('.top5-bar').forEach((bar, i) => {
            bar.style.width = `${pred.top5[i].confidence}%`;
        });
    }, 200);

    // --- Severity Card ---
    const sevBadge = document.getElementById('severity-badge');
    sevBadge.textContent = sev.label;
    sevBadge.className = `severity-badge ${sev.label}`;

    document.getElementById('severity-percent').textContent = `${sev.percent}%`;
    document.getElementById('healthy-percent').textContent = `${sev.healthy_percent}%`;

    const gaugeFill = document.getElementById('severity-fill');
    gaugeFill.className = `gauge-fill ${sev.label}`;
    setTimeout(() => {
        gaugeFill.style.width = `${sev.percent}%`;
    }, 100);

    // Heatmap images
    if (sev.heatmap) {
        document.getElementById('heatmap-image').src = `data:image/jpeg;base64,${sev.heatmap}`;
    }
    if (sev.annotated) {
        document.getElementById('annotated-image').src = `data:image/jpeg;base64,${sev.annotated}`;
    }

    // --- Recommendation Card ---
    const predCard = document.getElementById('prediction-card');
    if (isHealthy) {
        predCard.classList.add('healthy-result');
    } else {
        predCard.classList.remove('healthy-result');
    }

    document.getElementById('rec-description').textContent = rec.description;
    document.getElementById('rec-scientific').textContent = rec.scientific_name || 'N/A';
    document.getElementById('rec-severity-desc').textContent = rec.severity_description || '';
    document.getElementById('rec-fertilizer').textContent = rec.fertilizer;
    document.getElementById('rec-prevention').textContent = rec.prevention;

    const treatmentOl = document.getElementById('rec-treatment');
    treatmentOl.innerHTML = (rec.treatment || []).map(t => `<li>${t}</li>`).join('');
}

// ===== FIELD UPLOAD =====
function setupFieldUploadHandlers() {
    const zone = document.getElementById('field-upload-zone');
    const input = document.getElementById('field-file-input');
    const btnAnalyze = document.getElementById('btn-field-analyze');

    zone.addEventListener('click', () => input.click());

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        handleFieldFiles(e.dataTransfer.files);
    });

    input.addEventListener('change', (e) => {
        handleFieldFiles(e.target.files);
    });

    btnAnalyze.addEventListener('click', analyzeField);
}

function handleFieldFiles(files) {
    fieldFiles = Array.from(files).filter(f => {
        const ext = f.name.split('.').pop().toLowerCase();
        return ['jpg', 'jpeg', 'png', 'webp', 'bmp'].includes(ext);
    });

    const preview = document.getElementById('field-images-preview');
    const btnAnalyze = document.getElementById('btn-field-analyze');

    preview.innerHTML = '';

    fieldFiles.forEach((file, idx) => {
        const thumb = document.createElement('div');
        thumb.className = 'field-preview-thumb';

        const img = document.createElement('img');
        const reader = new FileReader();
        reader.onload = (e) => { img.src = e.target.result; };
        reader.readAsDataURL(file);

        const label = document.createElement('div');
        label.className = 'thumb-label';
        label.textContent = `Zone ${idx + 1}`;

        thumb.appendChild(img);
        thumb.appendChild(label);
        preview.appendChild(thumb);
    });

    if (fieldFiles.length > 0) {
        btnAnalyze.style.display = 'inline-flex';
    }
}

async function analyzeField() {
    if (fieldFiles.length === 0) return;

    const btnAnalyze = document.getElementById('btn-field-analyze');
    btnAnalyze.disabled = true;
    btnAnalyze.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px"></div> Analyzing Field...';

    try {
        const formData = new FormData();
        fieldFiles.forEach(f => formData.append('images', f));

        const res = await fetch(`${API_BASE}/api/analyze-field`, {
            method: 'POST',
            body: formData
        });

        const data = await res.json();

        if (data.success) {
            renderFieldResults(data);
            showToast(`Field analysis complete! ${data.zone_results.length} zones analyzed.`, 'success');
        } else {
            showToast(data.error || 'Field analysis failed', 'error');
        }
    } catch (err) {
        showToast('Could not connect to server', 'error');
        console.error(err);
    } finally {
        btnAnalyze.disabled = false;
        btnAnalyze.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> Generate Field Health Map`;
    }
}

function renderFieldResults(data) {
    const container = document.getElementById('field-results');
    container.style.display = 'block';

    setTimeout(() => container.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);

    const stats = data.field_stats;

    // Stats grid
    const statsGrid = document.getElementById('field-stats-grid');
    statsGrid.innerHTML = `
        <div class="field-stat-card">
            <div class="field-stat-value green">${stats.total_zones}</div>
            <div class="field-stat-label">Total Zones</div>
        </div>
        <div class="field-stat-card">
            <div class="field-stat-value ${stats.average_severity > 50 ? 'red' : stats.average_severity > 25 ? 'amber' : 'green'}">${stats.average_severity}%</div>
            <div class="field-stat-label">Avg Severity</div>
        </div>
        <div class="field-stat-card">
            <div class="field-stat-value red">${stats.max_severity}%</div>
            <div class="field-stat-label">Max Severity</div>
        </div>
        <div class="field-stat-card">
            <div class="field-stat-value red">${stats.critical_zones}</div>
            <div class="field-stat-label">Critical Zones</div>
        </div>
        <div class="field-stat-card">
            <div class="field-stat-value green">${stats.healthy_zones}</div>
            <div class="field-stat-label">Healthy Zones</div>
        </div>
    `;

    // Field heatmap
    if (data.field_heatmap) {
        document.getElementById('field-heatmap').src = `data:image/jpeg;base64,${data.field_heatmap}`;
    }

    // Zone results
    const zoneContainer = document.getElementById('zone-results');
    zoneContainer.innerHTML = data.zone_results.map((zone, idx) => {
        const sevPercent = zone.severity.percent;
        const sevColor = sevPercent > 55 ? 'background:rgba(248,113,113,0.15);color:#f87171' :
            sevPercent > 25 ? 'background:rgba(251,191,36,0.15);color:#fbbf24' :
                'background:rgba(52,211,153,0.15);color:#34d399';

        return `
        <div class="zone-card">
            <div class="zone-card-header">
                <span class="zone-name">Zone ${idx + 1}</span>
                <span class="zone-severity" style="${sevColor}">${sevPercent}%</span>
            </div>
            <div class="zone-disease">${zone.recommendation.disease} (${zone.recommendation.crop})</div>
            <div class="zone-confidence">Confidence: ${zone.prediction.confidence}%</div>
        </div>`;
    }).join('');
}

// ===== DISEASE LIST =====
async function loadDiseaseList() {
    try {
        const res = await fetch(`${API_BASE}/api/diseases`);
        const data = await res.json();
        renderDiseaseList(data.diseases);
    } catch {
        // Fallback static list
        renderDiseaseList([
            { key: 'rice_blast', crop: 'Rice', disease: 'Rice Blast' },
            { key: 'rice_brownspot', crop: 'Rice', disease: 'Brown Spot' },
            { key: 'rice_leaf_blight', crop: 'Rice', disease: 'Bacterial Leaf Blight' },
            { key: 'wheat_rust', crop: 'Wheat', disease: 'Wheat Rust' },
            { key: 'wheat_septoria', crop: 'Wheat', disease: 'Septoria Leaf Blotch' },
            { key: 'cotton_bacterial_blight', crop: 'Cotton', disease: 'Bacterial Blight' },
            { key: 'cotton_curl_virus', crop: 'Cotton', disease: 'Leaf Curl Virus' },
            { key: 'cotton_fusarium_wilt', crop: 'Cotton', disease: 'Fusarium Wilt' },
            { key: 'tomato_early_blight', crop: 'Tomato', disease: 'Early Blight' },
            { key: 'tomato_late_blight', crop: 'Tomato', disease: 'Late Blight' },
            { key: 'tomato_leaf_mold', crop: 'Tomato', disease: 'Leaf Mold' },
            { key: 'tomato_yellow_curl', crop: 'Tomato', disease: 'Yellow Leaf Curl Virus' },
        ]);
    }
}

function renderDiseaseList(diseases) {
    const grid = document.getElementById('diseases-grid');

    const render = (crop) => {
        const filtered = crop === 'all' ? diseases : diseases.filter(d => d.crop === crop);
        grid.innerHTML = filtered.map(d => `
            <div class="disease-info-card" data-crop="${d.crop}">
                <div class="disease-card-crop">${getCropEmoji(d.crop)} ${d.crop}</div>
                <div class="disease-card-name">${d.disease}</div>
                <span class="disease-card-key">${d.key}</span>
            </div>
        `).join('');
    };

    render('all');

    // Crop tabs
    document.querySelectorAll('.crop-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.crop-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            render(tab.dataset.crop);
        });
    });
}

// ===== UTILITIES =====
function formatClassName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getCropEmoji(crop) {
    const emojis = { Rice: '🌾', Wheat: '🌿', Cotton: '☁️', Tomato: '🍅' };
    return emojis[crop] || '🌱';
}

function showToast(message, type = 'success') {
    // Remove existing toasts
    document.querySelectorAll('.toast').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${type === 'success' ? '✅' : '❌'}</span>
        <span style="font-size:0.9rem">${message}</span>
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
