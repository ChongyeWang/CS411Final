window.addEventListener("load", () => {
    let firstName = document.getElementById("first_name");
    let lastName = document.getElementById("last_name");
    let email = document.getElementById("email");
    let password = document.getElementById("password");
    let confirmPassword = document.getElementById("confirm_password");

    let firstNameError = "Please enter your first name.";
    let lastNameError = "Please enter your last name.";
    let emailError = "Please enter a valid email address.";
    let passwordError = "Please enter a password of at least eight characters.";
    let confirmPasswordError = "Please confirm you password.";
    let passwordMismatchError = "The passwords must match.";

    firstName.setCustomValidity(firstNameError);
    lastName.setCustomValidity(lastNameError);
    email.setCustomValidity(emailError);
    password.setCustomValidity(passwordError);
    confirmPassword.setCustomValidity(confirmPasswordError);

    firstName.addEventListener("input", () => {
        if (firstName.validity.valueMissing)
            firstName.setCustomValidity(firstNameError);
        else firstName.setCustomValidity("");
    });

    lastName.addEventListener("input", () => {
        if (lastName.validity.valueMissing) {
            lastName.setCustomValidity(lastNameError);
        } else lastName.setCustomValidity("");
    });

    email.addEventListener("input", () => {
        if (email.validity.valueMissing) email.setCustomValidity(emailError);
        else email.setCustomValidity("");
    });

    password.addEventListener("input", () => {
        if (password.validity.valueMissing || password.validity.tooShort) {
            password.setCustomValidity(passwordError);
        } else password.setCustomValidity("");
    });

    confirmPassword.addEventListener("input", () => {
        if (confirmPassword.validity.valueMissing) {
            confirmPassword.setCustomValidity(confirmPasswordError);
        } else if (confirmPassword.value !== password.value) {
            confirmPassword.setCustomValidity(passwordMismatchError);
        } else confirmPassword.setCustomValidity("");
    });
});
