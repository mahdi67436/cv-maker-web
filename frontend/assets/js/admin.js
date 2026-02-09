/**
 * FreeUltraCV - Admin Panel JavaScript
 */

const API_BASE = '/api';

let state = {
    currentPage: 'dashboard',
    stats: {
        users: 0,
        resumes: 0,
        downloads: 0,
        templates: 5
    },
    users: [],
    templates: []
};

/**
 * Initialize admin panel
 */
async function initAdmin() {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        redirectToLogin();
        return;
    }

    // Check admin access
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    if (!userData.is_admin) {
        redirectToDashboard();
        return;
    }

    await loadDashboardData();
    setupEventListeners();
}

/**
 * Load dashboard data
 */
async function loadDashboardData() {
    try {
        const token = localStorage.getItem('accessToken');

        // Load stats
        const statsResponse = await fetch(`${API_BASE}/admin/stats`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (statsResponse.ok) {
            const data = await statsResponse.json();
            state.stats = {
                users: data.data.users.total,
                resumes: data.data.templates.total || 0,
                downloads: (data.data.downloads.pdf + data.data.downloads.docx + data.data.downloads.png),
                templates: 5
            };
            updateStatsDisplay();
        }

        // Load recent users
        await loadUsers(1);

    } catch (error) {
        console.error('Load dashboard error:', error);
    }
}

/**
 * Update stats display
 */
function updateStatsDisplay() {
    document.getElementById('totalUsers').textContent = state.stats.users.toLocaleString();
    document.getElementById('totalResumes').textContent = state.stats.resumes.toLocaleString();
    document.getElementById('totalDownloads').textContent = state.stats.downloads.toLocaleString();
}

/**
 * Load users
 */
async function loadUsers(page = 1) {
    try {
        const token = localStorage.getItem('accessToken');
        const status = document.getElementById('userStatusFilter')?.value || '';

        const response = await fetch(`${API_BASE}/admin/users?page=${page}&status=${status}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            state.users = data.data.users;
            renderUsersTable(data.data.users);
            renderPagination(data.data.total, data.data.page, data.data.per_page);
        }
    } catch (error) {
        console.error('Load users error:', error);
    }
}

/**
 * Render users table
 */
function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;

    tbody.innerHTML = users.map(user => `
        <tr>
            <td>
                <div class="table-user">
                    <div class="table-avatar">${user.name?.charAt(0) || user.email?.charAt(0) || 'U'}</div>
                    <div class="table-user-info">
                        <span class="table-user-name">${user.name || 'Unknown'}</span>
                        <span class="table-user-email">${user.email}</span>
                    </div>
                </div>
            </td>
            <td>
                <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                    ${user.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>${user.resume_count || 0}</td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                <div class="table-actions">
                    <button class="table-action-btn" onclick="viewUser(${user.id})" title="View">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                            <circle cx="12" cy="12" r="3"/>
                        </svg>
                    </button>
                    <button class="table-action-btn" onclick="toggleUserStatus(${user.id})" title="Toggle Status">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>
                            <line x1="12" y1="2" x2="12" y2="12"/>
                        </svg>
                    </button>
                    <button class="table-action-btn delete" onclick="deleteUser(${user.id})" title="Delete">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

/**
 * Render pagination
 */
function renderPagination(total, page, perPage) {
    const pagination = document.getElementById('usersPagination');
    if (!pagination) return;

    const totalPages = Math.ceil(total / perPage);

    let html = '';

    // Previous button
    html += `
        <button class="pagination-btn" ${page === 1 ? 'disabled' : ''} onclick="loadUsers(${page - 1})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"/>
            </svg>
        </button>
    `;

    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === page) {
            html += `<button class="pagination-btn active">${i}</button>`;
        } else if (i === 1 || i === totalPages || (i >= page - 2 && i <= page + 2)) {
            html += `<button class="pagination-btn" onclick="loadUsers(${i})">${i}</button>`;
        } else if (i === page - 3 || i === page + 3) {
            html += `<span class="pagination-btn" style="pointer-events: none;">...</span>`;
        }
    }

    // Next button
    html += `
        <button class="pagination-btn" ${page === totalPages ? 'disabled' : ''} onclick="loadUsers(${page + 1})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
            </svg>
        </button>
    `;

    pagination.innerHTML = html;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.sidebar .nav-item[data-page]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            switchPage(item.dataset.page);
        });
    });

    // User status filter
    document.getElementById('userStatusFilter')?.addEventListener('change', () => {
        loadUsers(1);
    });

    // Logout
    document.getElementById('adminLogout')?.addEventListener('click', logout);

    // Mobile menu
    document.querySelector('.mobile-menu-toggle')?.addEventListener('click', toggleMobileMenu);
}

