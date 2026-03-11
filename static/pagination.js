const rowsPerPage = 50;
  let currentPage = 1;

  document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("Table");
    const tbody = table.querySelector("tbody");
    const rows = tbody.querySelectorAll("tr");

    function showPage(page) {
      const start = (page - 1) * rowsPerPage;
      const end = start + rowsPerPage;

      rows.forEach((row, index) => {
        row.style.display = (index >= start && index < end) ? "" : "none";
      });

      renderPagination(rows.length, page);
    }

    function renderPagination(totalRows, currentPage) {
      const totalPages = Math.ceil(totalRows / rowsPerPage);
      const pagination = document.querySelector(".pagination");
      pagination.innerHTML ="";

      const prevLi = document.createElement("li");
      prevLi.className = `page-item ${currentPage === 1 ? "disabled" : ""}`;
      prevLi.innerHTML = `<a class="page-link" href="#">Précédent</a>`;
      prevLi.addEventListener("click", () => {
        if (currentPage > 1) {
          currentPage--;
          showPage(currentPage);
        }
      });
      pagination.appendChild(prevLi);

      for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement("li");
        li.className = `page-item ${i === currentPage ? "active" : ""}`;
        li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        li.addEventListener("click", () => {
          currentPage = i;
          showPage(currentPage);
        });
        pagination.appendChild(li);
      }

      const nextLi = document.createElement("li");
      nextLi.className = `page-item ${currentPage === totalPages ? "disabled" : ""}`;
      nextLi.innerHTML = `<a class="page-link" href="#">Suivant</a>`;
      nextLi.addEventListener("click", () => {
        if (currentPage < totalPages) {
          currentPage++;
          showPage(currentPage);
        }
      });
      pagination.appendChild(nextLi);
    }

    // Affiche la première page au chargement
    showPage(currentPage);
  });