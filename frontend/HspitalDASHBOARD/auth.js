
/* HEATCARE Demo Authentication
   For demonstration only — not secure authentication.
*/

document.addEventListener("DOMContentLoaded", function () {

    // Demo registration
    const registerForm = document.getElementById("hospitalRegisterForm");

    if (registerForm) {
        registerForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const hospitalName =
                document.getElementById("hospitalName")?.value.trim();
            const registrationNumber =
                document.getElementById("registrationNumber")?.value.trim();
            const adminName =
                document.getElementById("adminName")?.value.trim();
            const email =
                document.getElementById("hospitalEmail")?.value.trim();
            const password =
                document.getElementById("hospitalPassword")?.value;
            const confirmPassword =
                document.getElementById("confirmPassword")?.value;

            const message = document.getElementById("registerMessage");

            if (!hospitalName || !email || !password) {
                if (message) message.textContent = "Please fill in all required fields.";
                return;
            }

            if (password !== confirmPassword) {
                if (message) message.textContent = "Passwords do not match.";
                return;
            }

            // Store demo registration in this browser only.
            const demoAccount = {
                hospitalName,
                registrationNumber,
                adminName,
                email,
                password
            };

            localStorage.setItem("heatcareDemoAccount", JSON.stringify(demoAccount));

            if (message) {
                message.textContent = "Demo account created! You can now log in.";
                message.style.color = "green";
            }

            setTimeout(function () {
                window.location.href = "./login.html";
            }, 800);
        });
    }

    // Demo login
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const hospitalId =
                document.getElementById("hospitalId")?.value.trim();
            const password =
                document.getElementById("password")?.value;
            const message = document.getElementById("loginMessage");

            const savedAccount = localStorage.getItem("heatcareDemoAccount");

            if (!savedAccount) {
                if (message) {
                    message.textContent = "Please create a demo account first.";
                    message.style.color = "red";
                }
                return;
            }

            const account = JSON.parse(savedAccount);

            if (
                hospitalId.toLowerCase() === account.email.toLowerCase() &&
                password === account.password
            ) {
                sessionStorage.setItem("heatcareDemoLoggedIn", "true");
                sessionStorage.setItem("heatcareDemoHospital", account.hospitalName);

                if (message) {
                    message.textContent = "Login successful! Opening dashboard...";
                    message.style.color = "green";
                }

                setTimeout(function () {
                    window.location.href = "./dashboard.html";
                }, 500);
            } else {
                if (message) {
                    message.textContent = "Invalid email or password.";
                    message.style.color = "red";
                }
            }
        });
    }

});
