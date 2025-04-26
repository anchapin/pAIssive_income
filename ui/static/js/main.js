/**
 * pAIssive Income Framework UI
 * Main JavaScript file for the web interface
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            
            sidebar.classList.toggle('active');
            content.classList.toggle('active');
        });
    }
    
    // Auto-close alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
        
        const closeBtn = alert.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.style.display = 'none';
                }, 300);
            });
        }
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Opportunity score color coding
    const opportunityScores = document.querySelectorAll('.opportunity-score .score');
    opportunityScores.forEach(function(score) {
        const value = parseFloat(score.textContent);
        if (value >= 0.8) {
            score.style.color = '#28a745'; // Success/green
        } else if (value >= 0.6) {
            score.style.color = '#17a2b8'; // Info/blue
        } else if (value >= 0.4) {
            score.style.color = '#ffc107'; // Warning/yellow
        } else {
            score.style.color = '#dc3545'; // Danger/red
        }
    });
    
    // Initialize any charts
    initializeCharts();
    
    // Initialize any data tables
    initializeDataTables();
    
    console.log('pAIssive Income Framework UI initialized');
});

/**
 * Initialize charts for the dashboard
 */
function initializeCharts() {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not available. Charts will not be rendered.');
        return;
    }
    
    // Example: Niche Opportunity Chart
    const nicheOpportunityChart = document.getElementById('nicheOpportunityChart');
    if (nicheOpportunityChart) {
        new Chart(nicheOpportunityChart, {
            type: 'bar',
            data: {
                labels: ['E-commerce', 'Content Creation', 'Freelancing', 'Education', 'Real Estate'],
                datasets: [{
                    label: 'Opportunity Score',
                    data: [0.85, 0.82, 0.78, 0.75, 0.80],
                    backgroundColor: [
                        'rgba(74, 108, 247, 0.7)',
                        'rgba(74, 108, 247, 0.7)',
                        'rgba(74, 108, 247, 0.7)',
                        'rgba(74, 108, 247, 0.7)',
                        'rgba(74, 108, 247, 0.7)'
                    ],
                    borderColor: [
                        'rgba(74, 108, 247, 1)',
                        'rgba(74, 108, 247, 1)',
                        'rgba(74, 108, 247, 1)',
                        'rgba(74, 108, 247, 1)',
                        'rgba(74, 108, 247, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
    }
    
    // Example: Revenue Projection Chart
    const revenueProjectionChart = document.getElementById('revenueProjectionChart');
    if (revenueProjectionChart) {
        new Chart(revenueProjectionChart, {
            type: 'line',
            data: {
                labels: ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6', 'Month 7', 'Month 8', 'Month 9', 'Month 10', 'Month 11', 'Month 12'],
                datasets: [{
                    label: 'Revenue',
                    data: [500, 800, 1200, 1800, 2500, 3200, 4000, 4800, 5600, 6400, 7200, 8000],
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 2,
                    tension: 0.4
                },
                {
                    label: 'Expenses',
                    data: [400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500],
                    backgroundColor: 'rgba(220, 53, 69, 0.2)',
                    borderColor: 'rgba(220, 53, 69, 1)',
                    borderWidth: 2,
                    tension: 0.4
                },
                {
                    label: 'Profit',
                    data: [100, 300, 600, 1100, 1700, 2300, 3000, 3700, 4400, 5100, 5800, 6500],
                    backgroundColor: 'rgba(74, 108, 247, 0.2)',
                    borderColor: 'rgba(74, 108, 247, 1)',
                    borderWidth: 2,
                    tension: 0.4
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

/**
 * Initialize data tables
 */
function initializeDataTables() {
    // Check if DataTable is available
    if (typeof $.fn.DataTable === 'undefined') {
        console.warn('DataTables not available. Tables will not be enhanced.');
        return;
    }
    
    // Initialize any tables with the 'datatable' class
    $('.datatable').DataTable({
        responsive: true,
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]]
    });
}
