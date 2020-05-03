window.addEventListener("load", () => {
    let email = document.getElementById("email");
    let password = document.getElementById("password");

    let emailError = "Please enter your email.";
    let passwordError = "Please enter your password.";

    email.setCustomValidity(emailError);
    password.setCustomValidity(passwordError);

    email.addEventListener("input", () => {
        if (email.validity.valueMissing) email.setCustomValidity(emailError);
        else email.setCustomValidity("");
    });

    password.addEventListener("input", () => {
        if (password.validity.valueMissing || password.validity.tooShort) {
            password.setCustomValidity(passwordError);
        } else password.setCustomValidity("");
    });
});
