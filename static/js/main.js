// Medicine Stock Management System - Main JavaScript

// Global variables
let currentUser = null;
let csrfToken = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Get CSRF token
    csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    // Initialize components
    initializeNavigation();
    initializeModals();
    initializeTooltips();
    initializeAlerts();
    initializeFormValidation();
    initializeDataTables();
    initializeCharts();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(hideAlerts, 5000);
}

// Navigation Functions
function initializeNavigation() {
    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && 
                !sidebar.contains(e.target) && 
                !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
    
    // Active navigation highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Modal Functions
function initializeModals() {
    // Reset forms when modals are hidden
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
                clearFormErrors(form);
            }
        });
    });
}

// Tooltip initialization
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Alert Functions
function initializeAlerts() {
    // Make alerts dismissible
    const alerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
    alerts.forEach(alert => {
        alert.classList.add('alert-dismissible');
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'btn-close';
        closeBtn.setAttribute('data-bs-dismiss', 'alert');
        closeBtn.setAttribute('aria-label', 'Close');
        alert.appendChild(closeBtn);
    });
}

function hideAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    });
}

function showAlert(message, type = 'info', permanent = false) {
    const alertContainer = document.getElementById('alert-container') || document.body;
    const alertDiv = document.createElement('div');
    
    alertDiv.className = `alert alert-${type} alert-dismissible fade show ${permanent ? 'alert-permanent' : ''}`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
    
    if (!permanent) {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function clearFormErrors(form) {
    // Clear validation classes
    form.classList.remove('was-validated');
    
    // Clear error messages
    const errorElements = form.querySelectorAll('.invalid-feedback, .error-message');
    errorElements.forEach(element => element.remove());
    
    // Reset field states
    const fields = form.querySelectorAll('.form-control, .form-select');
    fields.forEach(field => {
        field.classList.remove('is-invalid', 'is-valid');
    });
}

function displayFormErrors(form, errors) {
    clearFormErrors(form);
    
    Object.keys(errors).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.classList.add('is-invalid');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = errors[fieldName][0]; // First error message
            
            field.parentNode.appendChild(errorDiv);
        }
    });
}

// AJAX Functions
function makeAjaxRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    return fetch(url, finalOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('AJAX request failed:', error);
            showAlert('An error occurred. Please try again.', 'danger');
            throw error;
        });
}

function submitFormAjax(form, successCallback = null, errorCallback = null) {
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    
    // Show loading state
    const submitBtn = form.querySelector('[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (successCallback) {
                successCallback(data);
            } else {
                showAlert(data.message || 'Operation completed successfully!', 'success');
                // Close modal if form is in a modal
                const modal = form.closest('.modal');
                if (modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    bsModal.hide();
                }
                // Refresh page after a short delay
                setTimeout(() => window.location.reload(), 1000);
            }
        } else {
            if (data.errors) {
                displayFormErrors(form, data.errors);
            }
            if (errorCallback) {
                errorCallback(data);
            } else {
                showAlert(data.message || 'Please correct the errors below.', 'danger');
            }
        }
    })
    .catch(error => {
        console.error('Form submission error:', error);
        if (errorCallback) {
            errorCallback({ message: 'An error occurred. Please try again.' });
        } else {
            showAlert('An error occurred. Please try again.', 'danger');
        }
    })
    .finally(() => {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

// Data Table Functions
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        // Add search functionality
        const searchInput = table.parentElement.querySelector('.table-search');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                filterTable(table, this.value);
            });
        }
        
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, this.cellIndex, this.dataset.sortType || 'string');
            });
        });
    });
}

function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

function sortTable(table, columnIndex, sortType) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        if (sortType === 'number') {
            return parseFloat(aValue) - parseFloat(bValue);
        } else if (sortType === 'date') {
            return new Date(aValue) - new Date(bValue);
        } else {
            return aValue.localeCompare(bValue);
        }
    });
    
    rows.forEach(row => tbody.appendChild(row));
}

// Chart Functions
function initializeCharts() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeDashboardCharts();
    }
}

function initializeDashboardCharts() {
    // Stock levels chart
    const stockChart = document.getElementById('stockChart');
    if (stockChart) {
        new Chart(stockChart, {
            type: 'doughnut',
            data: {
                labels: ['In Stock', 'Low Stock', 'Out of Stock'],
                datasets: [{
                    data: [65, 25, 10],
                    backgroundColor: ['#059669', '#d97706', '#dc2626']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // Sales trend chart
    const salesChart = document.getElementById('salesChart');
    if (salesChart) {
        new Chart(salesChart, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Sales',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// Utility Functions
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options })
        .format(new Date(date));
}

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

// Confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function confirmDelete(itemName, deleteUrl) {
    const message = `Are you sure you want to delete "${itemName}"? This action cannot be undone.`;
    
    if (confirm(message)) {
        // Show loading state
        const deleteBtn = event.target;
        deleteBtn.disabled = true;
        deleteBtn.textContent = 'Deleting...';
        
        fetch(deleteUrl, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message || 'Item deleted successfully!', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showAlert(data.message || 'Failed to delete item.', 'danger');
                deleteBtn.disabled = false;
                deleteBtn.textContent = 'Delete';
            }
        })
        .catch(error => {
            console.error('Delete error:', error);
            showAlert('An error occurred while deleting.', 'danger');
            deleteBtn.disabled = false;
            deleteBtn.textContent = 'Delete';
        });
    }
}

// Export functions for global use
window.MedicineStock = {
    showAlert,
    hideAlerts,
    makeAjaxRequest,
    submitFormAjax,
    confirmAction,
    confirmDelete,
    formatCurrency,
    formatDate,
    debounce
};