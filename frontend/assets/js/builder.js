/**
 * FreeUltraCV - Resume Builder JavaScript
 */

const API_BASE = '/api';

// State management
let state = {
    resumeId: null,
    resume: {
        title: 'My Resume',
        template_name: 'modern',
        full_name: '',
        email: '',
        phone: '',
        city: '',
        country: '',
        linkedin: '',
        github: '',
        portfolio: '',
        summary: '',
        experiences: [],
        education: [],
        skills: [],
        projects: [],
        certifications: []
    },
    isLoading: false,
    isDirty: false,
    saveTimeout: null
};

/**
 * Initialize builder
 */
async function initBuilder() {
    // Get resume ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    state.resumeId = urlParams.get('id');

    // Check authentication
    const token = localStorage.getItem('accessToken');
    if (!token && !state.resumeId) {
        redirectToLogin();
        return;
    }

    // Load resume data
    if (state.resumeId) {
        await loadResume();
    }

    // Setup event listeners
    setupEventListeners();

    // Setup auto-save
    setupAutoSave();

    // Initial render
    renderPreview();
}

/**
 * Load resume data
 */
async function loadResume() {
    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/resumes/${state.resumeId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            state.resume = { ...state.resume, ...data.data.resume };
            updateFormFromState();
            updateSaveStatus('saved');
        } else {
            showToast('Failed to load resume', 'error');
        }
    } catch (error) {
        console.error('Load resume error:', error);
        showToast('Failed to load resume', 'error');
    }
}

/**
 * Update form from state
 */
function updateFormFromState() {
    // Personal info
    document.getElementById('resumeTitle').value = state.resume.title || 'My Resume';
    document.getElementById('fullName').value = state.resume.full_name || '';
    document.getElementById('jobTitle').value = state.resume.job_title || '';
    document.getElementById('email').value = state.resume.email || '';
    document.getElementById('phone').value = state.resume.phone || '';
    document.getElementById('city').value = state.resume.city || '';
    document.getElementById('country').value = state.resume.country || '';
    document.getElementById('linkedin').value = state.resume.linkedin || '';
    document.getElementById('github').value = state.resume.github || '';
    document.getElementById('portfolio').value = state.resume.portfolio || '';
    document.getElementById('summary').value = state.resume.summary || '';

    // Render lists
    renderExperienceList();
    renderEducationList();
    renderSkillsList();
    renderProjectsList();
    renderCertificationsList();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-section').forEach(btn => {
        btn.addEventListener('click', () => switchSection(btn.dataset.section));
    });

    // Form inputs - save on change
    document.querySelectorAll('input, textarea, select').forEach(input => {
        input.addEventListener('input', handleInputChange);
        input.addEventListener('change', handleInputChange);
    });

    // Resume title
    document.getElementById('resumeTitle').addEventListener('blur', async (e) => {
        state.resume.title = e.target.value;
        await saveResume();
    });

    // Add buttons
    document.getElementById('addExperience')?.addEventListener('click', () => addExperience());
    document.getElementById('addEducation')?.addEventListener('click', () => addEducation());
    document.getElementById('addSkill')?.addEventListener('click', () => addSkill());
    document.getElementById('addProject')?.addEventListener('click', () => addProject());
    document.getElementById('addCertification')?.addEventListener('click', () => addCertification());

    // AI buttons
    document.getElementById('aiGenerateSummary')?.addEventListener('click', generateAISummary);
    document.getElementById('aiSuggestSkills')?.addEventListener('click', suggestAISkills);

    // Preview buttons
    document.getElementById('previewBtn')?.addEventListener('click', () => {
        if (state.resumeId) {
            window.location.href = `preview.html?id=${state.resumeId}`;
        } else {
            showToast('Please save your resume first', 'warning');
        }
    });

    // Download dropdown
    setupDownloadDropdown();

    // ATS check
    document.getElementById('atsCheckBtn')?.addEventListener('click', runATSCheck);

    // AI modal
    setupAIModal();

    // Zoom controls
    document.getElementById('zoomIn')?.addEventListener('click', () => zoomPreview(10));
    document.getElementById('zoomOut')?.addEventListener('click', () => zoomPreview(-10));
}

/**
 * Handle input change
 */
function handleInputChange(e) {
    const id = e.target.id;
    const value = e.target.value;

    // Map form fields to state
    const fieldMap = {
        'fullName': 'full_name',
        'jobTitle': 'job_title',
        'email': 'email',
        'phone': 'phone',
        'city': 'city',
        'country': 'country',
        'linkedin': 'linkedin',
        'github': 'github',
        'portfolio': 'portfolio',
        'summary': 'summary'
    };

    if (fieldMap[id]) {
        state.resume[fieldMap[id]] = value;
    }

    // Update preview
    renderPreview();

    // Mark as dirty
    state.isDirty = true;
    updateSaveStatus('saving');

    // Clear save timeout
    if (state.saveTimeout) {
        clearTimeout(state.saveTimeout);
    }
}

