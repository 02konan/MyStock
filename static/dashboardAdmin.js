async function loadDashboardData() {
    try {
        const response = await fetch('/api/realestate/dashboard');

        if (!response.ok) throw new Error('Erreur lors du chargement des données');

        const result = await response.json();
        if (!result.success) throw new Error(result.error || 'Erreur inconnue');

        // Mise à jour des statistiques immobilières
        updateStatistics(result);
        // Liste des transactions récentes
        updateRecentTransactions(result.recent_transactions);
        // Tableau des propriétés
        updatePropertiesTable(result.properties);
        // Graphiques (revenus)
        updateRevenueChart(result.chart_revenue.map(c => c.lotissements), result.chart_revenue.map(c => c.revenue));

    } catch (error) {
        console.error('Erreur:', error);
        // showErrorNotification('Impossible de charger les données du dashboard immobilier');
    }
}

// Fonction pour mettre à jour les statistiques
function updateStatistics(data) {
    animateCounter('dash_properties-count', data.properties_count || 0);
    animateCounter('dash_tenants-count', data.tenants_count || 0);
    animateCounter('dash_monthly-income', data.monthly_income || 0);
    animateCounter('dash_ilot-count', data.ilot_count || 0);
    animateCounter('dash_localite-count', data.localite_count || 0);
    animateCounter('dash_lot-count', data.lot_count|| 0);
    animateCounter('dash_sales-count', data.sales_count|| 0);
    animateCounter('dash_vente-count', data.vente_count|| 0);

    // const occupancy = typeof data.occupancy_rate === 'number' ? data.occupancy_rate : 0;
    // document.getElementById('dash_occupancy-rate').textContent = `${occupancy}%`;
    // updateProgressBar('dash_bar-occupancy', occupancy);
}

// Fonction pour animer les compteurs
function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const duration = 1000; // 1 seconde
    const startValue = parseInt(element.textContent) || 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = Math.floor(startValue + (progress * (targetValue - startValue)));
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = targetValue;
        }
    }
    
    requestAnimationFrame(update);
}

// Fonction pour mettre à jour les barres de progression
function updateProgressBar(elementId, percentage) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const clampedPercentage = Math.min(Math.max(percentage, 0), 100);
    element.style.width = clampedPercentage + '%';
    element.setAttribute('aria-valuenow', clampedPercentage.toFixed(0));
}

// Fonction pour mettre à jour l'activité récente
function updateRecentTransactions(transactions) {
    const list = document.getElementById('dash_recent-transactions-list');
    if (!list) return;
    list.innerHTML = '';

    if (!transactions || transactions.length === 0) {
        list.innerHTML = `
            <li class="list-group-item text-center text-muted py-4">
                <i class="fas fa-inbox fa-2x mb-2"></i>
                <p class="mb-0">Aucune activité récente</p>
            </li>
        `;
        return;
    }

    transactions.forEach(tx => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.innerHTML = `
            <div>
                <strong>${tx.title || tx.type || 'Transaction'}</strong>
                <div class="small text-muted">${tx.date || ''}</div>
            </div>
            <div class="text-end">
                <div>${tx.amount ? tx.amount + 'fr' : ''}</div>
                <div class=""><code>${tx.description || ''}</code></div>
            </div>
        `;
        list.appendChild(li);
    });
}

function updatePropertiesTable(properties) {
    const tbody = document.querySelector('#dash_properties-table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!properties || properties.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">Aucune propriété trouvée</td></tr>';
        return;
    }

    properties.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${p.ilot || ''}</td>
            <td>${p.number || ''}</td>
            <td><code>${p.surface ? p.surface + ' m²' : ''}</code></td>
            <td class="text-${p.status === 'Disponible' ? 'success' : p.status === 'Vendu' ? 'danger' : 'primary'}">${p.status || ''}</td>
            <td>${p.price ? p.price + ' fr' : ''}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Variables pour les graphiques
let revenueChart = null;

function updateRevenueChart(labels = [], values = []) {
    const ctx = document.getElementById('dash_revenueChart');
    if (!ctx) return;
    if (revenueChart) revenueChart.destroy();

    revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenu',
                data: values,
                backgroundColor: 'rgba(13,110,253,0.7)'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// Fonction pour afficher une notification d'erreur
function showErrorNotification(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 end-0 m-3';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        <strong>Erreur!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}

// Fonction pour rafraîchir le dashboard
function refreshDashboard() {
    loadDashboardData();
}

// Charger les données au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    setInterval(refreshDashboard, 5 * 60 * 1000);
});

document.addEventListener('DOMContentLoaded', function() {
    const voirToutBtn = document.querySelector('.card-header button');
    if (voirToutBtn) {
        voirToutBtn.addEventListener('click', function() {
            console.log('Voir toutes les activités');
            window.location.href = '/historique-activites';
        });
    }
});
