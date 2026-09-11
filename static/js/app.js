/**
 * TalentAI ATS - Frontend Application Controller
 * Pure Vanilla JavaScript (ES6+)
 */

// Global Application State
const AppState = {
    candidates: [],
    jobDescription: null,
    stats: {
        total_candidates: 0,
        screened_candidates: 0,
        top_match_score: 0,
        avg_match_score: 0,
        shortlisted_count: 0
    },
    activeCandidateId: null,
    isUploading: false
};

// ==========================================================================
// 1. INITIALIZATION & THEME MANAGEMENT
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initEventListeners();
    fetchInitialData();
});

function initTheme() {
    const savedTheme = localStorage.getItem('talentai_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('talentai_theme', newTheme);
    showToast(`Switched to ${newTheme.toUpperCase()} theme`, 'info');
}

// ==========================================================================
// 2. TOAST NOTIFICATIONS SYSTEM
// ==========================================================================

function showToast(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconSvg = '';
    if (type === 'success') {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><path d="M20 6L9 17l-5-5"></path></svg>`;
    } else if (type === 'error') {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
    } else if (type === 'warning') {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
    } else {
        iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366f1" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }

    toast.innerHTML = `
        ${iconSvg}
        <span class="toast-msg">${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ==========================================================================
// 3. DATA FETCHING & STATE SYNC
// ==========================================================================

async function fetchInitialData() {
    try {
        const response = await fetch('/api/candidates');
        const data = await response.json();
        if (data.success) {
            AppState.candidates = data.candidates || [];
            AppState.jobDescription = data.job_description || null;
            AppState.stats = data.stats || AppState.stats;
            
            updateTopbar();
            updateDashboardStats();
            
            if (document.getElementById('candidates-tbody')) {
                renderCandidatesTable();
            }
        }
    } catch (err) {
        console.error('Failed to fetch initial ATS data:', err);
    }
}

function updateTopbar() {
    const jobTitleEl = document.getElementById('topbar-job-title');
    if (jobTitleEl) {
        jobTitleEl.textContent = AppState.jobDescription && AppState.jobDescription.title 
            ? AppState.jobDescription.title 
            : 'No Job Description Configured';
    }

    const navCountEl = document.getElementById('nav-candidate-count');
    if (navCountEl) {
        navCountEl.textContent = AppState.candidates.length;
    }
}

function updateDashboardStats() {
    const s = AppState.stats;
    const totalEl = document.getElementById('stat-total-candidates');
    const screenedEl = document.getElementById('stat-screened-candidates');
    const topEl = document.getElementById('stat-top-match');
    const avgEl = document.getElementById('stat-avg-score');
    const shortEl = document.getElementById('stat-shortlisted');

    if (totalEl) totalEl.textContent = s.total_candidates;
    if (screenedEl) screenedEl.textContent = s.screened_candidates;
    if (topEl) topEl.textContent = `${s.top_match_score}%`;
    if (avgEl) avgEl.textContent = `${s.avg_match_score}%`;
    if (shortEl) shortEl.textContent = s.shortlisted_count;

    const queuedCount = document.getElementById('queued-count');
    if (queuedCount) queuedCount.textContent = AppState.candidates.length;
}

// ==========================================================================
// 4. EVENT LISTENERS SETUP
// ==========================================================================

function initEventListeners() {
    // Theme Toggle
    const themeBtn = document.getElementById('btn-theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    // Sidebar Toggle
    const sidebarToggle = document.getElementById('btn-toggle-sidebar');
    const sidebar = document.getElementById('sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Intelligence & Safeguards Modals
    setupModal('btn-show-weights', 'weights-modal', 'modal-close-weights', 'btn-close-weights-footer');
    setupModal('btn-show-fairness', 'fairness-modal', 'modal-close-fairness', 'btn-close-fairness-footer');
    
    // Candidate Details Modal Close
    const closeCandModalBtn = document.getElementById('modal-close-candidate');
    const candModal = document.getElementById('candidate-modal');
    if (closeCandModalBtn && candModal) {
        closeCandModalBtn.addEventListener('click', () => candModal.classList.remove('show'));
        candModal.addEventListener('click', (e) => {
            if (e.target === candModal) candModal.classList.remove('show');
        });
    }

    // Sample JD selector
    const sampleJdSelect = document.getElementById('select-sample-jd');
    if (sampleJdSelect) {
        sampleJdSelect.addEventListener('change', handleSampleJdSelect);
    }

    // JD File Upload
    const jdFileInput = document.getElementById('jd-file-upload');
    if (jdFileInput) {
        jdFileInput.addEventListener('change', handleJdFileUpload);
    }

    // Dropzone & File Browse
    const dropzone = document.getElementById('resume-dropzone');
    const fileInput = document.getElementById('resume-file-input');
    const browseBtn = document.getElementById('btn-browse-files');

    if (dropzone && fileInput) {
        if (browseBtn) browseBtn.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('click', (e) => {
            if (e.target !== browseBtn) fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                handleFileUpload(e.target.files);
            }
        });

        // Drag events
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('drag-over');
            });
        });

        dropzone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                handleFileUpload(files);
            }
        });
    }

    // Main Ranking Execution Buttons
    const rankBtnMain = document.getElementById('btn-analyze-main');
    const startRankBtn = document.getElementById('btn-start-ranking');
    if (rankBtnMain) rankBtnMain.addEventListener('click', executeScreening);
    if (startRankBtn) startRankBtn.addEventListener('click', executeScreening);

    // Load Demo Data Buttons
    const loadDemoTopbar = document.getElementById('btn-load-demo-topbar');
    if (loadDemoTopbar) loadDemoTopbar.addEventListener('click', loadDemoData);

    // Clear / Reset Session Button
    const resetBtn = document.getElementById('btn-reset-session');
    if (resetBtn) resetBtn.addEventListener('click', confirmResetSession);

    const clearQueueBtn = document.getElementById('btn-clear-queue');
    if (clearQueueBtn) clearQueueBtn.addEventListener('click', confirmResetSession);

    // Filter toolbar events in results page
    setupFilterEvents();

    // Modal Recruiter Actions
    setupModalRecruiterActions();
}