/**
 * Switch section
 */
function switchSection(section) {
    // Update nav
    document.querySelectorAll('.nav-section').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.section === section);
    });

    // Update form sections
    document.querySelectorAll('.form-section').forEach(sec => {
        sec.classList.toggle('active', sec.id === `${section}Section`);
    });
}

/**
 * Render preview
 */
function renderPreview() {
    const container = document.getElementById('resumePreview');
    if (!container) return;

    const template = state.resume.template_name || 'modern';
    container.className = `resume-preview ${template}`;

    container.innerHTML = `
        <div class="preview-header">
            <h1 class="preview-name">${state.resume.full_name || 'Your Name'}</h1>
            <p class="preview-title">${state.resume.job_title || ''}</p>
        </div>
        
        ${state.resume.summary ? `
        <div class="preview-section summary-section">
            <h3 class="section-title">Professional Summary</h3>
            <p>${state.resume.summary}</p>
        </div>
        ` : ''}
        
        ${state.resume.experiences.length > 0 ? `
        <div class="preview-section">
            <h3 class="section-title">Experience</h3>
            ${state.resume.experiences.map(exp => `
                <div class="preview-item">
                    <h4>${exp.position || ''}</h4>
                    <p class="preview-subtitle">${exp.company || ''} | ${exp.start_date || ''} - ${exp.end_date || 'Present'}</p>
                    ${exp.description ? `<p>${exp.description}</p>` : ''}
                </div>
            `).join('')}
        </div>
        ` : ''}
        
        ${state.resume.education.length > 0 ? `
        <div class="preview-section">
            <h3 class="section-title">Education</h3>
            ${state.resume.education.map(edu => `
                <div class="preview-item">
                    <h4>${edu.degree || ''}</h4>
                    <p class="preview-subtitle">${edu.institution || ''} | ${edu.start_date || ''} - ${edu.end_date || ''}</p>
                </div>
            `).join('')}
        </div>
        ` : ''}
        
        ${state.resume.skills.length > 0 ? `
        <div class="preview-section">
            <h3 class="section-title">Skills</h3>
            <div class="skills-preview">
                ${state.resume.skills.map(skill => `
                    <span class="skill-tag">${skill.name || ''}</span>
                `).join('')}
            </div>
        </div>
        ` : ''}
    `;
}

/**
 * Experience list
 */
function renderExperienceList() {
    const container = document.getElementById('experienceList');
    if (!container) return;

    container.innerHTML = state.resume.experiences.map((exp, index) => `
        <div class="item-card" data-index="${index}">
            <div class="item-card-header">
                <span class="item-card-title">${exp.position || exp.company || 'New Experience'}</span>
                <div class="item-card-actions">
                    <button class="item-action-btn delete" data-type="experience" data-index="${index}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="item-card-body">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Position</label>
                        <input type="text" value="${exp.position || ''}" data-type="experience" data-index="${index}" data-field="position">
                    </div>
                    <div class="form-group">
                        <label>Company</label>
                        <input type="text" value="${exp.company || ''}" data-type="experience" data-index="${index}" data-field="company">
                    </div>
                    <div class="form-group">
                        <label>Start Date</label>
                        <input type="text" value="${exp.start_date || ''}" data-type="experience" data-index="${index}" data-field="start_date">
                    </div>
                    <div class="form-group">
                        <label>End Date</label>
                        <input type="text" value="${exp.end_date || ''}" data-type="experience" data-index="${index}" data-field="end_date">
                    </div>
                    <div class="form-group full-width">
                        <label>Description</label>
                        <textarea rows="3" data-type="experience" data-index="${index}" data-field="description">${exp.description || ''}</textarea>
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    // Add event listeners
    container.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('input', updateExperience);
    });

    container.querySelectorAll('.delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteItem('experience', parseInt(btn.dataset.index));
        });
    });
}

function updateExperience(e) {
    const { type, index, field } = e.target.dataset;
    if (type === 'experience') {
        state.resume.experiences[index][field] = e.target.value;
        renderPreview();
    }
}

function addExperience() {
    state.resume.experiences.push({
        position: '',
        company: '',
        start_date: '',
        end_date: 'Present',
        description: ''
    });
    renderExperienceList();
    renderPreview();
}

/**
 * Education list
 */
function renderEducationList() {
    const container = document.getElementById('educationList');
    if (!container) return;

    container.innerHTML = state.resume.education.map((edu, index) => `
        <div class="item-card" data-index="${index}">
            <div class="item-card-header">
                <span class="item-card-title">${edu.degree || edu.institution || 'New Education'}</span>
                <div class="item-card-actions">
                    <button class="item-action-btn delete" data-type="education" data-index="${index}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="item-card-body">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Degree</label>
                        <input type="text" value="${edu.degree || ''}" data-type="education" data-index="${index}" data-field="degree">
                    </div>
                    <div class="form-group">
                        <label>Institution</label>
                        <input type="text" value="${edu.institution || ''}" data-type="education" data-index="${index}" data-field="institution">
                    </div>
                    <div class="form-group">
                        <label>Start Date</label>
                        <input type="text" value="${edu.start_date || ''}" data-type="education" data-index="${index}" data-field="start_date">
                    </div>
                    <div class="form-group">
                        <label>End Date</label>
                        <input type="text" value="${edu.end_date || ''}" data-type="education" data-index="${index}" data-field="end_date">
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    container.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', updateEducation);
    });

    container.querySelectorAll('.delete').forEach(btn => {
        btn.addEventListener('click', () => deleteItem('education', parseInt(btn.dataset.index)));
    });
}

