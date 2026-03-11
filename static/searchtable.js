function recherchetable() {
  const searchInput = document.getElementById("champrecherche");
  const table = document.getElementById("TableauHistorique");
  const rows = table.querySelectorAll("tbody tr");

  searchInput.addEventListener("input", function () {
    const query = this.value.toLowerCase();

    rows.forEach((row) => {
      const cells = row.querySelectorAll("td");
      let found = false;

      cells.forEach((cell) => {
        if (cell.textContent.toLowerCase().includes(query)) {
          found = true;
        }
      });

      if (found) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  });
    
}