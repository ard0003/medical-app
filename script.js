// Populate symptoms dropdown
document.addEventListener("DOMContentLoaded", () => {
  const symptomSelect = document.getElementById("symptom-select");
  const warning = document.getElementById("selection-warning");

  // Fetch symptoms from the backend and populate the dropdown
  fetch("http://127.0.0.1:5000/get-symptoms")
    .then((response) => response.json())
    .then((data) => {
      if (data.symptoms) {
        data.symptoms.forEach((symptom) => {
          const option = document.createElement("option");
          option.value = symptom;
          option.textContent = symptom;
          symptomSelect.appendChild(option);
        });
      } else {
        console.error("Failed to fetch symptoms:", data.error);
      }
    })
    .catch((error) => console.error("Error fetching symptoms:", error));

  // Restrict selection to 4 symptoms
  symptomSelect.addEventListener("change", () => {
    const selectedOptions = Array.from(symptomSelect.selectedOptions);

    if (selectedOptions.length > 4) {
      warning.style.display = "block";
      // Deselect the last selected option (to limit to 4)
      selectedOptions[selectedOptions.length - 1].selected = false;
    } else {
      warning.style.display = "none";
    }
  });
});

// Handle form submission
document.getElementById("predict-btn").addEventListener("click", () => {
  const symptomSelect = document.getElementById("symptom-select");
  symptomSelect.setAttribute("multiple", "true");
  const selectedSymptoms = Array.from(symptomSelect.selectedOptions).map(
    (option) => option.value
  );
  console.log(selectedSymptoms);
  // Validate selection count
  if (selectedSymptoms.length !== 4) {
    alert("Please select exactly 4 symptoms.");
    return;
  }

  // Send symptoms to backend
  fetch("http://127.0.0.1:5000/predict-disease", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ symptoms: selectedSymptoms }),
  })
    .then((response) => response.json())
    .then((data) => {
      const resultDiv = document.getElementById("result");
      if (data.disease) {
        resultDiv.innerHTML = `
            <p><strong>Disease:</strong> ${data.disease}</p>
            <p><strong>Specialist:</strong> ${data.specialist}</p>
          `;
      } else {
        resultDiv.innerHTML = `<p><strong>Error:</strong> ${data.error}</p>`;
      }
    })
    .catch((error) => {
      console.error("Error during prediction:", error);
      document.getElementById("result").innerHTML =
        "<p>An error occurred while processing your request.</p>";
    });
});
