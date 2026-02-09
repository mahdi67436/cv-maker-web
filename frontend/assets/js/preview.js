/**
 * FreeUltraCV - Resume Preview JavaScript
 */

const API_BASE = '/api';

let state = {
    resumeId: null,
    resume: null,
    template: 'modern',
    zoom: 100
};

/**
 * Initialize preview
 */
async function initPreview() {
    const urlParams = new URLSearchParams(window.location.search);
    state.resumeId = urlParams.get('id');

    if (!state.resumeId) {
        showToast('No resume specified', 'error');
        return;
    }

    await loadResume();
    setupEventListeners();
    renderPreview();
}

/**
 * Load resume data
 */
async function loadResume() {
    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/resumes/${state.resumeId}`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });

        if (response.ok) {
            const data = await response.json();
            state.resume = data.data.resume;
            document.getElementById('resumeTitle').textContent = state.resume.title || 'Resume Preview';
        } else {
            showToast('Failed to load resume', 'error');
        }
    } catch (error) {
        console.error('Load error:', error);
        showToast('Failed to load resume', 'error');
    }
}

/**
 * Render preview
 */
function renderPreview() {
    const container = document.getElementById('resumeDocument');
    if (!container || !state.resume) return;

    container.className = `resume-document ${state.template}`;

    const html = `
        <div class="resume-preview ${state.template}">
            <div class="preview-header">
                <h1 class="preview-name">${state.resume.full_name || 'Your Name'}</h1>
                <p class="preview-title">${state.resume.job_title || ''}</p>
                ${renderContactInfo()}
            </div>

            ${state.resume.summary ? `
            <div class="preview-section">
                <h3 class="section-title">Professional Summary</h3>
                <p>${state.resume.summary}</p>
            </div>
            ` : ''}

            ${state.resume.experiences?.length > 0 ? `
            <div class="preview-section">
                <h3 class="section-title">Experience</h3>
                ${state.resume.experiences.map(exp => renderExperience(exp)).join('')}
            </div>
            ` : ''}

            ${state.resume.education?.length > 0 ? `
            <div class="preview-section">
                <h3 class="section-title">Education</h3>
                ${state.resume.education.map(edu => renderEducation(edu)).join('')}
            </div>
            ` : ''}

            ${state.resume.skills?.length > 0 ? `
            <div class="preview-section">
                <h3 class="section-title">Skills</h3>
                <div class="skills-preview">
                    ${state.resume.skills.map(skill => `<span class="skill-tag">${skill.name || ''}</span>`).join('')}
                </div>
            </div>
            ` : ''}

            ${state.resume.projects?.length > 0 ? `
            <div class="preview-section">
                <h3 class="section-title">Projects</h3>
                ${state.resume.projects.map(proj => renderProject(proj)).join('')}
            </div>
            ` : ''}

            ${state.resume.certifications?.length > 0 ? `
            <div class="preview-section">
                <h3 class="section-title">Certifications</h3>
                ${state.resume.certifications.map(cert => renderCertification(cert)).join('')}
            </div>
            ` : ''}
        </div>
    `;

    container.innerHTML = html;
}

function renderContactInfo() {
    const parts = [];
    if (state.resume.email) parts.push(state.resume.email);
    if (state.resume.phone) parts.push(state.resume.phone);
    if (state.resume.city) parts.push(state.resume.city);

    const social = [];
    if (state.resume.linkedin) social.push(`LinkedIn: ${state.resume.linkedin}`);
    if (state.resume.github) social.push(`GitHub: ${state.resume.github}`);
    if (state.resume.portfolio) social.push(`Portfolio: ${state.resume.portfolio}`);

    return `
        <p class="preview-contact">${parts.join(' | ')}</p>
        ${social.length > 0 ? `<p class="preview-social">${social.join(' | ')}</p>` : ''}
    `;
}

function renderExperience(exp) {
    return `
        <div class="preview-item">
            <h4>${exp.position || ''}</h4>
            <p class="preview-subtitle">${exp.company || ''} | ${exp.start_date || ''} - ${exp.end_date || 'Present'}</p>
            ${exp.description ? `<p>${exp.description}</p>` : ''}
        </div>
    `;
}

function renderEducation(edu) {
    return `
        <div class="preview-item">
            <h4>${edu.degree || ''}</h4>
            <p class="preview-subtitle">${edu.institution || ''} | ${edu.start_date || ''} - ${edu.end_date || ''}</p>
            ${edu.gpa ? `<p>GPA: ${edu.gpa}</p>` : ''}
        </div>
    `;
}

function renderProject(proj) {
    return `
        <div class="preview-item">
            <h4>${proj.name || ''}</h4>
            ${proj.description ? `<p>${proj.description}</p>` : ''}
            ${proj.technologies ? `<p class="preview-subtitle">${proj.technologies}</p>` : ''}
        </div>
    `;
}

function renderCertification(cert) {
    return `
        <div class="preview-item">
            <h4>${cert.name || ''}</h4>
            <p class="preview-subtitle">${cert.issuing_organization || ''} | ${cert.issue_date || ''}</p>
        </div>
    `;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Template selector
    document.getElementById('templateSelect')?.addEventListener('change', (e) => {
        state.template = e.target.value;
        renderPreview();
    });

    // Zoom controls
    document.getElementById('zoomIn')?.addEventListener('click', () => zoomPreview(10));
    document.getElementById('zoomOut')?.addEventListener('click', () => zoomPreview(-10));

    // Size buttons
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Share modal
    setupShareModal();

    // QR modal
    setupQrModal();

    // Download dropdown
    setupDownloadDropdown();
}

/**
 * Zoom preview
 */
function zoomPreview(delta) {
    state.zoom = Math.max(50, Math.min(150, state.zoom + delta));
    const preview = document.getElementById('resumeDocument');
    if (preview) {
        preview.style.transform = `scale(${state.zoom / 100})`;
    }
    document.getElementById('zoomLevel').textContent = `${state.zoom}%`;
}

/**
 * Setup share modal
 */
function setupShareModal() {
    const modal = document.getElementById('shareModal');
    const shareBtn = document.getElementById('shareBtn');
    const closeBtn = document.getElementById('closeShareModal');

    shareBtn?.addEventListener('click', () => {
        modal?.classList.add('active');
        generateShareLink();
    });

    closeBtn?.addEventListener('click', () => modal?.classList.remove('active'));
    modal?.querySelector('.modal-overlay')?.addEventListener('click', () => modal?.classList.remove('active'));

    document.getElementById('copyLink')?.addEventListener('click', copyShareLink);

    // Social share buttons
    modal?.querySelectorAll('.share-btn').forEach(btn => {
        btn.addEventListener('click', () => shareOnSocial(btn.dataset.platform));
    });
}

/**
 * Generate share link
 */
function generateShareLink() {
    const shareUrl = `${window.location.origin}/preview/${state.resume.slug}`;
    document.getElementById('shareLink').value = shareUrl;

    const embedCode = `<iframe src="${shareUrl}/embed" width="100%" height="600"></iframe>`;
    document.getElementById('embedCode').value = embedCode;
}

/**
 * Copy share link
 */
function copyShareLink() {
    const input = document.getElementById('shareLink');
    input.select();
    document.execCommand('copy');
    showToast('Link copied!', 'success');
}

/**
 * Share on social
 */
function shareOnSocial(platform) {
    const url = encodeURIComponent(document.getElementById('shareLink').value);
    const title = encodeURIComponent(state.resume.title);

    let shareUrl;
    switch (platform) {
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
            break;
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
            break;
        case 'email':
            shareUrl = `mailto:?subject=${title}&body=Check out my resume: ${url}`;
            break;
    }

    if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=400');
    }
}

/**
 * Setup QR modal
 */
function setupQrModal() {
    const modal = document.getElementById('qrModal');
    const qrBtn = document.getElementById('qrBtn');
    const closeBtn = document.getElementById('closeQrModal');

    qrBtn?.addEventListener('click', () => {
        modal?.classList.add('active');
        generateQrCode();
    });

    closeBtn?.addEventListener('click', () => modal?.classList.remove('active'));
    modal?.querySelector('.modal-overlay')?.addEventListener('click', () => modal?.classList.remove('active'));

    document.getElementById('downloadQr')?.addEventListener('click', downloadQrCode);
}

/**
 * Generate QR code
 */
function generateQrCode() {
    const shareUrl = `${window.location.origin}/preview/${state.resume.slug}`;
    const qrContainer = document.getElementById('qrCode');

    // Using a simple QR code placeholder
    qrContainer.innerHTML = `
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(shareUrl)}" 
             alt="QR Code" 
             style="width: 200px; height: 200px;">
    `;
}

/**
 * Download QR code
 */
function downloadQrCode() {
    const img = document.querySelector('#qrCode img');
    if (img) {
        const a = document.createElement('a');
        a.href = img.src;
        a.download = 'resume-qr.png';
        a.click();
        showToast('QR code downloaded!', 'success');
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
        item.addEventListener('click', () => downloadResume(item.dataset.format));
    });
}

/**
 * Download resume
 */
async function downloadResume(format) {
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
document.addEventListener('DOMContentLoaded', initPreview);
