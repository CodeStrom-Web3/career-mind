/* =========================================================
   auth.js — front-end only validation for Login / Register
   Wire the fetch() calls to your real API in services/api.js
   equivalent once the backend is ready.
   ========================================================= */

function setError(fieldEl, hasError) {
  fieldEl.classList.toggle('has-error', hasError);
}

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// ---- LOGIN ----
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    let valid = true;

    const emailOk = emailPattern.test(email.value.trim());
    setError(document.getElementById('emailField'), !emailOk);
    if (!emailOk) valid = false;

    const passOk = password.value.trim().length > 0;
    setError(document.getElementById('passwordField'), !passOk);
    if (!passOk) valid = false;

    if (!valid) return;

    showToast('Logging in…');
    setTimeout(() => { window.location.href = 'dashboard.html'; }, 900);
  });
}

// ---- REGISTER ----
const registerForm = document.getElementById('registerForm');
if (registerForm) {
  registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const fullName = document.getElementById('fullName');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    let valid = true;

    const nameOk = fullName.value.trim().length > 0;
    setError(document.getElementById('nameField'), !nameOk);
    if (!nameOk) valid = false;

    const emailOk = emailPattern.test(email.value.trim());
    setError(document.getElementById('emailField'), !emailOk);
    if (!emailOk) valid = false;

    const passOk = password.value.trim().length >= 8;
    setError(document.getElementById('passwordField'), !passOk);
    if (!passOk) valid = false;

    if (!valid) return;

    showToast('Creating your memory…');
    setTimeout(() => { window.location.href = 'dashboard.html'; }, 900);
  });
}