function updateEducation(e) {
    const { type, index, field } = e.target.dataset;
    if (type === 'education') {
        state.resume.education[index][field] = e.target.value;
        renderPreview();
    }
}

function addEducation() {
    state.resume.education.push({
        degree: '',
        institution: '',
        start_date: '',
        end_date: ''
    });
    renderEducationList();
    renderPreview();
}

/**
 * Skills list
 */
function renderSkillsList() {
    const container = document.getElementById('skillsContainer');
    if (!container) return;

    container.innerHTML = `
        <div class="skills-container">
            ${state.resume.skills.map((skill, index) => `
                <span class="skill-tag">
                    ${skill.name || ''}
                    <button class="remove-skill" data-index="${index}">&times;</button>
                </span>
            `).join('')}
        </div>
        <div class="add-skill-form">
            <input type="text" id="newSkill" placeholder="Add a skill...">
            <button class="btn btn-primary" id="saveNewSkill">Add</button>
        </div>
    `;

    document.getElementById('saveNewSkill')?.addEventListener('click', () => {
        const input = document.getElementById('newSkill');
        if (input.value.trim()) {
            state.resume.skills.push({ name: input.value.trim(), category: 'Other' });
            input.value = '';
            renderSkillsList();
            renderPreview();
        }
    });

    container.querySelectorAll('.remove-skill').forEach(btn => {
        btn.addEventListener('click', () => deleteItem('skill', parseInt(btn.dataset.index)));
    });
}

function addSkill() {
    const input = document.getElementById('newSkill');
    if (input && input.value.trim()) {
        state.resume.skills.push({ name: input.value.trim(), category: 'Other' });
        input.value = '';
        renderSkillsList();
        renderPreview();
    }
}

function suggestAISkills() {
    // AI skill suggestions would go here
    showToast('AI skill suggestions feature coming soon', 'info');
}

/**
 * Delete item
 */
function deleteItem(type, index) {
    if (type === 'experience') {
        state.resume.experiences.splice(index, 1);
        renderExperienceList();
    } else if (type === 'education') {
        state.resume.education.splice(index, 1);
        renderEducationList();
    } else if (type === 'skill') {
        state.resume.skills.splice(index, 1);
        renderSkillsList();
    }
    renderPreview();
}

/**
 * Setup auto-save
 */
function setupAutoSave() {
    // Save every 30 seconds if dirty
    setInterval(() => {
        if (state.isDirty && state.resumeId) {
            saveResume();
        }
    }, 30000);
}

/**
 * Save resume
 */