function setupModal(triggerId, modalId, closeBtnId, footerCloseBtnId) {
    const trigger = document.getElementById(triggerId);
    const modal = document.getElementById(modalId);
    const closeBtn = document.getElementById(closeBtnId);
    const footerCloseBtn = document.getElementById(footerCloseBtnId);

    if (trigger && modal) {
        trigger.addEventListener('click', () => modal.classList.add('show'));
    }
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => modal.classList.remove('show'));
    }
    if (footerCloseBtn && modal) {
        footerCloseBtn.addEventListener('click', () => modal.classList.remove('show'));
    }
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('show');
        });
    }
}

// ==========================================================================
// 5. JOB DESCRIPTION HANDLING
// ==========================================================================

async function handleSampleJdSelect(e) {
    const selectedKey = e.target.value;
    if (!selectedKey) return;

    try {
        const response = await fetch('/api/sample-jds');
        const data = await response.json();
        if (data.success && data.samples) {
            const sample = data.samples.find(s => s.filename.includes(selectedKey));
            if (sample) {
                const jdTextEl = document.getElementById('jd-text-input');
                const jdTitleEl = document.getElementById('jd-role-title');
                if (jdTextEl) jdTextEl.value = sample.content;
                if (jdTitleEl) jdTitleEl.value = sample.title;
                showToast(`Loaded sample JD: ${sample.title}`, 'info');
            }
        }
    } catch (err) {
        showToast('Failed to load sample JD', 'error');
    }
}

function handleJdFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        const content = event.target.result;
        const jdTextEl = document.getElementById('jd-text-input');
        if (jdTextEl) {
            jdTextEl.value = content;
            showToast(`Loaded JD from file: ${file.name}`, 'success');
        }
    };
    reader.readAsText(file);
}

// ==========================================================================
// 6. RESUME FILE UPLOAD & BULK PROGRESS
// ==========================================================================

