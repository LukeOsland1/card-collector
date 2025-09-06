/**
 * Card Collector - Main Application JavaScript
 */

// Global application state
const CardCollector = {
    // Configuration
    config: {
        apiBaseUrl: '/api/v1',
        itemsPerPage: 20,
        debounceDelay: 500,
    },
    
    // State management
    state: {
        currentUser: null,
        accessToken: localStorage.getItem('access_token'),
        theme: localStorage.getItem('theme') || 'light',
    },
    
    // Initialize application
    init() {
        this.loadTheme();
        this.setupEventListeners();
        this.checkAuthStatus();
        
        // Add fade-in animation to main content
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelector('main')?.classList.add('fade-in');
        });
    },
    
    // Theme management
    loadTheme() {
        if (this.state.theme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    },
    
    toggleTheme() {
        this.state.theme = this.state.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.state.theme);
        document.body.classList.toggle('dark-theme');
    },
    
    // Event listeners
    setupEventListeners() {
        // Handle auth callback
        if (window.location.pathname === '/auth/callback') {
            this.handleAuthCallback();
        }
        
        // Setup form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('ajax-form')) {
                e.preventDefault();
                this.handleFormSubmission(e.target);
            }
        });
        
        // Setup click handlers
        document.addEventListener('click', (e) => {
            // Handle logout clicks
            if (e.target.matches('[data-action="logout"]')) {
                e.preventDefault();
                this.logout();
            }
            
            // Handle card interactions
            if (e.target.closest('.card-item')) {
                this.handleCardClick(e.target.closest('.card-item'));
            }
        });
        
        // Setup keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
        });
        
        // Handle network status
        window.addEventListener('online', () => this.showNotification('Connection restored', 'success'));
        window.addEventListener('offline', () => this.showNotification('Connection lost', 'warning'));
    },
    
    // Authentication
    async checkAuthStatus() {
        if (this.state.accessToken) {
            try {
                const user = await this.apiCall('/users/me');
                this.state.currentUser = user;
                this.updateAuthUI(true);
            } catch (error) {
                console.error('Auth check failed:', error);
                this.logout();
            }
        } else {
            this.updateAuthUI(false);
        }
    },
    
    async handleAuthCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const error = urlParams.get('error');
        
        if (error) {
            this.showNotification(`Authentication failed: ${error}`, 'danger');
            window.location.href = '/';
            return;
        }
        
        if (code) {
            try {
                const response = await fetch('/auth/callback?' + window.location.search.slice(1));
                const data = await response.json();
                
                if (data.access_token) {
                    localStorage.setItem('access_token', data.access_token);
                    this.state.accessToken = data.access_token;
                    this.state.currentUser = data.user;
                    
                    this.showNotification('Login successful!', 'success');
                    window.location.href = '/';
                } else {
                    throw new Error('No access token received');
                }
            } catch (error) {
                console.error('Auth callback failed:', error);
                this.showNotification('Authentication failed', 'danger');
                window.location.href = '/';
            }
        }
    },
    
    logout() {
        localStorage.removeItem('access_token');
        this.state.accessToken = null;
        this.state.currentUser = null;
        this.updateAuthUI(false);
        this.showNotification('Logged out successfully', 'info');
        
        // Redirect to home if on a protected page
        if (window.location.pathname === '/collection' || window.location.pathname === '/admin') {
            window.location.href = '/';
        }
    },
    
    updateAuthUI(isAuthenticated) {
        const loginElements = document.querySelectorAll('[data-auth="login"]');
        const logoutElements = document.querySelectorAll('[data-auth="logout"]');
        const protectedElements = document.querySelectorAll('[data-auth="protected"]');
        
        loginElements.forEach(el => el.style.display = isAuthenticated ? 'none' : '');
        logoutElements.forEach(el => el.style.display = isAuthenticated ? '' : 'none');
        protectedElements.forEach(el => el.style.display = isAuthenticated ? '' : 'none');
        
        // Update user info displays
        if (isAuthenticated && this.state.currentUser) {
            document.querySelectorAll('[data-user="name"]').forEach(el => {
                el.textContent = this.state.currentUser.username;
            });
            
            document.querySelectorAll('[data-user="avatar"]').forEach(el => {
                if (this.state.currentUser.avatar) {
                    el.src = `https://cdn.discordapp.com/avatars/${this.state.currentUser.discord_id}/${this.state.currentUser.avatar}.png`;
                }
            });
        }
    },
    
    // API helpers
    async apiCall(endpoint, options = {}) {
        const url = this.config.apiBaseUrl + endpoint;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (this.state.accessToken) {
            defaultOptions.headers.Authorization = `Bearer ${this.state.accessToken}`;
        }
        
        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };
        
        const response = await fetch(url, finalOptions);
        
        if (response.status === 401) {
            this.logout();
            throw new Error('Unauthorized');
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}`);
        }
        
        return response.json();
    },
    
    // UI helpers
    showNotification(message, type = 'info', duration = 5000) {
        const alertsContainer = document.getElementById('alerts-container') || document.querySelector('main');
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertsContainer.insertBefore(alert, alertsContainer.firstChild);
        
        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, duration);
        }
        
        return alert;
    },
    
    showLoading(container, message = 'Loading...') {
        const loadingHTML = `
            <div class="loading-overlay">
                <div class="text-center">
                    <div class="spinner-custom mb-3"></div>
                    <p class="text-muted">${message}</p>
                </div>
            </div>
        `;
        
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        if (container) {
            container.style.position = 'relative';
            container.insertAdjacentHTML('beforeend', loadingHTML);
        }
    },
    
    hideLoading(container) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        if (container) {
            const loadingOverlay = container.querySelector('.loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.remove();
            }
        }
    },
    
    // Form handling
    async handleFormSubmission(form) {
        const formData = new FormData(form);
        const method = form.method || 'POST';
        const action = form.action;
        
        // Convert FormData to JSON if needed
        const data = {};
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        try {
            this.showLoading(form.parentElement, 'Submitting...');
            
            const response = await this.apiCall(action.replace(window.location.origin, ''), {
                method: method.toUpperCase(),
                body: JSON.stringify(data),
            });
            
            this.showNotification('Form submitted successfully!', 'success');
            
            // Trigger custom event
            form.dispatchEvent(new CustomEvent('formSubmitted', { detail: response }));
            
        } catch (error) {
            console.error('Form submission failed:', error);
            this.showNotification(`Error: ${error.message}`, 'danger');
        } finally {
            this.hideLoading(form.parentElement);
        }
    },
    
    // Card interactions
    handleCardClick(cardElement) {
        const cardId = cardElement.dataset.cardId;
        const instanceId = cardElement.dataset.instanceId;
        
        if (instanceId) {
            this.showCardInstanceDetail(instanceId);
        } else if (cardId) {
            this.showCardDetail(cardId);
        }
    },
    
    async showCardDetail(cardId) {
        // Implementation would depend on having a card detail modal
        console.log('Show card detail:', cardId);
    },
    
    async showCardInstanceDetail(instanceId) {
        // Implementation would depend on having a card instance modal
        console.log('Show card instance detail:', instanceId);
    },
    
    // Search functionality
    focusSearch() {
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i], #searchInput');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    },
    
    // Utility functions
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    throttle(func, limit) {
        let lastFunc;
        let lastRan;
        return function executedFunction(...args) {
            if (!lastRan) {
                func(...args);
                lastRan = Date.now();
            } else {
                clearTimeout(lastFunc);
                lastFunc = setTimeout(() => {
                    if ((Date.now() - lastRan) >= limit) {
                        func(...args);
                        lastRan = Date.now();
                    }
                }, limit - (Date.now() - lastRan));
            }
        };
    },
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    },
    
    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    },
    
    formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        const intervals = [
            { label: 'year', seconds: 31536000 },
            { label: 'month', seconds: 2592000 },
            { label: 'day', seconds: 86400 },
            { label: 'hour', seconds: 3600 },
            { label: 'minute', seconds: 60 },
        ];
        
        for (const interval of intervals) {
            const count = Math.floor(diffInSeconds / interval.seconds);
            if (count > 0) {
                return `${count} ${interval.label}${count !== 1 ? 's' : ''} ago`;
            }
        }
        
        return 'Just now';
    },
    
    // Image handling
    loadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = src;
        });
    },
    
    async preloadImages(urls) {
        const promises = urls.map(url => this.loadImage(url));
        return Promise.allSettled(promises);
    },
    
    // Local storage helpers
    setLocalData(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
        }
    },
    
    getLocalData(key, defaultValue = null) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : defaultValue;
        } catch (error) {
            console.error('Failed to read from localStorage:', error);
            return defaultValue;
        }
    },
    
    // URL helpers
    updateURL(params, replaceState = false) {
        const url = new URL(window.location);
        
        Object.entries(params).forEach(([key, value]) => {
            if (value === null || value === undefined || value === '') {
                url.searchParams.delete(key);
            } else {
                url.searchParams.set(key, value);
            }
        });
        
        const method = replaceState ? 'replaceState' : 'pushState';
        window.history[method]({}, '', url);
    },
    
    getURLParams() {
        return Object.fromEntries(new URLSearchParams(window.location.search));
    },
};

// Global functions for template usage
window.logout = () => CardCollector.logout();
window.showNotification = (msg, type) => CardCollector.showNotification(msg, type);

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => CardCollector.init());
} else {
    CardCollector.init();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CardCollector;
}

// Service Worker registration (if available)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
        try {
            const registration = await navigator.serviceWorker.register('/sw.js');
            console.log('SW registered: ', registration);
        } catch (registrationError) {
            console.log('SW registration failed: ', registrationError);
        }
    });
}