async function saveResume() {
    try {
        const token = localStorage.getItem('accessToken');

        const data = {
            title: state.resume.title,
            template_name: state.resume.template_name,
            full_name: state.resume.full_name,
            email: state.resume.email,
            phone: state.resume.phone,
            city: state.resume.city,
            country: state.resume.country,
            linkedin: state.resume.linkedin,
            github: state.resume.github,
            portfolio: state.resume.portfolio,
            summary: state.resume.summary,
            content: {
                experiences: state.resume.experiences,
                education: state.resume.education,
                skills: state.resume.skills,
                projects: state.resume.projects,
                certifications: state.resume.certifications
            }
        };

        if (state.resumeId) {
            // Update existing
            const response = await fetch(`${API_BASE}/resumes/${state.resumeId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                state.isDirty = false;
                updateSaveStatus('saved');
            }
        } else {
            // Create new
            const response = await fetch(`${API_BASE}/resumes`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                state.resumeId = result.data.resume.id;
                state.isDirty = false;
                updateSaveStatus('saved');

                // Update URL
                const newUrl = `${window.location.pathname}?id=${state.resumeId}`;
                window.history.pushState({ id: state.resumeId }, '', newUrl);
            }
        }
    } catch (error) {
        console.error('Save error:', error);
        updateSaveStatus('error');
    }
}

/**
 * Update save status
 */
function updateSaveStatus(status) {
    const statusEl = document.getElementById('saveStatus');
    if (!statusEl) return;

    const dot = statusEl.querySelector('.status-dot');
    const text = statusEl.querySelector('.status-text');

    if (status === 'saving') {
        dot.className = 'status-dot saving';
        text.textContent = 'Saving...';
    } else if (status === 'saved') {
        dot.className = 'status-dot';
        text.textContent = 'Saved';
    } else if (status === 'error') {
        dot.className = 'status-dot';
        dot.style.background = 'var(--danger)';
        text.textContent = 'Error saving';
    }
}

/**
 * Setup download dropdown
 */
function setupDownloadDropdown() {
    const btn = document.getElementById('downloadBtn');
    const menu = document.getElementById('downloadMenu');

    btn?.addEventListener('click', (e) => {
        e.stopPropagation();
        menu?.parentElement.classList.toggle('active');
    });

    document.addEventListener('click', () => {
        menu?.parentElement.classList.remove('active');
    });

    menu?.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
            const format = item.dataset.format;
            downloadResume(format);
        });
    });
}

/**
 * Download resume
 */
async function downloadResume(format) {
    if (!state.resumeId) {
        showToast('Please save your resume first', 'warning');
        return;
    }

    showToast(`Downloading as ${format.toUpperCase()}...`, 'info');

    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/export/${format}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resume_id: state.resumeId })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${state.resume.title}.${format}`;
            a.click();
            window.URL.revokeObjectURL(url);
            showToast('Download complete!', 'success');
        } else {
            showToast('Download failed', 'error');
        }
    } catch (error) {
        console.error('Download error:', error);
        showToast('Download failed', 'error');
    }
}

/**
 * Run ATS check
 */
async function runATSCheck() {
    if (!state.resumeId) {
        showToast('Please save your resume first', 'warning');
        return;
    }

    showToast('Running ATS analysis...', 'info');

    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/ai/ats-check`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ resume_id: state.resumeId })
        });

        if (response.ok) {
            const data = await response.json();
            showATSScore(data.data);
        } else {
            showToast('ATS check failed', 'error');
        }
    } catch (error) {
        console.error('ATS check error:', error);
        showToast('ATS check failed', 'error');
    }
}

/**
 * Show ATS score
 */
function showATSScore(data) {
    const score = data.overall_score;
    let message = '';

    if (score >= 80) {
        message = `Great! Your ATS score is ${score}. Your resume should pass most ATS systems.`;
    } else if (score >= 60) {
        message = `Your ATS score is ${score}. Consider adding more keywords to improve.`;
    } else {
        message = `Your ATS score is ${score}. Significant improvements needed.`;
    }

    showToast(message, score >= 80 ? 'success' : 'warning');
}

/**
 * Generate AI summary
 */
async function generateAISummary() {
    showToast('Generating summary with AI...', 'info');

    // This would call the AI API
    setTimeout(() => {
        state.resume.summary = 'Experienced professional with a proven track record of success...';
        document.getElementById('summary').value = state.resume.summary;
        renderPreview();
        showToast('Summary generated!', 'success');
    }, 2000);
}

/**
 * Setup AI modal
 */
function setupAIModal() {
    const modal = document.getElementById('aiModal');
    const closeBtn = document.getElementById('closeAiModal');

    closeBtn?.addEventListener('click', () => {
        modal?.classList.remove('active');
    });

    modal?.querySelector('.modal-overlay')?.addEventListener('click', () => {
        modal?.classList.remove('active');
    });
}

/**
 * Zoom preview
 */
function zoomPreview(delta) {
    const preview = document.getElementById('resumePreview');
    const levelEl = document.getElementById('zoomLevel');

    if (!preview || !levelEl) return;

    let current = parseInt(levelEl.textContent);
    current = Math.max(50, Math.min(150, current + delta));

    preview.style.transform = `scale(${current / 100})`;
    levelEl.textContent = `${current}%`;
}

/**
 * Placeholder functions for missing sections
 */
function renderProjectsList() {}
function renderCertificationsList() {}
function addProject() {}
function addCertification() {}

/**
 * Redirect to login
 */
function redirectToLogin() {
    window.location.href = 'login.html';
}

/**
 * Show toast
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Initialize
document.addEventListener('DOMContentLoaded', initBuilder);
