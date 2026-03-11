function chargerDonneesProf() {
  fetch("/api/profdashboard")
    .then(res => res.json())
    .then(data => {
      afficherActivites(data["activité_recentes"]);
      afficherCharts(data);

       // MISE À JOUR DES COMPTEURS QUOTIDIENS (existants)
      document.getElementById("presents-prof").textContent = data.presents;
      document.getElementById("absents-prof").textContent = data.absents;
      document.getElementById("retard-prof").textContent = data.retard;
      document.getElementById("new-pointage").textContent = data.pointage;
    //   MISE À JOUR DES BARRES DE PROGRESSION QUOTIDIENNES (existantes)
      document.getElementById("bar-present").style.width = data.pourcentage_presents + "%";
      document.getElementById("bar-absent").style.width = data.pourcentage_absents + "%";
      document.getElementById("bar-retard").style.width = data.pourcentage_retards + "%";
    //   document.getElementById("bar-retard").style.width = data.pourcentage_retards + "%";
      
      
    })
    .catch(error =>
      console.error("Erreur lors du chargement du dashboard :", error)
    );
}

function afficherActivites(activites) {
  const container = document.getElementById("recent-activity-list");
  container.innerHTML = "";

  activites.forEach(([id, date,Status]) => {
    let couleur=""
    if (Status==="Arrivée enregistrée") {
      couleur="badge bg-success"
    }else{
      couleur="badge bg-danger"
    }

    const item = document.createElement("li");
    item.className =
      "list-group-item d-flex justify-content-between align-items-center p-3";
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
      <span class="text-muted">${new Date(date).toLocaleString()}</span>
    `;
    container.appendChild(item);
  });
}

function afficherCharts(data) {
  const ctxLine = document.getElementById("attendanceChart").getContext("2d");
  new Chart(ctxLine, {
    type: "line",
    data: {
      labels: ["Présents", "Absents", "Retards"],
      datasets: [
        {
          label: "Statistiques du jour",
          data: [data.presents, data.absents, data.retard],
          backgroundColor: "rgba(54, 162, 235, 0.2)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 2,
          fill: true,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        }
      }
    }
  });
}


document.addEventListener("DOMContentLoaded", () => {
  chargerDonneesDashboard();
  setInterval(chargerDonneesDashboard, 5000); // recharge toutes les 5s
});
