// Point this at your deployed prod API Gateway endpoint
const API_BASE_URL = "https://7m5e7ocgj9.execute-api.us-east-1.amazonaws.com/prod";

const eventSelect = document.getElementById("event-select");
const eventsList = document.getElementById("events-list");
const registerForm = document.getElementById("register-form");
const registerMessage = document.getElementById("register-message");
const lookupForm = document.getElementById("lookup-form");
const registrationsList = document.getElementById("registrations-list");

let cachedEvents = [];

function statusBadgeClass(event) {
  if (event.registeredCount >= event.capacity) return "full";
  if (event.registeredCount / event.capacity >= 0.8) return "limited";
  return "available";
}

function statusLabel(event) {
  if (event.registeredCount >= event.capacity) return "Full";
  if (event.registeredCount / event.capacity >= 0.8) return "Limited";
  return "Available";
}

async function loadEvents() {
  eventsList.innerHTML = '<p class="loading">Loading events...</p>';
  try {
    const res = await fetch(`${API_BASE_URL}/events`);
    const data = await res.json();
    cachedEvents = data.events || [];

    if (cachedEvents.length === 0) {
      eventsList.innerHTML = '<p class="empty">No events available right now.</p>';
      eventSelect.innerHTML = "";
      return;
    }

    eventsList.innerHTML = cachedEvents
      .map(
        (evt) => `
        <div class="event-item">
          <div>
            <div class="name">${escapeHtml(evt.eventName)}</div>
            <div class="date">${evt.eventDate}</div>
          </div>
          <span class="badge ${statusBadgeClass(evt)}">${statusLabel(evt)}</span>
        </div>
      `
      )
      .join("");

    eventSelect.innerHTML = cachedEvents
      .map((evt) => `<option value="${evt.eventId}">${escapeHtml(evt.eventName)}</option>`)
      .join("");
  } catch (err) {
    eventsList.innerHTML = '<p class="empty">Failed to load events. Please try again later.</p>';
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const eventId = eventSelect.value;
  const email = document.getElementById("email-input").value.trim();

  registerMessage.textContent = "";
  registerMessage.className = "message";

  const submitBtn = registerForm.querySelector("button");
  submitBtn.disabled = true;

  try {
    const res = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ eventId, email }),
    });
    const data = await res.json();

    if (res.ok) {
      registerMessage.textContent = `Registered successfully! Confirmation ID: ${data.registrationId}`;
      registerMessage.classList.add("success");
      document.getElementById("email-input").value = "";
      loadEvents();
    } else {
      registerMessage.textContent = data.error || "Registration failed.";
      registerMessage.classList.add("error");
    }
  } catch (err) {
    registerMessage.textContent = "Network error. Please try again.";
    registerMessage.classList.add("error");
  } finally {
    submitBtn.disabled = false;
  }
});

lookupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("lookup-email").value.trim();

  registrationsList.innerHTML = '<p class="loading">Looking up registrations...</p>';

  try {
    const res = await fetch(`${API_BASE_URL}/registrations/${encodeURIComponent(email)}`);
    const data = await res.json();

    if (!res.ok) {
      registrationsList.innerHTML = `<p class="empty">${data.error || "Lookup failed."}</p>`;
      return;
    }

    if (data.registrations.length === 0) {
      registrationsList.innerHTML = '<p class="empty">No registrations found for this email.</p>';
      return;
    }

    registrationsList.innerHTML = data.registrations
      .map((reg) => {
        const evt = cachedEvents.find((e) => e.eventId === reg.eventId);
        const eventName = evt ? evt.eventName : reg.eventId;
        const isCancelled = reg.status === "cancelled";
        return `
          <div class="registration-item">
            <div>
              <div class="name">${escapeHtml(eventName)}</div>
              <div class="date">${new Date(reg.registeredAt).toLocaleDateString()}</div>
            </div>
            <span class="badge ${reg.status}">${reg.status}</span>
            ${
              !isCancelled
                ? `<button class="cancel-btn" data-id="${reg.registrationId}">Cancel</button>`
                : ""
            }
          </div>
        `;
      })
      .join("");

    document.querySelectorAll(".cancel-btn").forEach((btn) => {
      btn.addEventListener("click", () => cancelRegistration(btn.dataset.id, email));
    });
  } catch (err) {
    registrationsList.innerHTML = '<p class="empty">Network error. Please try again.</p>';
  }
});

async function cancelRegistration(registrationId, email) {
  try {
    const res = await fetch(`${API_BASE_URL}/registration/${registrationId}`, {
      method: "DELETE",
    });
    if (res.ok) {
      lookupForm.dispatchEvent(new Event("submit"));
      loadEvents();
    }
  } catch (err) {
    alert("Failed to cancel registration.");
  }
}

loadEvents();
