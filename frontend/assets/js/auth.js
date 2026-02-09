/**
 * FreeUltraCV - Authentication JavaScript
 */

const API_BASE = '/api';

// State management
let state = {
    isLoading: false
};

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const errorMessage = document.getElementById('errorMessage');
const togglePasswordBtns = document.querySelectorAll('.toggle-password');
const passwordInput = document.getElementById('password');
const strengthBar = document.querySelector('.strength-bar');

/**
 * Initialize authentication page
 */
function initAuth() {
    // Check if already logged in
    const token = localStorage.getItem('accessToken');
    if (token) {
        redirectToDashboard();
        return;
    }

    // Setup form handlers
    if (loginForm) {
        setupLoginForm();
    }

    if (registerForm) {
        setupRegisterForm();
    }

    // Setup password toggle
    setupPasswordToggle();

    // Setup password strength meter
    if (registerForm && passwordInput) {
        setupPasswordStrength();
    }
}

/**
 * Setup login form
 */
function setupLoginForm() {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember')?.checked || false;

        // Basic validation
        if (!email || !password) {
            showError('Please fill in all fields');
            return;
        }

        try {
            setLoading(true);

            const response = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password, remember })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Store tokens
                localStorage.setItem('accessToken', data.data.access_token);
                localStorage.setItem('refreshToken', data.data.refresh_token);
                localStorage.setItem('user', JSON.stringify(data.data.user));

                showToast('Login successful!', 'success');
                redirectToDashboard();
            } else {
                showError(data.error || 'Login failed. Please try again.');
            }
        } catch (error) {
            console.error('Login error:', error);
            showError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    });
}

/**
 * Setup register form
 */
function setupRegisterForm() {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        const terms = document.getElementById('terms')?.checked || false;

        // Basic validation
        if (!name || !email || !password || !confirmPassword) {
            showError('Please fill in all fields');
            return;
        }

        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }

        if (!terms) {
            showError('Please accept the terms and conditions');
            return;
        }

        // Password strength check
        if (!validatePasswordStrength(password)) {
            showError('Password does not meet requirements');
            return;
        }

        try {
            setLoading(true);

            const response = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, email, password, confirm_password: confirmPassword })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Store tokens
                localStorage.setItem('accessToken', data.data.access_token);
                localStorage.setItem('refreshToken', data.data.refresh_token);
                localStorage.setItem('user', JSON.stringify(data.data.user));

                showToast('Registration successful!', 'success');
                redirectToDashboard();
            } else {
                showError(data.error || data.errors?.[0] || 'Registration failed. Please try again.');
            }
        } catch (error) {
            console.error('Registration error:', error);
            showError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    });
}

/**
 * Setup password toggle visibility
 */
function setupPasswordToggle() {
    togglePasswordBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.parentElement.querySelector('input');
            const type = input.type === 'password' ? 'text' : 'password';
            input.type = type;

            // Update icon
            const svg = btn.querySelector('svg');
            if (type === 'text') {
                svg.innerHTML = `
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                `;
            } else {
                svg.innerHTML = `
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                `;
            }
        });
    });
}

/**
 * Setup password strength meter
 */
function setupPasswordStrength() {
    passwordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        const strength = calculatePasswordStrength(password);

        strengthBar.className = 'strength-bar';

        if (password.length === 0) {
            strengthBar.style.width = '0';
        } else if (strength < 40) {
            strengthBar.classList.add('weak');
        } else if (strength < 80) {
            strengthBar.classList.add('medium');
        } else {
            strengthBar.classList.add('strong');
        }
    });
}

/**
 * Calculate password strength
 */
function calculatePasswordStrength(password) {
    let score = 0;
    let criteria = 0;

    // Length check
    if (password.length >= 8) {
        score += 20;
        criteria++;
    }
    if (password.length >= 12) {
        score += 10;
    }

    // Uppercase check
    if (/[A-Z]/.test(password)) {
        score += 20;
        criteria++;
    }

    // Lowercase check
    if (/[a-z]/.test(password)) {
        score += 20;
        criteria++;
    }

    // Number check
    if (/\d/.test(password)) {
        score += 20;
        criteria++;
    }

    // Special character check
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        score += 20;
        criteria++;
    }

    // Bonus for variety
    if (criteria >= 5) {
        score += 10;
    }

    return Math.min(score, 100);
}

/**
 * Validate password strength
 */
function validatePasswordStrength(password) {
    const minLength = 8;
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return password.length >= minLength &&
           hasUpper &&
           hasLower &&
           hasNumber &&
           hasSpecial;
}

/**
 * Set loading state
 */
function setLoading(isLoading) {
    state.isLoading = isLoading;

    const submitBtns = document.querySelectorAll('button[type="submit"]');
    submitBtns.forEach(btn => {
        btn.disabled = isLoading;
        btn.innerHTML = isLoading
            ? '<span class="spinner"></span> Please wait...'
            : btn.dataset.originalText || 'Submit';
    });
}

/**
 * Show error message
 */
function showError(message) {
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';

        // Auto hide after 5 seconds
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    } else {
        showToast(message, 'error');
    }
}

/**
 * Redirect to dashboard
 */
function redirectToDashboard() {
    window.location.href = 'dashboard.html';
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Remove after 3 seconds
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
        // Clear local storage
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');

        // Redirect to home
        window.location.href = 'index.html';
    }
}

// Export for use in other scripts
window.authUtils = {
    logout,
    showToast,
    calculatePasswordStrength,
    validatePasswordStrength
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initAuth);
