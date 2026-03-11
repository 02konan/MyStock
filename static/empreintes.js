document.addEventListener("DOMContentLoaded", () => {
    function capturerEmpreinte() {
  const userId = document.querySelector('input[name="idEmploye"]').value;

  if (!userId) {
    alert("Veuillez d'abord renseigner l'ID Employé.");
    return;
  }

  fetch('/enregistrer-empreinte', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ user_id: userId, ip: '192.168.1.201' })  // À adapter selon ton réseau
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("empreinte_message").textContent = data.message;
    if (data.status === "success") {
      document.getElementById("empreinte_status").value = "enregistrée";
      document.getElementById("empreinte_message").classList.remove("text-danger");
      document.getElementById("empreinte_message").classList.add("text-success");
    } else {
      document.getElementById("empreinte_status").value = "non_enregistrée";
      document.getElementById("empreinte_message").classList.remove("text-success");
      document.getElementById("empreinte_message").classList.add("text-danger");
    }
  })
  .catch(() => {
    document.getElementById("empreinte_message").textContent = "Erreur de communication avec la pointeuse.";
    document.getElementById("empreinte_message").classList.add("text-danger");
  });
}
});