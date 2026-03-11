document.addEventListener("DOMContentLoaded", () => {

  fetch("/api/liste_rapports")
    .then(res => res.json())
    .then(liste => liste.forEach(ajouterLigneRapport));

  function ajouterLigneRapport(data) {
    const ligne = document.createElement("tr");
    ligne.innerHTML = `
      <td><code>${data.projet}</code></td>
      <td>${data.type}</td>
      <td><code>${data.numero}</code></td>
      <td><code>${data.date}</code></td>
      <td>
        <a href="/telechargement/${encodeURIComponent(data.nom)}" class="btn btn-sm btn-outline-primary me-1">
          <i class="fas fa-download"></i>
        </a>
        <a href="/impression/${encodeURIComponent(data.nom)}" target="_blank" class="btn btn-sm btn-outline-secondary me-1">
          <i class="fas fa-print"></i>
        </a>
      </td>
    `;
    document.getElementById("table-rapports").prepend(ligne);
  }

  // Suppression d’un rapport
  window.supprimerRapport = function(nom, btn) {
    if (!confirm("Voulez-vous vraiment supprimer ce rapport ?")) return;
    fetch(`/suppression/${encodeURIComponent(nom)}`, { method: "DELETE" })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const ligne = btn.closest("tr");
          ligne.remove();
        }
      });
  };

  // Bouton de génération de rapport
  const btnGenerer = document.getElementById("btn-fiche-presence");
  btnGenerer.addEventListener("click", () => {
    const dateDebut = document.getElementById("date_debut").value;
    const dateFin = document.getElementById("date_fin").value;
    const employeeid = document.getElementById("idEmploye").value;

    if (!dateDebut || !dateFin) {
      alert("Veuillez sélectionner une date de début et une date de fin.");
      return;
    }

    // Afficher le spinner / message
    btnGenerer.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Génération en cours...';
    btnGenerer.disabled = true;

    fetch("/api/fiche_presence", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date_debut: dateDebut, date_fin: dateFin, idEmploye: employeeid})
    })
    .then(async response => {
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Erreur lors de la génération du rapport");
      ajouterLigneRapport({
        nom: result.nom,
        type: result.type,
        auteur: result.auteur,
        date: result.date
      });
      alert(`Rapport généré avec succès : ${result.nom}`);
    })
    .finally(() => {
      // Réinitialiser le bouton
      btnGenerer.innerHTML = '<i class="fas fa-file-pdf me-2"></i>Générer le rapport';
      btnGenerer.disabled = false;
    });
  });

});


    const btnGenereradmin = document.getElementById("btn-fiche-presence-admin");
    btnGenereradmin.addEventListener("click", () => {
      const dateDebut_admin = document.getElementById("date_debut_admin").value;
      const dateFin_admin = document.getElementById("date_fin_admin").value;
      const employeeid_admin = document.getElementById("idEmploye_admin").value;
      const section_admin =document.getElementById("sectionid").value;

      if (!dateDebut_admin || !dateFin_admin) {
      NotificationMsg("Erreur!","Veuillez sélectionner une date de début et une date de fin.","alert-danger");
      return;
    }
      
      btnGenereradmin.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Génération en cours...';
      btnGenereradmin.disabled = true;
      setInterval(() => {
        location.reload()
      }, 5000);

      fetch("/api/fiche_presence_admin", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          date_admin_debut: dateDebut_admin,
          date_admin_fin: dateFin_admin,
          employeeid_admin: employeeid_admin,
          section_admin: section_admin
        })
      }).then(response=>response.json()).then(
        data=>{
          if (data.success) {
            NotificationMsg("Valider.",data.error,"alert-success")
          } else {
            NotificationMsg("Erreur!",data.error,"alert-danger")
          }
        }
      );
    });

    function NotificationMsg(ctgmessage,message,couleur) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${couleur} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        <strong>${ctgmessage}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}

    // document.getElementById("form-fiche-absences")
    // .addEventListener("click", () => {
    //   const dateDebutabsence = document.getElementById("date_debut_absence").value;
    //   const dateFinabsence = document.getElementById("date_fin_absence").value;

    //   fetch("/api/fiche_absence", {
    //     method: "POST",
    //     headers: {
    //       "Content-Type": "application/json"
    //     },
    //     body: JSON.stringify({
    //       date_debut_absence: dateDebutabsence,
    //       date_fin_absence: dateFinabsence
    //     })
    //   });
    // });

     document.getElementById("form-fiche-persornalise")
    .addEventListener("click", () => {
      const Matricule = document.getElementById("matricule").value;
      fetch("/api/fiche_presence_unique", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          Matricule: Matricule
        })
      });
    });

