function showForm(type) {
    let loginForm = document.getElementById("login-form");
    let registerForm = document.getElementById("register-form");

    if (type === "login") {
        loginForm.classList.remove("hidden");
        registerForm.classList.add("hidden");
    } else {
        registerForm.classList.remove("hidden");
        loginForm.classList.add("hidden");
    }
}