/**
 * Switch page
 */
function switchPage(page) {
    state.currentPage = page;

    // Update nav
    document.querySelectorAll('.sidebar .nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });

    // Update page content
    document.querySelectorAll('.admin-page').forEach(p => {
        p.classList.toggle('active', p.id === `${page}Page`);
    });

    // Update title
    const titles = {
        dashboard: 'Dashboard',
        users: 'User Management',
        resumes: 'Resume Management',
        templates: 'Template Management',
        analytics: 'Analytics',
        settings: 'Settings'
    };

    document.getElementById('pageTitle').textContent = titles[page] || 'Admin';
}

/**
 * Toggle user status
 */
async function toggleUserStatus(userId) {
    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/admin/users/${userId}/status`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            showToast('User status updated', 'success');
            loadUsers(1);
        } else {
            showToast('Failed to update user', 'error');
        }
    } catch (error) {
        console.error('Toggle status error:', error);
        showToast('Failed to update user', 'error');
    }
}

/**
 * Delete user
 */
async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        return;
    }

    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/admin/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            showToast('User deleted', 'success');
            loadUsers(1);
        } else {
            showToast('Failed to delete user', 'error');
        }
    } catch (error) {
        console.error('Delete user error:', error);
        showToast('Failed to delete user', 'error');
    }
}

/**
 * View user details
 */
function viewUser(userId) {
    showToast('User details coming soon', 'info');
}

/**
 * Load templates
 */
async function loadTemplates() {
    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/admin/templates`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            state.templates = data.data.templates;
            renderTemplatesGrid();
        }
    } catch (error) {
        console.error('Load templates error:', error);
    }
}

/**
 * Render templates grid
 */
function renderTemplatesGrid() {
    const grid = document.getElementById('templatesGrid');
    if (!grid) return;

    grid.innerHTML = state.templates.map(template => `
        <div class="template-card-admin">
            <div class="template-preview-admin">
                <div class="template-preview ${template.slug}">
                    <div class="template-content">
                        <div class="tp-name"></div>
                        <div class="tp-title"></div>
                    </div>
                </div>
            </div>
            <div class="template-info-admin">
                <h4>${template.name}</h4>
                <p>${template.description || 'No description'}</p>
                <div class="template-actions">
                    <button class="btn btn-secondary btn-sm" onclick="editTemplate(${template.id})">Edit</button>
                    <button class="btn btn-ghost btn-sm" onclick="toggleTemplateStatus(${template.id})">
                        ${template.is_active ? 'Disable' : 'Enable'}
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Toggle template status
 */
async function toggleTemplateStatus(templateId) {
    try {
        const token = localStorage.getItem('accessToken');

        const response = await fetch(`${API_BASE}/admin/templates/${templateId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                is_active: !state.templates.find(t => t.id === templateId)?.is_active
            })
        });

        if (response.ok) {
            showToast('Template updated', 'success');
            loadTemplates();
        } else {
            showToast('Failed to update template', 'error');
        }
    } catch (error) {
        console.error('Toggle template error:', error);
        showToast('Failed to update template', 'error');
    }
}

/**
 * Edit template
 */
function editTemplate(templateId) {
    showToast('Template editor coming soon', 'info');
}

/**
 * Toggle mobile menu
 */
function toggleMobileMenu() {
    document.querySelector('.admin-sidebar')?.classList.toggle('active');
}

/**
 * Format date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Redirect to login
 */
function redirectToLogin() {
    window.location.href = 'login.html';
}

/**
 * Redirect to dashboard
 */
function redirectToDashboard() {
    window.location.href = 'dashboard.html';
}

/**
 * Logout
 */
async function logout() {
    try {
        const token = localStorage.getItem('accessToken');

        if (token) {
            await fetch(`${API_BASE}/auth/logout`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
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

// Make functions globally accessible
window.loadUsers = loadUsers;
window.toggleUserStatus = toggleUserStatus;
window.deleteUser = deleteUser;
window.viewUser = viewUser;
window.toggleTemplateStatus = toggleTemplateStatus;
window.editTemplate = editTemplate;

// Initialize
document.addEventListener('DOMContentLoaded', initAdmin);
