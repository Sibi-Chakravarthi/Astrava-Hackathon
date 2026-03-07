/**
 * Astrava - Core Logics
 */

const CONFIG = {
    // Note: ensure this matches your Flask endpoint.
    API_URL: '/predict',
};

// --- DATA: Hardcoded Crop & Disease Definitions (Wait for User confirmation, standard placeholders for now) ---
const CROP_DISEASES = {
    'rice': [
        { name: 'Rice Blast', desc: 'Apply Tricyclazole 75WP. Boost potassium and silica.' },
        { name: 'Rice Leaf Blight', desc: 'Apply Copper Oxychloride. Reduce nitrogen.' },
        { name: 'Rice Grain Discoloration', desc: 'Apply Propiconazole. Ensure proper drainage.' },
        { name: 'Rice Pesticide Residue', desc: 'Stop pesticide application. Flush field with water.' }
    ],
    'cotton': [
        { name: 'Cotton Bacterial Blight', desc: 'Apply Copper-based bactericide. Remove infected leaves.' },
        { name: 'Cotton Leaf Curl Virus', desc: 'No cure — remove infected plants. Apply imidacloprid for whitefly control.' },
        { name: 'Cotton Grey Mildew', desc: 'Apply Carbendazim. Improve air circulation.' },
        { name: 'Cotton Alternaria Leaf Spot', desc: 'Apply Mancozeb. Avoid overhead irrigation.' },
        { name: 'Cotton Wilt', desc: 'Drench soil with Carbendazim. Improve drainage.' }
    ],
    'tomato': [
        { name: 'Tomato Early Blight', desc: 'Apply Chlorothalonil. Mulch around base of plant.' },
        { name: 'Tomato Late Blight', desc: 'Apply Metalaxyl + Mancozeb immediately. Remove infected tissue.' },
        { name: 'Tomato Bacterial Spot', desc: 'Apply Copper Hydroxide. Avoid working in wet conditions.' },
        { name: 'Tomato Septoria Leaf Spot', desc: 'Apply Chlorothalonil or Mancozeb. Remove lower leaves.' },
        { name: 'Tomato Mosaic Virus', desc: 'No cure — remove and destroy infected plants. Control aphids.' },
        { name: 'Tomato Yellow Leaf Curl Virus', desc: 'No cure — remove infected plants. Apply thiamethoxam for whitefly.' },
        { name: 'Tomato Leaf Mold', desc: 'Apply Copper Oxychloride. Reduce humidity.' },
        { name: 'Tomato Spider Mite', desc: 'Apply Abamectin or neem oil. Increase humidity.' }
    ],
    'wheat': [
        { name: 'Wheat Powdery Mildew', desc: 'Apply Tebuconazole. Avoid excess nitrogen.' },
        { name: 'Wheat Septoria Leaf Blotch', desc: 'Apply Propiconazole. Remove crop debris after harvest.' },
        { name: 'Wheat Stem Rust', desc: 'Apply Tebuconazole or Propiconazole immediately.' },
        { name: 'Wheat Yellow Rust', desc: 'Apply Tebuconazole. Monitor weekly for spread.' }
    ]
};

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initNavigation();
    initFarmerPortal();
    initDroneDashboard();
    initLocationControls();
    initTimeSeries();
});

// ==========================================
// 0. Theme Toggle
// ==========================================
function initThemeToggle() {
    const themeToggleBtn = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

    // Check local storage for theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        if (themeIcon) themeIcon.className = 'ri-sun-fill';
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.body.getAttribute('data-theme');
            if (currentTheme === 'dark') {
                document.body.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                if (themeIcon) themeIcon.className = 'ri-moon-fill';
                updateChartTheme('light');
            } else {
                document.body.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                if (themeIcon) themeIcon.className = 'ri-sun-fill';
                updateChartTheme('dark');
            }
        });
    }
}

