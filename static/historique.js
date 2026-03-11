
// Fonction pour filtrer le tableau
function filtrerActivites() {
    const dateDebutStr = document.getElementById('date-debut') ? document.getElementById('date-debut').value : '';
    const dateFinStr = document.getElementById('date-fin') ? document.getElementById('date-fin').value : '';
    const statut = document.getElementById('statut') ? document.getElementById('statut').value : 'tous';
    const section = document.getElementById('section') ? document.getElementById('section').value : 'toutes';
    const recherchetable = document.getElementById('champrecherche') ? document.getElementById('champrecherche').value : '';

    // Parse dates safely
    function parseDate(str) {
    if (!str) return null;
    str = str.trim();

    // Format ISO : YYYY-MM-DD
    if (/^\d{4}-\d{2}-\d{2}$/.test(str)) {
        const [y, m, d] = str.split("-");
        return new Date(y, m - 1, d);
    }

    // Format DD/MM/YYYY
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(str)) {
        const [d, m, y] = str.split("-");
        return new Date(y, m - 1, d);
    }

    // Fallback
    return null;
}


    const dateDebut = parseDate(dateDebutStr);
    const dateFin = parseDate(dateFinStr);

    const rows = document.querySelectorAll('#dashboard_recent_activity_list tr');

    rows.forEach(row => {
        // Colonne: 0=Nom,1=Date,2=Heure,3=Statut,4=Section,5=Action
        const nomCell = row.cells[0] ? row.cells[0].textContent.trim() : '';
        const dateCellRaw = row.cells[1] ? row.cells[1].textContent.trim() : '';
        const statutCell = row.cells[3] ? row.cells[3].textContent.trim() : '';
        const sectionCell = row.cells[4] ? row.cells[4].textContent.trim() : ''; 

        const dateCell = parseDate(dateCellRaw);

        let afficher = true;

        // Filtrer par statut
        if (statut !== 'tous' && statutCell !== statut) {
            afficher = false;
        }

        // Filtrer par date (utiliser objets Date pour comparaison)
        if (dateDebut && dateCell< dateDebut) {
            afficher = false;
        }
        if (dateFin && dateCell> dateFin) {
            afficher = false;
        }
        // // Si la ligne n'a pas de date et qu'un filtre de date est actif, masquer
        // if ((dateDebut || dateFin) && !dateCell) {
        //     afficher = false;
        // }

        // Filtrer par section
        if (section !== 'toutes' && sectionCell !== section) {
            afficher = false;
        }

        // Filtrer par recherche (insensible à la casse)
        if (recherchetable && !nomCell.toLowerCase().includes(recherchetable.toLowerCase().trim())) {
            afficher = false;
        }

        row.style.display = afficher ? '' : 'none';
    });
}

// Attacher les écouteurs d'événements lorsque le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    const dateDebutEl = document.getElementById('date-debut');
    const dateFinEl = document.getElementById('date-fin');
    const statutEl = document.getElementById('statut');
    const sectionEl = document.getElementById('section');
    const rechercheEl = document.getElementById('champrecherche');

    if (dateDebutEl) dateDebutEl.addEventListener('change', filtrerActivites);
    if (dateFinEl) dateFinEl.addEventListener('change', filtrerActivites);
    if (statutEl) statutEl.addEventListener('change', filtrerActivites);
    if (sectionEl) sectionEl.addEventListener('change', filtrerActivites);
    if (rechercheEl) rechercheEl.addEventListener('input', filtrerActivites);

    // Lancer un premier filtrage pour appliquer les valeurs initiales
    filtrerActivites();
});

