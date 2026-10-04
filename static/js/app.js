const app = {
  state: {
    currentFile: null,
    currentObsId: null,
    observations: [],
    map: null,
    markers: []
  },

  init() {
    this.checkStatus();
    this.setupEventListeners();
    this.loadObservations();
    
    // Check hash for page routing
    if (window.location.hash) {
      const page = window.location.hash.substring(1);
      if (['home', 'assess', 'dashboard', 'architecture'].includes(page)) {
        this.showPage(page);
      }
    }
  },

  async checkStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      // Status check complete, keeping UI clean and professional
    } catch (e) {
      console.warn('Backend not running or status check failed.', e);
    }
  },

  setupEventListeners() {
    // Nav links
    document.querySelectorAll('.nav-link').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.showPage(e.target.dataset.target);
      });
    });

    // File upload
    const dropZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('image-input');
    
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', e => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
      if (e.dataTransfer.files.length) this.handleImageSelect(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', e => {
      if (e.target.files.length) this.handleImageSelect(e.target.files[0]);
    });

    // Observation chips
    document.querySelectorAll('.obs-chip input').forEach(input => {
      input.addEventListener('change', (e) => {
        const chip = e.target.closest('.obs-chip');
        chip.classList.toggle('selected', e.target.checked);
      });
    });

    // Review options
    document.querySelectorAll('.review-option').forEach(opt => {
      opt.addEventListener('click', () => {
        document.querySelectorAll('.review-option').forEach(o => {
          o.classList.remove('selected-confirm', 'selected-test', 'selected-dismiss');
        });
        const val = opt.querySelector('input').value;
        if (val === 'CONFIRMED') opt.classList.add('selected-confirm');
        if (val === 'REQUIRES_TESTING') opt.classList.add('selected-test');
        if (val === 'DISMISSED') opt.classList.add('selected-dismiss');
      });
    });
  },

  showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    
    document.getElementById(`page-${pageId}`).classList.add('active');
    const link = document.querySelector(`.nav-link[data-target="${pageId}"]`);
    if (link) link.classList.add('active');
    
    window.location.hash = pageId;

    if (pageId === 'dashboard') {
      setTimeout(() => this.initMap(), 100);
      this.loadObservations();
    }
  },

  // Assessment Flow
  nextStep(step) {
    document.querySelectorAll('.step-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`panel-${step}`).classList.add('active');
    
    document.getElementById(`indicator-${step}`).classList.add('active');
    document.getElementById(`indicator-${step - 1}`).classList.add('done');
    document.getElementById(`indicator-${step - 1}`).classList.remove('active');
  },

  prevStep(step) {
    document.querySelectorAll('.step-panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`panel-${step}`).classList.add('active');
    
    document.getElementById(`indicator-${step}`).classList.add('active');
    document.getElementById(`indicator-${step}`).classList.remove('done');
    document.getElementById(`indicator-${step + 1}`).classList.remove('active');
  },

  handleImageSelect(file) {
    if (!file.type.match('image.*')) {
      this.showToast('Please select an image file', 'error');
      return;
    }
    
    this.state.currentFile = file;
    const reader = new FileReader();
    reader.onload = e => {
      document.getElementById('image-preview').src = e.target.result;
      document.getElementById('upload-zone').style.display = 'none';
      document.getElementById('image-preview-container').style.display = 'block';
      document.getElementById('btn-next-1').disabled = false;
    };
    reader.readAsDataURL(file);
  },

  async runAnalysis() {
    this.nextStep(3);
    document.getElementById('analysis-loader').classList.add('active');
    document.getElementById('result-container').classList.remove('active');
    
    const steps = document.querySelectorAll('.loader-step');
    let stepIdx = 0;
    const intId = setInterval(() => {
      if (stepIdx > 0) {
        steps[stepIdx-1].classList.remove('active');
        steps[stepIdx-1].classList.add('done');
        steps[stepIdx-1].querySelector('.loader-step-icon').textContent = '✓';
      }
      if (stepIdx < steps.length) {
        steps[stepIdx].classList.add('active');
      }
      stepIdx++;
      if (stepIdx > steps.length) clearInterval(intId);
    }, 1000);

    const formData = new FormData();
    formData.append('image', this.state.currentFile);
    formData.append('water_body', document.getElementById('input-water-body').value);
    formData.append('location_name', document.getElementById('input-location').value);
    
    const selectedObs = Array.from(document.querySelectorAll('.obs-chip input:checked')).map(i => i.value);
    formData.append('citizen_observations', JSON.stringify(selectedObs));

    try {
      const res = await fetch('/api/assess', { method: 'POST', body: formData });
      const data = await res.json();
      
      clearInterval(intId);
      steps.forEach(s => {
        s.classList.remove('active');
        s.classList.add('done');
        s.querySelector('.loader-step-icon').textContent = '✓';
      });

      setTimeout(() => {
        document.getElementById('analysis-loader').classList.remove('active');
        this.renderAssessmentResult(data);
      }, 800);

    } catch (e) {
      clearInterval(intId);
      this.showToast('Analysis failed. Please try again.', 'error');
      this.prevStep(2);
    }
  },

  renderAssessmentResult(data) {
    const { observation_id, assessment, validation, observation } = data;
    this.state.currentObsId = observation_id;
    
    const container = document.getElementById('result-container');
    
    // Generate evidence list HTML
    const evidenceHtml = assessment.visible_evidence.map(e => 
      `<li class="evidence-item"><div class="evidence-dot"></div>${e}</li>`
    ).join('');
    
    // Generate validation HTML
    let validationHtml = '';
    if (validation.mismatch_detected) {
      validationHtml += `
        <div class="mismatch-alert">
          <h3>Observation Mismatch Detected</h3>
          <p>${validation.mismatch_note}</p>
        </div>
      `;
    } else {
      validationHtml += `
        <div class="all-clear-alert">
          <span>✓</span>
          <strong>All citizen observations verified by AI.</strong>
        </div>
      `;
    }

    const matches = validation.matched.map(m => `<div class="val-item match">✓ ${m}</div>`).join('');
    const mismatches = validation.mismatched.map(m => `<div class="val-item mismatch">✕ ${m} (Not verified)</div>`).join('');
    const notFound = observation.citizen_observations.length === 0 ? '<div class="val-item neutral">No specific observations provided</div>' : '';

    const html = `
      <div class="result-header">
        <div class="result-header-top">
          <div class="result-title-area">
            <h2>AI-Supported Ecosystem Assessment</h2>
            <p>Analysis Complete</p>
          </div>
          <div class="risk-badge ${assessment.risk_level}">
            Risk Level: ${assessment.risk_level}
          </div>
        </div>
        
        <div class="result-metrics">
          <div class="metric-card">
            <div class="metric-value">${assessment.ai_confidence.toFixed(1)}%</div>
            <div class="metric-label">AI Confidence</div>
          </div>
          <div class="metric-card">
            <div class="metric-value" style="color: var(--risk-low);">${assessment.visually_safe.toFixed(1)}%</div>
            <div class="metric-label">Safe Indicators</div>
          </div>
          <div class="metric-card">
            <div class="metric-value" style="color: var(--risk-high);">${assessment.visually_risky.toFixed(1)}%</div>
            <div class="metric-label">Risk Indicators</div>
          </div>
        </div>
      </div>

      <div class="result-card">
        <div class="card-title"><span>👁️</span> Visible Evidence</div>
        <p style="font-size: 15px; color: var(--text-primary); margin-bottom: 16px;">${assessment.description}</p>
        <ul class="evidence-list">
          ${evidenceHtml}
        </ul>
      </div>

      <div class="result-card">
        <div class="card-title"><span>⚖️</span> Citizen vs AI Validation</div>
        ${validationHtml}
        <div class="validation-grid">
          <div class="validation-col">
            <h3>Citizen Reported</h3>
            ${observation.citizen_observations.map(o => `<div class="val-item neutral">${o}</div>`).join('') || '<div class="val-item neutral">None selected</div>'}
          </div>
          <div class="validation-col">
            <h3>AI Verified</h3>
            ${matches}
            ${mismatches}
            ${!matches && !mismatches ? notFound : ''}
          </div>
        </div>
      </div>

      <div class="result-card">
        <div class="card-title"><span>🧠</span> How AI Reached This Assessment</div>
        <div class="explanation-text" style="margin-bottom: 20px;">
          ${assessment.reasoning}
        </div>
        <div class="uncertainty-box">
          <strong>Important Limitation:</strong> ${assessment.uncertainty_note}
        </div>
      </div>

      <div class="result-card">
        <div class="card-title"><span>🌱</span> One Health Insights</div>
        <div class="one-health-grid">
          <div class="one-health-card">
            <div class="oh-icon">🌿</div>
            <div class="oh-label">Ecosystem</div>
            <div class="oh-title">Environmental Impact</div>
            <div class="oh-text">${assessment.ecosystem_insight}</div>
          </div>
          <div class="one-health-card">
            <div class="oh-icon">🐟</div>
            <div class="oh-label">Aquatic Life</div>
            <div class="oh-title">Biodiversity</div>
            <div class="oh-text">${assessment.aquatic_life_note}</div>
          </div>
          <div class="one-health-card">
            <div class="oh-icon">👥</div>
            <div class="oh-label">Human Health</div>
            <div class="oh-title">Well-being</div>
            <div class="oh-text">${assessment.human_wellbeing_note}</div>
          </div>
        </div>
        
        <div style="background: rgba(0,168,255,0.1); border-radius: 8px; padding: 16px; margin-bottom: 24px;">
          <strong>Recommended Action:</strong> ${assessment.recommended_action}
        </div>
      </div>

      <div style="display: flex; gap: 16px; margin-top: 32px;">
        <button class="btn-secondary" style="flex: 1;" onclick="app.resetAssessment()">New Assessment</button>
        <button class="btn-primary" style="flex: 2;" onclick="app.openReviewModal('${observation_id}')">Send to Human Verification</button>
      </div>
    `;
    
    container.innerHTML = html;
    container.classList.add('active');
  },

  resetAssessment() {
    this.state.currentFile = null;
    this.state.currentObsId = null;
    document.getElementById('image-input').value = '';
    document.getElementById('upload-zone').style.display = 'block';
    document.getElementById('image-preview-container').style.display = 'none';
    document.getElementById('btn-next-1').disabled = true;
    
    document.getElementById('input-location').value = '';
    document.getElementById('input-water-body').value = 'stream';
    document.querySelectorAll('.obs-chip input').forEach(i => {
      i.checked = false;
      i.parentElement.classList.remove('selected');
    });
    
    this.nextStep(1);
  },

  // Dashboard & Map
  async loadObservations() {
    try {
      const res = await fetch('/api/observations');
      const data = await res.json();
      this.state.observations = data.observations;
      this.updateDashboard();
    } catch (e) {
      console.warn("Could not load observations");
    }
  },

  updateDashboard() {
    const obs = this.state.observations;
    
    // Stats
    document.getElementById('stat-total').textContent = obs.length;
    document.getElementById('stat-ai').textContent = obs.length;
    document.getElementById('stat-verify').textContent = obs.filter(o => o.reviewer_status === 'AWAITING_VERIFICATION').length;
    document.getElementById('stat-elevated').textContent = obs.filter(o => ['ELEVATED', 'HIGH'].includes(o.assessment.risk_level)).length;

    // Pattern detection (simple simulation for hackathon demo)
    const elevated = obs.filter(o => ['ELEVATED', 'HIGH'].includes(o.assessment.risk_level));
    if (elevated.length >= 2) {
      document.getElementById('pattern-alert').style.display = 'flex';
    }

    // List
    const list = document.getElementById('obs-list');
    list.innerHTML = obs.slice().reverse().map(o => {
      const riskColors = { 'LOW': 'var(--risk-low)', 'MODERATE': 'var(--risk-moderate)', 'ELEVATED': 'var(--risk-elevated)', 'HIGH': 'var(--risk-high)' };
      const statusLabels = { 'CONFIRMED': 'Confirmed', 'AWAITING_VERIFICATION': 'Needs Review', 'REQUIRES_TESTING': 'Field Test Required', 'DISMISSED': 'Dismissed', 'AI_SCREENED': 'AI Screened' };
      
      const date = new Date(o.timestamp).toLocaleDateString(undefined, {month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'});
      
      return `
        <div class="obs-item" onclick="app.showObservationDetails('${o.id}')">
          <div class="obs-risk-dot" style="background: ${riskColors[o.assessment.risk_level] || 'gray'}"></div>
          <div class="obs-info">
            <div class="obs-location">${o.location}</div>
            <div class="obs-meta">${date} • ${o.assessment.ai_confidence.toFixed(0)}% AI Conf.</div>
          </div>
          <div class="obs-status-badge ${o.reviewer_status || 'AI_SCREENED'}">
            ${statusLabels[o.reviewer_status] || 'AI Screened'}
          </div>
        </div>
      `;
    }).join('');

    // Update map markers if map exists
    if (this.state.map) {
      this.state.markers.forEach(m => this.state.map.removeLayer(m));
      this.state.markers = [];
      
      obs.forEach(o => {
        if (o.lat && o.lng) {
          const colors = { 'LOW': '#00d4aa', 'MODERATE': '#f5c518', 'ELEVATED': '#ff8c00', 'HIGH': '#ff3b5c' };
          const color = colors[o.assessment.risk_level] || '#00a8ff';
          
          const markerHtml = `
            <div style="background:${color}; width:16px; height:16px; border-radius:50%; border:2px solid white; box-shadow:0 2px 4px rgba(0,0,0,0.3);"></div>
          `;
          
          const icon = L.divIcon({ html: markerHtml, className: '', iconSize: [16, 16], iconAnchor: [8, 8] });
          const marker = L.marker([o.lat, o.lng], { icon }).addTo(this.state.map);
          
          marker.bindPopup(`
            <div style="font-family:Inter,sans-serif;">
              <strong>${o.location}</strong><br>
              Risk: ${o.assessment.risk_level}<br>
              Status: ${o.reviewer_status.replace('_', ' ')}
            </div>
          `);
          
          this.state.markers.push(marker);
        }
      });
    }
  },

  initMap() {
    if (this.state.map || !document.getElementById('leaflet-map')) return;
    
    // Default to Islamabad region for demo
    this.state.map = L.map('leaflet-map').setView([33.68, 73.04], 11);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19
    }).addTo(this.state.map);
    
    // Re-render markers if map just initialized
    this.updateDashboard();
  },

  showObservationDetails(id) {
    const obs = this.state.observations.find(o => o.id === id);
    if (!obs) return;
    
    this.renderAssessmentResult({
      observation_id: id,
      assessment: obs.assessment,
      validation: obs.validation,
      observation: obs
    });
    
    this.showPage('assess');
    this.nextStep(3);
  },

  // Review Modal
  openReviewModal(obsId) {
    this.state.currentObsId = obsId;
    document.querySelectorAll('.review-option').forEach(o => {
      o.classList.remove('selected-confirm', 'selected-test', 'selected-dismiss');
      o.querySelector('input').checked = false;
    });
    document.getElementById('review-notes').value = '';
    document.getElementById('review-modal').classList.add('active');
  },

  closeReviewModal() {
    document.getElementById('review-modal').classList.remove('active');
  },

  async submitReview() {
    const selected = document.querySelector('input[name="review_decision"]:checked');
    if (!selected) {
      this.showToast('Please select a verification decision.', 'error');
      return;
    }
    
    const decision = selected.value;
    const notes = document.getElementById('review-notes').value;
    
    try {
      const res = await fetch(`/api/observations/${this.state.currentObsId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: decision, notes: notes })
      });
      
      if (res.ok) {
        this.closeReviewModal();
        this.showToast('Human verification saved.', 'success');
        this.loadObservations(); // Refresh data
        
        // Return to dashboard
        setTimeout(() => this.showPage('dashboard'), 1500);
      }
    } catch (e) {
      this.showToast('Failed to save review.', 'error');
    }
  },

  // UI Utilities
  showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.className = `toast active ${type}`;
    toast.querySelector('.icon').textContent = type === 'success' ? '✓' : '⚠️';
    toast.querySelector('.text').textContent = message;
    
    setTimeout(() => {
      toast.classList.remove('active');
    }, 4000);
  }
};

document.addEventListener('DOMContentLoaded', () => app.init());