function updateChartTheme(theme) {
    if (typeof timeSeriesChartInstance !== 'undefined' && timeSeriesChartInstance) {
        const isDark = theme === 'dark';
        const textColor = isDark ? '#f8fafc' : '#1e293b';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        
        timeSeriesChartInstance.options.plugins.legend.labels.color = textColor;
        timeSeriesChartInstance.options.scales.x.ticks.color = textColor;
        timeSeriesChartInstance.options.scales.x.grid.color = gridColor;
        timeSeriesChartInstance.options.scales.y.ticks.color = textColor;
        timeSeriesChartInstance.options.scales.y.grid.color = gridColor;
        timeSeriesChartInstance.update();
    }
}

// ==========================================
// 1. Navigation & Routing
// ==========================================
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.view-section');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Update Active Nav Icon
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // Switch Section Views
            const targetId = item.getAttribute('data-target');
            sections.forEach(sec => {
                if (sec.id === targetId) {
                    sec.classList.remove('hidden');
                    sec.classList.add('active');
                } else {
                    sec.classList.remove('active');
                    sec.classList.add('hidden');
                }
            });
        });
    });
}

// ==========================================
// 2. Farmer Portal (Upload & Analysis)
// ==========================================
function initFarmerPortal() {
    const uploadZone = document.getElementById('farmerUploadZone');
    const fileInput = document.getElementById('farmerImageInput');
    const previewZone = document.getElementById('farmerPreviewZone');
    const previewImg = document.getElementById('farmerPreviewImg');
    const scanningOverlay = document.getElementById('scanningOverlay');
    const resetBtn = document.getElementById('farmerResetBtn');

    // Drag and Drop Events
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFarmerUpload(e.dataTransfer.files[0]);
        }
    });

    // Click Upload
    uploadZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFarmerUpload(e.target.files[0]);
        }
    });

    // Reset Button
    resetBtn.addEventListener('click', resetFarmerPortal);

    function handleFarmerUpload(file) {
        // Validate
        if (!file.type.startsWith('image/')) {
            alert("Please upload a valid image file.");
            return;
        }

        // Show Local Preview Immediately
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            uploadZone.classList.add('hidden');
            previewZone.classList.remove('hidden');
            scanningOverlay.classList.remove('hidden'); // Show Scanning Animation

            // Call API
            analyzeImage(file);
        };
        reader.readAsDataURL(file);
    }
}

async function analyzeImage(file) {
    const formData = new FormData();
    formData.append('file', file); // app.py expects 'file'

    try {
        const response = await fetch(CONFIG.API_URL, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            let errorText = "Server error occurred.";
            try {
                const errData = await response.json();
                if (errData.error) errorText = errData.error;
            } catch (e) { }
            throw new Error(errorText);
        }

        const data = await response.json();

        // Hide Scanning Overlay
        document.getElementById('scanningOverlay').classList.add('hidden');

        if (data.error) {
            alert(data.error);
            resetFarmerPortal();
            return;
        }

        renderFarmerResults(data);

    } catch (error) {
        console.error("Analysis Error:", error);
        document.getElementById('scanningOverlay').classList.add('hidden');
        alert("Analysis failed: " + error.message);
    }
}

