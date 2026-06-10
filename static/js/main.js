// Main visual script for Adarsh Cinemas
document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss alerts after 4 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            // Check if alert is still in DOM and fade it out
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.6s ease';
                setTimeout(() => alert.remove(), 600);
            }
        }, 4000);
    });

    // 2. Tab selection persistent routing (admin page)
    const hash = window.location.hash;
    if (hash) {
        const triggerEl = document.querySelector(`.nav-tabs-admin a[href="${hash}"]`);
        if (triggerEl) {
            // Trigger Bootstrap Tab toggle
            const tab = new bootstrap.Tab(triggerEl);
            tab.show();
        }
    }
});

// Admin Charting Wrapper Function
function renderAdminCharts() {
    const revenueCanvas = document.getElementById('revenueTrendChart');
    const bookingsCanvas = document.getElementById('dailyBookingsChart');
    const popularCanvas = document.getElementById('popularMoviesChart');

    if (!revenueCanvas || !bookingsCanvas || !popularCanvas) return;

    // Fetch statistics data from REST API
    fetch('/admin/api/analytics')
        .then(res => res.json())
        .then(data => {
            // 1. Revenue Line Chart
            new Chart(revenueCanvas, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Revenue (INR)',
                        data: data.revenue_trend,
                        borderColor: '#E50914',
                        backgroundColor: 'rgba(229, 9, 20, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#FFFFFF',
                        pointBorderColor: '#E50914',
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#94A3B8' } },
                        x: { grid: { display: false }, ticks: { color: '#94A3B8' } }
                    }
                }
            });

            // 2. Bookings Bar Chart
            new Chart(bookingsCanvas, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Tickets Booked',
                        data: data.daily_bookings,
                        backgroundColor: '#3B82F6',
                        borderRadius: 6,
                        barThickness: 20
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.06)' }, ticks: { color: '#94A3B8', precision: 0 } },
                        x: { grid: { display: false }, ticks: { color: '#94A3B8' } }
                    }
                }
            });

            // 3. Popular Movies Pie/Doughnut Chart
            new Chart(popularCanvas, {
                type: 'doughnut',
                data: {
                    labels: data.popular_labels,
                    datasets: [{
                        data: data.popular_values,
                        backgroundColor: [
                            '#E50914',
                            '#3B82F6',
                            '#10B981',
                            '#F59E0B',
                            '#8B5CF6'
                        ],
                        borderWidth: 1,
                        borderColor: '#1E293B'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#FFFFFF', boxWidth: 12, padding: 15 }
                        }
                    }
                }
            });
        })
        .catch(err => console.error("Error drawing charts:", err));
}
