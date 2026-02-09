/**
 * FreeUltraCV - Main JavaScript
 */

const API_BASE = '/api';

/**
 * Initialize main page
 */
function initMain() {
    setupNavigation();
    setupSmoothScroll();
    setupMobileMenu();
    checkAuthState();
}

/**
 * Check authentication state
 */
async function checkAuthState() {
    const token = localStorage.getItem('accessToken');
    const loginBtn = document.querySelector('.nav-auth a[href="login.html"]');
    const registerBtn = document.querySelector('.nav-auth a[href="register.html"]');

    if (token) {
        // User is logged in
        if (loginBtn) loginBtn.textContent = 'Dashboard';
        if (loginBtn) loginBtn.href = 'dashboard.html';
        if (registerBtn) registerBtn.style.display = 'none';
    }
}

/**
 * Setup navigation
 */
function setupNavigation() {
    // Sticky navbar effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
}

/**
 * Setup smooth scrolling
 */
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Setup mobile menu
 */
function setupMobileMenu() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.querySelector('.nav-links');
    const navAuth = document.querySelector('.nav-auth');

    if (menuBtn && (navLinks || navAuth)) {
        menuBtn.addEventListener('click', () => {
            menuBtn.classList.toggle('active');

            if (navLinks) navLinks.classList.toggle('active');
            if (navAuth) navAuth.classList.toggle('active');
        });
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
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Generate unique ID
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Copy to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success');
        return true;
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            document.execCommand('copy');
            showToast('Copied to clipboard!', 'success');
            return true;
        } catch (err) {
            showToast('Failed to copy', 'error');
            return false;
        } finally {
            document.body.removeChild(textArea);
        }
    }
}

/**
 * API helper
 */
async function api(endpoint, options = {}) {
    const token = localStorage.getItem('accessToken');

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || 'API request failed');
    }

    return data;
}

/**
 * Check if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Animate elements on scroll
 */
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, { threshold: 0.1 });

    elements.forEach(el => observer.observe(el));
}

/**
 * Initialize animations
 */
function initAnimations() {
    // Add animation classes
    document.querySelectorAll('.feature-card, .template-card, .step').forEach(el => {
        el.classList.add('animate-on-scroll');
    });

    // Start scroll animations
    animateOnScroll();
}

// Export utilities
window.freultracv = {
    showToast,
    formatDate,
    debounce,
    throttle,
    generateId,
    copyToClipboard,
    api,
    isInViewport,
    checkAuthState
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initMain);