function renderFarmerResults(data) {
    // 1. Update Image to bounded box version generated by app.py
    if (data.image) {
        document.getElementById('farmerPreviewImg').src = data.image;
    }

    // 2. Compute Max Severity and dominant disease
    let maxSeverity = 0;
    let dominantDisease = 'Unknown';
    let recommendations = [];

    if (data.predictions && data.predictions.length > 0) {
        data.predictions.forEach(p => {
            if (p.severity > maxSeverity) {
                maxSeverity = p.severity;
                dominantDisease = p.class_name;
            }
            if (p.recommendation && !recommendations.includes(p.recommendation)) {
                recommendations.push(p.recommendation);
            }
        });
    }

    // Fallback if healthy or not finding anything sever
    if (maxSeverity === 0 && data.predictions.length > 0) {
        dominantDisease = data.predictions[0].class_name; // might be "healthy"
        recommendations.push(data.predictions[0].recommendation || "No immediate action required.");
    }

    // 3. Update DOM
    document.getElementById('farmerResultsPlaceholder').classList.add('hidden');
    document.getElementById('farmerResultsContent').classList.remove('hidden');

    document.getElementById('farmerDiseaseName').innerText = dominantDisease.replace(/_/g, ' ');

    // Animate Circle
    const circle = document.getElementById('farmerSeverityCircle');
    const valueEl = document.getElementById('farmerSeverityValue');

    // SVG circle dasharray animation (100 is full circumference here)
    circle.style.strokeDasharray = `${maxSeverity}, 100`;
    valueEl.innerHTML = `${Math.round(maxSeverity)}<span>%</span>`;

    // Change circle color based on severity
    if (maxSeverity < 20) circle.style.stroke = 'var(--success-color)';
    else if (maxSeverity < 50) circle.style.stroke = 'var(--warning-color)';
    else circle.style.stroke = 'var(--danger-color)';

    // 4. Update Recommendations List
    const recList = document.getElementById('farmerRecList');
    recList.innerHTML = ''; // clear old

    if (recommendations.length === 0) {
        recList.innerHTML = `<div class="rec-item"><span>No specific treatment found.</span></div>`;
    } else {
        recommendations.forEach(rec => {
            recList.innerHTML += `
                <div class="rec-item">
                    <strong>Primary Treatment</strong>
                    <span>${rec}</span>
                </div>
            `;
        });
    }
}

function resetFarmerPortal() {
    document.getElementById('farmerImageInput').value = '';
    document.getElementById('farmerPreviewImg').src = '';

    document.getElementById('farmerPreviewZone').classList.add('hidden');
    document.getElementById('farmerUploadZone').classList.remove('hidden');

    document.getElementById('farmerResultsContent').classList.add('hidden');
    document.getElementById('farmerResultsPlaceholder').classList.remove('hidden');

    // reset circle
    document.getElementById('farmerSeverityCircle').style.strokeDasharray = '0, 100';
    document.getElementById('farmerSeverityValue').innerHTML = `0<span>%</span>`;
}


// ==========================================
// 3. Drone Dashboard Logic
// ==========================================
function initDroneDashboard() {
    const cropBtns = document.querySelectorAll('.btn-crop');

    // Initialize first crop (Rice)
    renderDiseases('rice');

    cropBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            cropBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Get crop string and display
            const cropType = btn.getAttribute('data-crop');
            // update UI label
            document.getElementById('activeCropName').innerText = btn.innerText.trim();

            renderDiseases(cropType);
        });
    });
}

function renderDiseases(cropKey) {
    const accordion = document.getElementById('diseaseAccordion');
    accordion.innerHTML = ''; // clear previous

    const diseases = CROP_DISEASES[cropKey] || [];

    if (diseases.length === 0) {
        accordion.innerHTML = '<p class="text-muted" style="padding:1rem;">No data available.</p>';
        return;
    }

    diseases.forEach((disease, idx) => {
        const item = document.createElement('div');
        item.className = 'accordion-item';

        item.innerHTML = `
            <div class="accordion-header">
                <span>${disease.name}</span>
                <i class="ri-arrow-down-s-line icon-chevron"></i>
            </div>
            <div class="accordion-content">
                <p style="padding-bottom: 1rem;">${disease.desc}</p>
            </div>
        `;

        // Click event for accordion toggle
        item.querySelector('.accordion-header').addEventListener('click', function () {
            // close others
            Array.from(accordion.children).forEach(child => {
                if (child !== item) {
                    child.classList.remove('active');
                    const content = child.querySelector('.accordion-content');
                    content.style.maxHeight = null;
                }
            });

            // toggle current
            item.classList.toggle('active');
            const content = item.querySelector('.accordion-content');
            if (item.classList.contains('active')) {
                content.style.maxHeight = content.scrollHeight + "px";
            } else {
                content.style.maxHeight = null;
            }
        });

        // Open first item by default
        if (idx === 0) {
            // Use timeout to allow DOM to render before calculating scrollHeight
            setTimeout(() => {
                item.classList.add('active');
                const content = item.querySelector('.accordion-content');
                content.style.maxHeight = content.scrollHeight + "px";
            }, 10);
        }

        accordion.appendChild(item);
    });
}


