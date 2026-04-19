document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Clear and reset activity select dropdown
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <p><strong>Participants:</strong></p>
            <ul class="participants-list">
              ${details.participants.length > 0 ? details.participants.map(p => `<li>${p} <span class="delete-participant" data-email="${p}" data-activity="${name}">&times;</span></li>`).join('') : '<li>No participants yet</li>'}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add delete event listeners
        const deleteButtons = activityCard.querySelectorAll('.delete-participant');
        deleteButtons.forEach(button => {
          button.addEventListener('click', async () => {
            const email = button.dataset.email;
            const activityName = button.dataset.activity;
            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`,
                { method: 'DELETE' }
              );
              if (response.ok) {
                fetchActivities(); // Refresh activities
              } else {
                const errorData = await response.json();
                alert(`Failed to unregister: ${errorData.detail || 'Unknown error'}`);
              }
            } catch (error) {
              console.error('Error unregistering:', error);
              alert('Failed to unregister. Please try again.');
            }
          });
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
