let attendanceChart = null;
let attendancePieChart = null;

function chargerDonneesDashboard() {
  fetch("/api/dashboard")
    .then(res => res.json())
    .then(data => {
      // --- ACTIVITES RECENTES ---
      if (data["activité_recentes"]) {
        afficherActivites(data["activité_recentes"]);
      }
      if (data["activité_recentes_user"]) {
        afficherActivites(data["activité_recentes_user"]);
      }

      // --- CHARTS ---
      if (data.total_eleves !== undefined) {
        afficherChartsAdmin(data);
      } else if (data.pointage !== undefined) {
        afficherChartsProf(data);
      }

      // --- COMPTEURS ---
      const counters = [
        ["presents-count", data.presents],
        ["absents-count", data.absents],
        ["retard-count", data.retard],
        ["total-eleves", data.total_eleves],
        ["presents-prof", data.presents_user],
        ["absents-prof", data.absents_user],
        ["retard-prof", data.retard_user],
        ["new-pointage", data.pointage]
      ];

      counters.forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value ?? 0;
      });

      // --- BARRES DE PROGRESSION ---
      const bars = [
        ["bar-present", data.pourcentage_presents ?? data.pourcentage_presents_user],
        ["bar-absent", data.pourcentage_absents ?? data.pourcentage_absents_user],
        ["bar-retard", data.pourcentage_retards ?? data.pourcentage_retards_user]
      ];

      bars.forEach(([id, pct]) => {
        const el = document.getElementById(id);
        if (el) el.style.width = (pct ?? 0) + "%";
      });

      // --- COMPTEURS MENSUELS (admin uniquement) ---
      if (data.total_eleves !== undefined) {
        const moisCounters = [
          ["presence-mois-count", data.employes_actifs_mois],
          ["absence-mois-count", data.total_eleves - (data.employes_actifs_mois ?? 0)],
          ["retard-mois-count", data.employes_retard_mois],
          ["new-employee-count", 0]
        ];

        moisCounters.forEach(([id, value]) => {
          const el = document.getElementById(id);
          if (el) el.textContent = value ?? 0;
        });
      }
    })
    .catch(error => console.error("Erreur lors du chargement du dashboard :", error));
}

function afficherActivites(activites) {
  const container = document.getElementById("recent-activity-list");
  if (!container) return;
  container.innerHTML = "";

  activites.forEach(([id, date, Status,NomSection]) => {
    const couleur = Status === "Arrivée enregistrée" ? "badge bg-success" : "badge bg-danger";

    const item = document.createElement("li");
    item.className = "list-group-item d-flex justify-content-between align-items-center p-3";
    item.innerHTML = `
      <div class="d-flex align-items-center">
         <div class="avatar me-2">
            <img src="static/images/icons8-life-cycle-96.png" alt="">
         </div>
        <div>
          <h6 class="mb-0">${id}</h6>
          <small class="${couleur}">${Status}</small>
        </div>
      </div>
      <div>
          <h6 class="mb-0">${new Date(date).toLocaleString()}</h6>
          <small class="text-primary">${NomSection}</small>
      </div>
    `;
    container.appendChild(item);
  });
}

function afficherChartsAdmin(data) {
  const lineCanvas = document.getElementById("attendanceChart");
  const pieCanvas = document.getElementById("attendancePieChart");
  if (!lineCanvas || !pieCanvas) return;

  if (attendanceChart) attendanceChart.destroy();
  if (attendancePieChart) attendancePieChart.destroy();

  // --- CHART LINE ---
  const ctxLine = lineCanvas.getContext("2d");
  attendanceChart = new Chart(ctxLine, {
    type: "line",
    data: {
      labels: ["Présents", "Absents", "Retards"],
      datasets: [{
        label: "Statistiques du jour",
        data: [data.presents ?? 0, data.absents ?? 0, data.retard ?? 0],
        backgroundColor: "rgba(54, 162, 235, 0.2)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: { responsive: true }
  });

  // --- CHART PIE ---
  const ctxPie = pieCanvas.getContext("2d");
  attendancePieChart = new Chart(ctxPie, {
    type: "pie",
    data: {
      labels: ["Présents", "Absents", "Retards"],
      datasets: [{
        label: "Répartition",
        data: [
          data.pourcentage_presents ?? 0,
          data.pourcentage_absents ?? 0,
          data.pourcentage_retards ?? 0
        ],
        backgroundColor: [
          "rgba(54, 162, 235, 0.7)",
          "rgba(255, 99, 132, 0.7)",
          "rgba(255, 206, 86, 0.7)"
        ]
      }]
    },
    options: { responsive: true, plugins: { legend: { position: "bottom" } } }
  });
}

function afficherChartsProf(data) {
  const lineCanvas = document.getElementById("attendanceChart");
  if (!lineCanvas) return;

  if (attendanceChart) attendanceChart.destroy();

  const ctxLine = lineCanvas.getContext("2d");
  attendanceChart = new Chart(ctxLine, {
    type: "line",
    data: {
      labels: ["Présents", "Absents", "Retards"],
      datasets: [{
        label: "Statistiques du jour (Professeur)",
        data: [data.presents_user ?? 0, data.absents_user ?? 0, data.retard_user ?? 0],
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: { responsive: true }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  chargerDonneesDashboard();
  setInterval(chargerDonneesDashboard, 10000);
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
