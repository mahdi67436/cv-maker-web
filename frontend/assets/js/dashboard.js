/**
 * FreeUltraCV - Dashboard JavaScript
 */

const API_BASE = '/api';

// State management
let state = {
    user: null,
    resumes: [],
    isLoading: false
};

/**
 * Initialize dashboard
 */
async function initDashboard() {
    // Check authentication
    const token = localStorage.getItem('accessToken');
    if (!token) {
        redirectToLogin();
        return;
    }

    // Get user data
    await loadUserData();

    // Load resumes
    await loadResumes();

    // Setup event listeners
    setupEventListeners();
}

/**
 * Load user data
 */
async function loadUserData() {
    try {
        const token = localStorage.getItem('accessToken');
        const userData = localStorage.getItem('user');

        if (userData) {
            state.user = JSON.parse(userData);
        }

        const response = await fetch(`${API_BASE}/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            state.user = data.data.user;
            localStorage.setItem('user', JSON.stringify(state.user));
        }
    } catch (error) {
        console.error('Error loading user data:', error);
    }
}

/**
 * Load user resumes
 */
async function loadResumes() {
    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/resumes`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            state.resumes = data.data.resumes || [];
            renderResumes();
            updateStats();
        }
    } catch (error) {
        console.error('Error loading resumes:', error);
        renderEmptyState();
    }
}

/**
 * Render resumes
 */
function renderResumes() {
    const grid = document.getElementById('resumesGrid');
    if (!grid) return;

    if (state.resumes.length === 0) {
        renderEmptyState();
        return;
    }

    grid.innerHTML = state.resumes.map(resume => `
        <div class="resume-card glass-effect" data-id="${resume.id}">
            <div class="resume-card-header">
                <h4>${resume.title}</h4>
                <span class="resume-template">${resume.template_name || 'Modern'}</span>
            </div>
            <div class="resume-card-body">
                <p class="resume-name">${resume.full_name || 'No name set'}</p>
                <p class="resume-updated">Updated ${formatDate(resume.updated_at)}</p>
            </div>
            <div class="resume-card-footer">
                <a href="builder.html?id=${resume.id}" class="btn btn-sm btn-secondary">Edit</a>
                <a href="preview.html?id=${resume.id}" class="btn btn-sm btn-ghost">View</a>
                <button class="btn btn-sm btn-ghost delete-btn" data-id="${resume.id}">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                </button>
            </div>
        </div>
    `).join('');

    // Add delete handlers
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', () => deleteResume(btn.dataset.id));
    });
}

/**
 * Render empty state
 */
function renderEmptyState() {
    const grid = document.getElementById('resumesGrid');
    if (!grid) return;

    grid.innerHTML = `
        <div class="resume-placeholder glass-effect">
            <div class="placeholder-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="5" x2="12" y2="19"/>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
            </div>
            <p>No resumes yet</p>
            <button class="btn btn-primary" id="createFirstResume">Create Your First Resume</button>
        </div>
    `;

    document.getElementById('createFirstResume')?.addEventListener('click', createNewResume);
}

/**
 * Update statistics
 */
function updateStats() {
    const totalResumes = state.resumes.length;
    const completedResumes = state.resumes.filter(r => r.is_complete).length;
    const totalDownloads = state.resumes.reduce((sum, r) => sum + (r.pdf_downloads || 0) + (r.docx_downloads || 0), 0);

    const totalResumesEl = document.getElementById('totalResumes');
    const completedResumesEl = document.getElementById('completedResumes');
    const totalDownloadsEl = document.getElementById('totalDownloads');

    if (totalResumesEl) totalResumesEl.textContent = totalResumes;
    if (completedResumesEl) completedResumesEl.textContent = completedResumes;
    if (totalDownloadsEl) totalDownloadsEl.textContent = totalDownloads;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // New resume button
    const newResumeBtn = document.getElementById('newResumeBtn');
    if (newResumeBtn) {
        newResumeBtn.addEventListener('click', createNewResume);
    }

    // Create first resume button
    const createFirstResume = document.getElementById('createFirstResume');
    if (createFirstResume) {
        createFirstResume.addEventListener('click', createNewResume);
    }

    // Quick actions
    const quickNewResume = document.getElementById('quickNewResume');
    if (quickNewResume) {
        quickNewResume.addEventListener('click', createNewResume);
    }

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
}

/**
 * Create new resume
 */
async function createNewResume() {
    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/resumes`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: 'My Resume',
                template_name: 'modern'
            })
        });

        if (response.ok) {
            const data = await response.json();
            const resumeId = data.data.resume.id;
            window.location.href = `builder.html?id=${resumeId}`;
        } else {
            showToast('Failed to create resume', 'error');
        }
    } catch (error) {
        console.error('Create resume error:', error);
        showToast('Failed to create resume', 'error');
    }
}

/**
 * Delete resume
 */
async function deleteResume(resumeId) {
    if (!confirm('Are you sure you want to delete this resume?')) {
        return;
    }

    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/resumes/${resumeId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showToast('Resume deleted successfully', 'success');
            await loadResumes();
        } else {
            showToast('Failed to delete resume', 'error');
        }
    } catch (error) {
        console.error('Delete resume error:', error);
        showToast('Failed to delete resume', 'error');
    }
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) {
        return 'just now';
    } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)} minutes ago`;
    } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)} hours ago`;
    } else if (diff < 604800000) {
        return `${Math.floor(diff / 86400000)} days ago`;
    } else {
        return date.toLocaleDateString();
    }
}

/**
 * Redirect to login
 */
function redirectToLogin() {
    window.location.href = 'login.html';
}

/**
 * Logout user
 */
async function logout() {
    try {
        const token = localStorage.getItem('accessToken');

        if (token) {
            await fetch(`${API_BASE}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        }
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    }
}

/**
 * Show toast notification
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

/**
 * Create toast container
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initDashboard);