// ==========================================
// 5. Location Controls Logic
// ==========================================
function initLocationControls() {
    const useLocationBtn = document.getElementById('useLocationBtn');
    const coordsInput = document.getElementById('farmCoordinates');
    const locationDisplay = document.getElementById('locationDisplay');
    const coordsText = document.getElementById('coordsText');
    const dashboardHeatmap = document.getElementById('dashboardHeatmap');
    const dashboardFieldText = document.getElementById('dashboardFieldText');

    if (!useLocationBtn) return;

    // Helper to request a high-resolution satellite map based on coordinates
    function updateDashboardHeatmap(locString) {
        if (!dashboardHeatmap) return;

        // Parse the lat/lon string
        const parts = locString.split(',');
        if (parts.length === 2) {
            const lat = parseFloat(parts[0].trim());
            const lon = parseFloat(parts[1].trim());

            if (!isNaN(lat) && !isNaN(lon)) {
                // Calculate an approximate bounding box (roughly 500-1000m wide)
                const offset = 0.005; // degree offset
                const minLon = lon - offset;
                const minLat = lat - offset;
                const maxLon = lon + offset;
                const maxLat = lat + offset;

                // ArcGIS REST MapServer Export API
                // bbox format: minX,minY,maxX,maxY (lon,lat,lon,lat)
                const bbox = `${minLon},${minLat},${maxLon},${maxLat}`;
                const mapUrl = `https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/export?bbox=${bbox}&bboxSR=4326&size=800,600&imageSR=102100&format=jpg&f=image`;

                dashboardHeatmap.style.backgroundImage = `url('${mapUrl}')`;
                dashboardHeatmap.style.backgroundSize = 'cover';
                dashboardHeatmap.style.backgroundPosition = 'center';
            }
        }

        if (dashboardFieldText) {
            dashboardFieldText.innerText = `Scanned: ${locString}`;
        }
    }

    useLocationBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser.');
            return;
        }

        useLocationBtn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> Locating...';
        useLocationBtn.disabled = true;

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude.toFixed(5);
                const lon = position.coords.longitude.toFixed(5);
                const coordsString = `${lat}, ${lon}`;

                // Update input and display areas
                coordsInput.value = coordsString;
                coordsText.innerText = coordsString;
                locationDisplay.classList.remove('hidden');

                // Update Background Heatmap
                updateDashboardHeatmap(coordsString);

                // Reset button
                useLocationBtn.innerHTML = '<i class="ri-focus-3-line"></i> Use Current Location';
                useLocationBtn.disabled = false;
            },
            (error) => {
                console.error("Geolocation error:", error);
                alert('Unable to retrieve your location. Please ensure location services are enabled.');
                // Reset button
                useLocationBtn.innerHTML = '<i class="ri-focus-3-line"></i> Use Current Location';
                useLocationBtn.disabled = false;
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    });

    // Also update display if user manually types coordinates
    // We'll use a short debounce so we don't rapid-fire image requests
    let typingTimer;
    coordsInput.addEventListener('input', (e) => {
        clearTimeout(typingTimer);

        if (e.target.value.trim().length > 0) {
            coordsText.innerText = e.target.value;
            locationDisplay.classList.remove('hidden');

            typingTimer = setTimeout(() => {
                updateDashboardHeatmap(e.target.value);
            }, 800);
        } else {
            locationDisplay.classList.add('hidden');
        }
    });
}