async function handleFileUpload(fileList) {
    const files = Array.from(fileList);
    if (files.length === 0) return;

    const validExtensions = ['pdf', 'docx', 'doc', 'txt'];
    const validFiles = files.filter(file => {
        const ext = file.name.split('.').pop().toLowerCase();
        return validExtensions.includes(ext);
    });

    if (validFiles.length === 0) {
        showToast('Please select valid resume files (.PDF, .DOCX, .TXT)', 'error');
        return;
    }

    const formData = new FormData();
    validFiles.forEach(file => formData.append('files', file));

    // Show Progress Bar
    const progressCard = document.getElementById('upload-progress-container');
    const fillBar = document.getElementById('progress-fill-bar');
    const statusText = document.getElementById('progress-status-text');
    const percentText = document.getElementById('progress-percent-text');
    const countText = document.getElementById('progress-count-text');

    if (progressCard) {
        progressCard.style.display = 'block';
        fillBar.style.width = '20%';
        percentText.textContent = '20%';
        statusText.textContent = 'Uploading & parsing resumes...';
        countText.textContent = `0 / ${validFiles.length} resumes processed`;
    }

    try {
        // Animate progress slightly for realism during parsing
        setTimeout(() => { if (fillBar) { fillBar.style.width = '60%'; percentText.textContent = '60%'; } }, 400);

        const response = await fetch('/api/upload-resumes', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (fillBar) { fillBar.style.width = '100%'; percentText.textContent = '100%'; }

        if (data.success) {
            showToast(data.message, 'success');
            await fetchInitialData();
            renderQueuedFilesList();
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
    } catch (err) {
        showToast('An error occurred during upload', 'error');
    } finally {
        setTimeout(() => {
            if (progressCard) progressCard.style.display = 'none';
        }, 1200);
    }
}

function renderQueuedFilesList() {
    const container = document.getElementById('queued-files-list');
    if (!container) return;

    if (AppState.candidates.length === 0) {
        container.innerHTML = `
            <div class="empty-queue-state">
                <p>No resumes uploaded yet. Drag files into the box above or load demo candidates to get started.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = AppState.candidates.map(cand => `
        <div class="queue-item" data-id="${cand.id}">
            <div class="queue-item-left">
                <span class="file-type-badge ${cand.file_type}">${cand.file_type.toUpperCase()}</span>
                <div class="queue-file-info">
                    <span class="queue-filename">${cand.filename}</span>
                    <span class="queue-meta">${cand.name} &bull; ${cand.skills.length} skills detected</span>
                </div>
            </div>
            <div class="queue-item-right">
                ${cand.score_breakdown && cand.score_breakdown.overall_score > 0 ? `
                    <span class="score-badge mini ${cand.score_breakdown.overall_score >= 80 ? 'score-high' : (cand.score_breakdown.overall_score >= 60 ? 'score-mid' : 'score-low')}">
                        ${cand.score_breakdown.overall_score}%
                    </span>
                ` : ''}
                <button type="button" class="btn-inspect-queue" onclick="openCandidateModal('${cand.id}')" title="Inspect Candidate Profile">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                </button>
            </div>
        </div>
    `).join('');
}

// ==========================================================================
// 7. SCREENING & RANKING EXECUTION
// ==========================================================================

async function executeScreening() {
    const jdTextEl = document.getElementById('jd-text-input');
    const jdTitleEl = document.getElementById('jd-role-title');
    const jdText = jdTextEl ? jdTextEl.value.trim() : '';
    const jdTitle = jdTitleEl ? jdTitleEl.value.trim() : '';

    if (!jdText && (!AppState.jobDescription || !AppState.jobDescription.raw_text)) {
        showToast('Please enter or upload a Job Description to rank candidates', 'warning');
        if (jdTextEl) jdTextEl.focus();
        return;
    }

    if (AppState.candidates.length === 0) {
        showToast('Please upload at least one candidate resume or click "Load Demo Data"', 'warning');
        return;
    }

    showToast('Running NLP screening & candidate ranking...', 'info');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jd_text: jdText,
                jd_title: jdTitle
            })
        });

        const data = await response.json();
        if (data.success) {
            AppState.candidates = data.candidates || [];
            AppState.jobDescription = data.job_description || null;
            AppState.stats = data.stats || AppState.stats;

            showToast(data.message, 'success');
            updateTopbar();
            updateDashboardStats();

            // If we are currently on dashboard, redirect to results view after screening
            if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
                window.location.href = '/results';
            } else {
                renderCandidatesTable();
            }
        } else {
            showToast(data.error || 'Screening failed', 'error');
        }
    } catch (err) {
        showToast('An error occurred during candidate screening', 'error');
    }
}

// ==========================================================================
// 8. 1-CLICK DEMO DATA LOADER
// ==========================================================================

async function loadDemoData() {
    showToast('Loading sample job description and candidate resumes...', 'info');
    try {
        const response = await fetch('/api/load-sample', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jd_type: 'senior_fullstack_engineer' })
        });
        const data = await response.json();

        if (data.success) {
            AppState.candidates = data.candidates || [];
            AppState.jobDescription = data.job_description || null;
            AppState.stats = data.stats || AppState.stats;

            showToast('Demo dataset loaded & ranked successfully!', 'success');
            updateTopbar();
            updateDashboardStats();

            // If on dashboard, update textareas and queue
            const jdTextEl = document.getElementById('jd-text-input');
            const jdTitleEl = document.getElementById('jd-role-title');
            if (jdTextEl && AppState.jobDescription) jdTextEl.value = AppState.jobDescription.raw_text;
            if (jdTitleEl && AppState.jobDescription) jdTitleEl.value = AppState.jobDescription.title;

            renderQueuedFilesList();

            if (document.getElementById('candidates-tbody')) {
                renderCandidatesTable();
            }
        }
    } catch (err) {
        showToast('Failed to load demo data', 'error');
    }
}

async function confirmResetSession() {
    if (!confirm('Are you sure you want to clear all uploaded resumes and job description state?')) {
        return;
    }

    try {
        const response = await fetch('/api/reset', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            AppState.candidates = [];
            AppState.jobDescription = null;
            AppState.stats = data.stats;

            showToast('Session reset successfully', 'info');
            updateTopbar();
            updateDashboardStats();
            renderQueuedFilesList();

            const jdTextEl = document.getElementById('jd-text-input');
            const jdTitleEl = document.getElementById('jd-role-title');
            if (jdTextEl) jdTextEl.value = '';
            if (jdTitleEl) jdTitleEl.value = '';

            if (document.getElementById('candidates-tbody')) {
                renderCandidatesTable();
            }
        }
    } catch (err) {
        showToast('Failed to reset session', 'error');
    }
}

// ==========================================================================
// 9. RESULTS PAGE FILTERING & SORTING
// ==========================================================================

function setupFilterEvents() {
    const searchInput = document.getElementById('filter-search-input');
    const minScoreSlider = document.getElementById('filter-min-score');
    const minScoreBadge = document.getElementById('filter-min-score-val');
    const recSelect = document.getElementById('filter-recommendation');
    const statusSelect = document.getElementById('filter-status');
    const sortSelect = document.getElementById('filter-sort-by');
    const shortlistedOnly = document.getElementById('filter-shortlisted-only');
    const resetFiltersBtn = document.getElementById('btn-reset-filters');

    if (minScoreSlider && minScoreBadge) {
        minScoreSlider.addEventListener('input', (e) => {
            minScoreBadge.textContent = `${e.target.value}%`;
            renderCandidatesTable();
        });
    }

    [searchInput, recSelect, statusSelect, sortSelect, shortlistedOnly].forEach(el => {
        if (el) el.addEventListener('input', renderCandidatesTable);
    });

    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', resetAllFilters);
    }
}

function resetAllFilters() {
    const searchInput = document.getElementById('filter-search-input');
    const minScoreSlider = document.getElementById('filter-min-score');
    const minScoreBadge = document.getElementById('filter-min-score-val');
    const recSelect = document.getElementById('filter-recommendation');
    const statusSelect = document.getElementById('filter-status');
    const sortSelect = document.getElementById('filter-sort-by');
    const shortlistedOnly = document.getElementById('filter-shortlisted-only');

    if (searchInput) searchInput.value = '';
    if (minScoreSlider) minScoreSlider.value = 0;
    if (minScoreBadge) minScoreBadge.textContent = '0%';
    if (recSelect) recSelect.value = 'ALL';
    if (statusSelect) statusSelect.value = 'ALL';
    if (sortSelect) sortSelect.value = 'score_desc';
    if (shortlistedOnly) shortlistedOnly.checked = false;

    renderCandidatesTable();
    showToast('Filters reset', 'info');
}

function getFilteredCandidates() {
    const searchVal = (document.getElementById('filter-search-input')?.value || '').toLowerCase().trim();
    const minScore = parseFloat(document.getElementById('filter-min-score')?.value || '0');
    const recVal = document.getElementById('filter-recommendation')?.value || 'ALL';
    const statusVal = document.getElementById('filter-status')?.value || 'ALL';
    const sortVal = document.getElementById('filter-sort-by')?.value || 'score_desc';
    const shortlistedOnly = document.getElementById('filter-shortlisted-only')?.checked || false;

    let list = [...AppState.candidates];

    // Filter: Search Text (Name, Email, Skills, Location)
    if (searchVal) {
        list = list.filter(c => {
            const nameMatch = c.name.toLowerCase().includes(searchVal);
            const emailMatch = c.email.toLowerCase().includes(searchVal);
            const locationMatch = c.location.toLowerCase().includes(searchVal);
            const skillMatch = c.skills.some(s => s.toLowerCase().includes(searchVal));
            return nameMatch || emailMatch || locationMatch || skillMatch;
        });
    }

    // Filter: Min Score
    if (minScore > 0) {
        list = list.filter(c => (c.score_breakdown?.overall_score || 0) >= minScore);
    }

    // Filter: Recommendation
    if (recVal !== 'ALL') {
        list = list.filter(c => c.recommendation === recVal);
    }

    // Filter: Status
    if (statusVal !== 'ALL') {
        list = list.filter(c => c.status === statusVal);
    }

    // Filter: Shortlisted only
    if (shortlistedOnly) {
        list = list.filter(c => c.is_shortlisted);
    }

    // Sorting
    list.sort((a, b) => {
        const scoreA = a.score_breakdown?.overall_score || 0;
        const scoreB = b.score_breakdown?.overall_score || 0;

        if (sortVal === 'score_desc') return scoreB - scoreA;
        if (sortVal === 'score_asc') return scoreA - scoreB;
        if (sortVal === 'name_asc') return a.name.localeCompare(b.name);
        if (sortVal === 'exp_desc') return (b.total_experience_years || 0) - (a.total_experience_years || 0);
        if (sortVal === 'skills_desc') return b.matched_required_skills.length - a.matched_required_skills.length;
        return 0;
    });

    return list;
}

function renderCandidatesTable() {
    const tbody = document.getElementById('candidates-tbody');
    const emptyState = document.getElementById('empty-results-state');
    const summaryCount = document.getElementById('results-count-summary');

    if (!tbody) return;

    const filtered = getFilteredCandidates();

    if (summaryCount) {
        summaryCount.textContent = `${filtered.length} of ${AppState.candidates.length} candidates displayed`;
    }

    if (filtered.length === 0) {
        tbody.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    if (emptyState) emptyState.style.display = 'none';

    tbody.innerHTML = filtered.map(c => {
        const initials = c.name.split(' ').map(p => p[0]).join('').substring(0, 2).toUpperCase() || 'CV';
        const score = c.score_breakdown?.overall_score || 0;
        const scoreRingHtml = window.ATSCharts ? ATSCharts.renderScoreRing(score, 42) : `${score}%`;

        let recBadgeClass = 'badge-danger';
        if (score >= 85) recBadgeClass = 'badge-success';
        else if (score >= 75) recBadgeClass = 'badge-info';
        else if (score >= 60) recBadgeClass = 'badge-warning';

        return `
            <tr data-id="${c.id}">
                <td>
                    <div class="rank-badge-circle rank-${c.rank}">
                        ${c.rank}
                    </div>
                </td>
                <td>
                    <div class="candidate-cell-flex">
                        <div class="candidate-avatar">${initials}</div>
                        <div class="candidate-cell-info">
                            <span class="cand-name-title">
                                ${c.name}
                                <button type="button" class="shortlist-star-btn ${c.is_shortlisted ? 'active' : ''}" 
                                    onclick="toggleShortlistCandidate('${c.id}', event)" title="Toggle Shortlist">
                                    ${c.is_shortlisted ? '★' : '☆'}
                                </button>
                            </span>
                            <span class="cand-meta-sub">${c.email} &bull; ${c.location}</span>
                        </div>
                    </div>
                </td>
                <td>
                    ${scoreRingHtml}
                </td>
                <td>
                    <div style="font-weight: 700; color: ${c.score_breakdown?.skills_score >= 70 ? 'var(--success)' : 'var(--text-secondary)'};">
                        ${c.score_breakdown?.skills_score || 0}%
                    </div>
                    <small style="color: var(--text-muted); font-size: 11px;">
                        ${c.matched_required_skills.length} matched
                    </small>
                </td>
                <td>
                    <strong>${c.experience_text}</strong>
                </td>
                <td>
                    <span class="badge badge-outline">${c.education_level}</span>
                </td>
                <td>
                    <span style="font-family: var(--font-mono); font-size: 12.5px;">${c.score_breakdown?.similarity_score || 0}%</span>
                </td>
                <td>
                    <span class="badge ${recBadgeClass}">${c.recommendation}</span>
                </td>
                <td>
                    <select class="form-select form-select-sm" onchange="updateCandidateStatus('${c.id}', this.value)" style="width: 110px;">
                        <option value="New" ${c.status === 'New' ? 'selected' : ''}>New</option>
                        <option value="Screening" ${c.status === 'Screening' ? 'selected' : ''}>Screening</option>
                        <option value="Shortlisted" ${c.status === 'Shortlisted' ? 'selected' : ''}>Shortlisted</option>
                        <option value="Interview" ${c.status === 'Interview' ? 'selected' : ''}>Interview</option>
                        <option value="Rejected" ${c.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
                        <option value="Hired" ${c.status === 'Hired' ? 'selected' : ''}>Hired</option>
                    </select>
                </td>
                <td>
                    <button type="button" class="btn btn-secondary btn-sm" onclick="openCandidateModal('${c.id}')">
                        Inspect
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// ==========================================================================
// 10. CANDIDATE DETAILED MODAL INSPECTOR
// ==========================================================================

function openCandidateModal(candidateId) {
    const cand = AppState.candidates.find(c => c.id === candidateId);
    if (!cand) return;

    AppState.activeCandidateId = candidateId;
    const modal = document.getElementById('candidate-modal');
    if (!modal) return;

    // Header info
    const avatarEl = document.getElementById('modal-avatar');
    const nameEl = document.getElementById('modal-candidate-name');
    const metaEl = document.getElementById('modal-candidate-meta');
    const scoreValEl = document.getElementById('modal-overall-score');
    const recLabelEl = document.getElementById('modal-recommendation');

    const initials = cand.name.split(' ').map(p => p[0]).join('').substring(0, 2).toUpperCase() || 'CV';
    if (avatarEl) avatarEl.textContent = initials;
    if (nameEl) nameEl.textContent = cand.name;
    if (metaEl) {
        metaEl.innerHTML = `
            <span>📧 ${cand.email}</span>
            <span>📱 ${cand.phone}</span>
            <span>📍 ${cand.location}</span>
        `;
    }

    const overall = cand.score_breakdown?.overall_score || 0;
    if (scoreValEl) scoreValEl.textContent = `${overall}%`;
    if (recLabelEl) recLabelEl.textContent = cand.recommendation;

    // Score Breakdown Bars
    const bd = cand.score_breakdown || {};
    const breakdownGrid = document.getElementById('modal-score-breakdown');
    if (breakdownGrid && window.ATSCharts) {
        breakdownGrid.innerHTML = `
            ${ATSCharts.renderScoreBar('Technical Skills Match', bd.skills_score, 'Weight: 40%', 'var(--primary)')}
            ${ATSCharts.renderScoreBar('Work Experience Match', bd.experience_score, 'Weight: 25%', '#3b82f6')}
            ${ATSCharts.renderScoreBar('Education Qualification', bd.education_score, 'Weight: 15%', '#8b5cf6')}
            ${ATSCharts.renderScoreBar('Semantic JD Similarity', bd.similarity_score, 'Weight: 10%', '#06b6d4')}
            ${ATSCharts.renderScoreBar('Certifications & Verified Skills', bd.certifications_score, 'Weight: 10%', '#10b981')}
        `;
    }

    // Explainability Lists
    const whyList = document.getElementById('modal-why-ranked');
    const gapsList = document.getElementById('modal-potential-gaps');

    if (whyList) {
        if (cand.why_ranked_highly && cand.why_ranked_highly.length > 0) {
            whyList.innerHTML = cand.why_ranked_highly.map(item => `<li>${item}</li>`).join('');
        } else {
            whyList.innerHTML = `<li>Meets baseline qualification criteria.</li>`;
        }
    }

    if (gapsList) {
        if (cand.potential_gaps && cand.potential_gaps.length > 0) {
            gapsList.innerHTML = cand.potential_gaps.map(item => `<li>${item}</li>`).join('');
        } else {
            gapsList.innerHTML = `<li>No significant gaps or red flags identified.</li>`;
        }
    }

    // Skills Matrix Chips
    const matchedCountEl = document.getElementById('modal-matched-count');
    const missingCountEl = document.getElementById('modal-missing-count');
    const matchedContainer = document.getElementById('modal-matched-skills');
    const missingContainer = document.getElementById('modal-missing-skills');
    const prefContainer = document.getElementById('modal-preferred-skills');
    const allContainer = document.getElementById('modal-all-skills');
    const allCountEl = document.getElementById('modal-all-skills-count');

    if (matchedCountEl) matchedCountEl.textContent = cand.matched_required_skills.length;
    if (missingCountEl) missingCountEl.textContent = cand.missing_required_skills.length;
    if (allCountEl) allCountEl.textContent = cand.skills.length;

    if (matchedContainer) {
        matchedContainer.innerHTML = cand.matched_required_skills.length > 0
            ? cand.matched_required_skills.map(s => `<span class="skill-chip matched">✓ ${s}</span>`).join('')
            : `<span class="text-muted">No required skills matched</span>`;
    }

    if (missingContainer) {
        missingContainer.innerHTML = cand.missing_required_skills.length > 0
            ? cand.missing_required_skills.map(s => `<span class="skill-chip missing">✗ ${s}</span>`).join('')
            : `<span class="text-muted">None - 100% required skills matched!</span>`;
    }

    if (prefContainer) {
        prefContainer.innerHTML = cand.matched_preferred_skills && cand.matched_preferred_skills.length > 0
            ? cand.matched_preferred_skills.map(s => `<span class="skill-chip preferred">★ ${s}</span>`).join('')
            : `<span class="text-muted">No preferred skills matched</span>`;
    }

    if (allContainer) {
        allContainer.innerHTML = cand.skills.map(s => `<span class="skill-chip">${s}</span>`).join('');
    }

    // Experience & Education Details with explicit JD Comparison
    const expSummaryEl = document.getElementById('modal-exp-summary');
    const expTimeline = document.getElementById('modal-exp-timeline');
    const reqExp = AppState.jobDescription?.min_experience_years || 0;
    const candExp = cand.total_experience_years !== null ? `${cand.total_experience_years} yrs` : cand.experience_text;
    
    if (expSummaryEl) {
        expSummaryEl.innerHTML = `${candExp} <small style="color: var(--text-muted); font-size: 11px;">(JD Required: ${reqExp > 0 ? reqExp + '+ yrs' : 'Any'})</small>`;
    }

    if (expTimeline) {
        let expHtml = `
            <div style="background-color: var(--bg-card-alt); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 8px 12px; margin-bottom: 12px; font-size: 12.5px;">
                <span style="color: var(--text-muted);">Candidate Experience:</span> <strong>${candExp}</strong> &bull; 
                <span style="color: var(--text-muted);">Required:</span> <strong>${reqExp > 0 ? reqExp + '+ yrs' : 'None specified'}</strong> &bull; 
                <span style="color: var(--text-muted);">Experience Match:</span> <strong style="color: #3b82f6;">${bd.experience_score || 0}%</strong>
            </div>
        `;
        if (cand.experience_records && cand.experience_records.length > 0) {
            expHtml += cand.experience_records.map(rec => `
                <div class="timeline-item">
                    <span class="timeline-duration">${rec.duration || 'Detected Work Record'}</span>
                    <p class="timeline-details">${rec.detail}</p>
                </div>
            `).join('');
        } else {
            expHtml += `<p class="text-muted">${cand.experience_text}</p>`;
        }
        expTimeline.innerHTML = expHtml;
    }

    const eduBlock = document.getElementById('modal-education-block');
    const reqEdu = AppState.jobDescription?.required_education || "Bachelor's";
    if (eduBlock) {
        eduBlock.innerHTML = `
            <div class="education-item">
                <div style="margin-bottom: 4px;">
                    <span style="color: var(--text-muted);">Candidate Degree:</span> <strong>${cand.education_level}</strong> &bull; 
                    <span style="color: var(--text-muted);">JD Required:</span> <strong>${reqEdu}</strong> &bull;
                    <span style="color: var(--text-muted);">Match:</span> <strong style="color: #8b5cf6;">${bd.education_score || 0}%</strong>
                </div>
                ${cand.education_records && cand.education_records.length > 0 ? `
                    <div style="margin-top: 6px; font-size: 11.5px; color: var(--text-muted); border-top: 1px dashed var(--border-color); padding-top: 4px;">
                        ${cand.education_records.map(e => e.detail).join('<br/>')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    const certsBlock = document.getElementById('modal-certs-block');
    if (certsBlock) {
        if (cand.certifications && cand.certifications.length > 0) {
            certsBlock.innerHTML = `
                <div class="cert-item">
                    <strong>Certifications:</strong> ${cand.certifications.join(', ')}
                </div>
            `;
        } else {
            certsBlock.innerHTML = `<div class="cert-item text-muted">No formal industry certifications detected.</div>`;
        }
    }

    // Recruiter Status & Notes
    const statusSelect = document.getElementById('modal-candidate-status');
    if (statusSelect) statusSelect.value = cand.status || 'New';

    const shortlistStar = document.getElementById('modal-shortlist-star');
    const shortlistText = document.getElementById('modal-shortlist-text');
    if (shortlistStar) shortlistStar.textContent = cand.is_shortlisted ? '★' : '☆';
    if (shortlistText) shortlistText.textContent = cand.is_shortlisted ? 'Shortlisted' : 'Shortlist Candidate';

    const notesTextarea = document.getElementById('modal-candidate-notes');
    if (notesTextarea) notesTextarea.value = cand.notes || '';

    const downloadBtn = document.getElementById('modal-btn-download-resume');
    if (downloadBtn) {
        downloadBtn.href = `/api/candidate/${cand.id}/file?download=0`;
    }

    modal.classList.add('show');
}

// ==========================================================================
// 11. RECRUITER ACTIONS: STATUS, SHORTLIST, NOTES
// ==========================================================================

function setupModalRecruiterActions() {
    const statusSelect = document.getElementById('modal-candidate-status');
    const shortlistBtn = document.getElementById('modal-btn-shortlist');
    const saveNotesBtn = document.getElementById('modal-btn-save-notes');
    const notesTextarea = document.getElementById('modal-candidate-notes');

    if (statusSelect) {
        statusSelect.addEventListener('change', (e) => {
            if (AppState.activeCandidateId) {
                updateCandidateStatus(AppState.activeCandidateId, e.target.value);
            }
        });
    }

    if (shortlistBtn) {
        shortlistBtn.addEventListener('click', () => {
            if (AppState.activeCandidateId) {
                toggleShortlistCandidate(AppState.activeCandidateId);
            }
        });
    }

    if (saveNotesBtn && notesTextarea) {
        saveNotesBtn.addEventListener('click', () => {
            if (AppState.activeCandidateId) {
                saveCandidateNotes(AppState.activeCandidateId, notesTextarea.value);
            }
        });
    }
}

async function toggleShortlistCandidate(candId, event) {
    if (event) event.stopPropagation();

    try {
        const response = await fetch(`/api/candidate/${candId}/shortlist`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            const cand = AppState.candidates.find(c => c.id === candId);
            if (cand) {
                cand.is_shortlisted = data.is_shortlisted;
                cand.status = data.status;
            }
            AppState.stats = data.stats || AppState.stats;
            updateDashboardStats();

            // Update modal state if open
            if (AppState.activeCandidateId === candId) {
                const shortlistStar = document.getElementById('modal-shortlist-star');
                const shortlistText = document.getElementById('modal-shortlist-text');
                const statusSelect = document.getElementById('modal-candidate-status');
                if (shortlistStar) shortlistStar.textContent = data.is_shortlisted ? '★' : '☆';
                if (shortlistText) shortlistText.textContent = data.is_shortlisted ? 'Shortlisted' : 'Shortlist Candidate';
                if (statusSelect) statusSelect.value = data.status;
            }

            renderCandidatesTable();
            showToast(data.is_shortlisted ? 'Candidate added to shortlist' : 'Candidate removed from shortlist', 'info');
        }
    } catch (err) {
        showToast('Failed to update shortlist status', 'error');
    }
}

async function updateCandidateStatus(candId, newStatus) {
    try {
        const response = await fetch(`/api/candidate/${candId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await response.json();
        if (data.success) {
            const cand = AppState.candidates.find(c => c.id === candId);
            if (cand) {
                cand.status = data.status;
                cand.is_shortlisted = data.is_shortlisted;
            }
            renderCandidatesTable();
            showToast(`Status updated to: ${newStatus}`, 'success');
        }
    } catch (err) {
        showToast('Failed to update status', 'error');
    }
}

async function saveCandidateNotes(candId, notesText) {
    const statusLabel = document.getElementById('modal-notes-status');
    if (statusLabel) statusLabel.textContent = 'Saving...';

    try {
        const response = await fetch(`/api/candidate/${candId}/notes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes: notesText })
        });
        const data = await response.json();
        if (data.success) {
            const cand = AppState.candidates.find(c => c.id === candId);
            if (cand) cand.notes = notesText;
            if (statusLabel) statusLabel.textContent = 'Notes saved successfully';
            showToast('Recruiter notes saved', 'success');
        }
    } catch (err) {
        if (statusLabel) statusLabel.textContent = 'Save failed';
        showToast('Failed to save notes', 'error');
    }
}

// Attach globally for inline HTML event handlers
window.openCandidateModal = openCandidateModal;
window.toggleShortlistCandidate = toggleShortlistCandidate;
window.updateCandidateStatus = updateCandidateStatus;
window.resetAllFilters = resetAllFilters;
