// Function to handle menu clicks and show the respective section
document.querySelectorAll('.menu-item').forEach(menuItem => {
    menuItem.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent default anchor behavior

        // Get the text content of the clicked menu item
        const sectionId = this.textContent.toLowerCase();

        // Hide all sections
        document.querySelectorAll('.container').forEach(section => {
            section.style.display = 'none';
        });

        // If Home is clicked, show the Home section and reset the result section
        if (sectionId === 'home') {
            const homeSection = document.getElementById('Home');
            homeSection.style.display = 'block';

            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'none';  // Keep result hidden when coming back to Home
            resultDiv.textContent = '';  // Clear any previous result text
        } else {
            // For About and Contact, show those sections
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.style.display = 'block';
            }
        }
    });
});

// Function to handle Predict button click
document.getElementById('predict-btn').addEventListener('click', function () {
    const selectedOptions = Array.from(document.querySelector('select').selectedOptions)
        .map(option => option.text)
        .join(', ');

    const resultDiv = document.getElementById('result');
    if (selectedOptions) {
        resultDiv.textContent = `You have selected: ${selectedOptions}`;
    } else {
        resultDiv.textContent = 'Please select at least one symptom.';
    }
    resultDiv.style.display = 'block';  // Display the result section
});