// ==========================================
// 6. Time Series Portal Logic
// ==========================================
let timeSeriesChartInstance = null;
function initTimeSeries() {
    const syncBtn = document.getElementById('timeSeriesSyncBtn');
    if (syncBtn) {
        syncBtn.addEventListener('click', fetchTimeSeriesData);
    }
    
    // Fetch data when navigating to the tab for the first time
    const navBtn = document.getElementById('navTimeSeries');
    if (navBtn) {
        navBtn.addEventListener('click', () => {
             if (!timeSeriesChartInstance) {
                 fetchTimeSeriesData();
             }
        });
    }
}

async function fetchTimeSeriesData() {
    try {
        const syncBtn = document.getElementById('timeSeriesSyncBtn');
        if (syncBtn) {
            syncBtn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> Loading...';
            syncBtn.disabled = true;
        }

        const response = await fetch('/api/time_series_data');
        if (!response.ok) throw new Error("Failed to fetch time series data");
        const data = await response.json();
        
        renderTimeSeriesChart(data);

        if (syncBtn) {
            syncBtn.innerHTML = '<i class="ri-refresh-line"></i> Refresh Data';
            syncBtn.disabled = false;
        }
    } catch (error) {
        console.error("Error fetching time series data:", error);
        alert("Failed to load time series data.");
        const syncBtn = document.getElementById('timeSeriesSyncBtn');
        if (syncBtn) {
            syncBtn.innerHTML = '<i class="ri-refresh-line"></i> Refresh Data';
            syncBtn.disabled = false;
        }
    }
}

function renderTimeSeriesChart(data) {
    const ctx = document.getElementById('timeSeriesChart');
    if (!ctx) return;

    if (timeSeriesChartInstance) {
        timeSeriesChartInstance.destroy();
    }
    
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#f8fafc' : '#1e293b';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

    // Astrava Colors for different crops
    const colors = {
        'Rice': { border: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' },    // Emerald
        'Cotton': { border: '#3b82f6', bg: 'rgba(59, 130, 246, 0.1)' }, // Blue
        'Tomato': { border: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' },  // Red
        'Wheat': { border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' }   // Amber
    };
    
    // Default fallback color
    const defaultColor = { border: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.1)' };

    const chartDatasets = data.datasets.map(ds => {
        const theme = colors[ds.label] || defaultColor;
        return {
            label: `${ds.label} Health`,
            data: ds.data,
            borderColor: theme.border,
            backgroundColor: theme.bg,
            borderWidth: 3,
            tension: 0.4,
            fill: false, 
            pointBackgroundColor: theme.border,
            pointRadius: 3,
            pointHoverRadius: 6
        };
    });

    timeSeriesChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: chartDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { 
                        color: textColor, 
                        font: { family: 'Outfit, sans-serif', size: 13 },
                        usePointStyle: true,
                        boxWidth: 8
                    }
                },
                tooltip: {
                    backgroundColor: isDark ? 'rgba(30, 41, 59, 0.95)' : 'rgba(255,255,255,0.95)',
                    titleColor: isDark ? '#f8fafc' : '#0f172a',
                    bodyColor: isDark ? '#cbd5e1' : '#334155',
                    borderColor: gridColor,
                    borderWidth: 1,
                    padding: 12,
                    boxPadding: 6,
                    usePointStyle: true,
                    callbacks: {
                        label: function(context) {
                            return ` ${context.dataset.label}: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor, drawBorder: false },
                    ticks: { color: textColor, font: { family: 'Outfit, sans-serif' }, maxTicksLimit: 15 },
                    title: { display: false }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: gridColor, borderDash: [5, 5], drawBorder: false },
                    ticks: { 
                        color: textColor, 
                        font: { family: 'Outfit, sans-serif' },
                        callback: function(value) { return value + '%'; }
                    },
                    title: { display: true, text: 'Overall Health Rate (%)', color: textColor, font: { size: 13 } }
                }
            }
        }
    });
}