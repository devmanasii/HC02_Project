
/* =========================================================
   HEATCARE - HOSPITAL DEMAND INTELLIGENCE
   Complete updated script.js

   Features:
   - Manual hospital data entry (7 fields)
   - Hospital Overview
   - Category-wise bed availability
   - Save and restore values using localStorage
   - Live weather
   - Flask backend status
   - Hospital attendance data
   - Prediction history
   - AI demand prediction
   - Demo login and registration validation
========================================================= */

"use strict";

/* =========================================================
   CONFIGURATION
========================================================= */

const API_BASE_URL = "http://127.0.0.1:5000";
const HOSPITAL_DATA_STORAGE_KEY = "heatcare_manual_hospital_data";

/* =========================================================
   GENERAL HELPERS
========================================================= */

function getElement(id) {
    return document.getElementById(id);
}

function setText(id, value) {
    const element = getElement(id);

    if (element) {
        element.textContent = value;
    }
}

function setMessage(id, message, type = "info") {
    const element = getElement(id);

    if (!element) return;

    element.textContent = message;
    element.className = `form-message ${type}`;
}

function formatNumber(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return new Intl.NumberFormat("en-IN", {
        maximumFractionDigits: 2
    }).format(number);
}

function formatDate(value) {
    if (!value) return "—";

    // Avoid timezone shifts for YYYY-MM date strings.
    const text = String(value);

    if (/^\d{4}-\d{2}$/.test(text)) {
        const [year, month] = text.split("-").map(Number);
        return new Date(year, month - 1, 1).toLocaleDateString("en-IN", {
            year: "numeric",
            month: "short"
        });
    }

    if (/^\d{4}-\d{2}-\d{2}$/.test(text)) {
        const [year, month, day] = text.split("-").map(Number);
        return new Date(year, month - 1, day).toLocaleDateString("en-IN", {
            year: "numeric",
            month: "short"
        });
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return text;
    }

    return date.toLocaleDateString("en-IN", {
        year: "numeric",
        month: "short"
    });
}

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            ...(options.body
                ? { "Content-Type": "application/json" }
                : {}),
            ...(options.headers || {})
        }
    });

    const contentType = response.headers.get("content-type") || "";
    let data;

    if (contentType.includes("application/json")) {
        data = await response.json();
    } else {
        data = await response.text();
    }

    if (!response.ok) {
        const message =
            typeof data === "object" && data !== null
                ? data.error || data.message
                : data;

        throw new Error(message || `Request failed: ${response.status}`);
    }

    return data;
}

/* =========================================================
   MANUAL HOSPITAL DATA
========================================================= */

/*
Required HTML IDs:
manualTotalBeds
manualAvailableBeds
manualOccupiedBeds
manualAdmittedPatients
manualICUBeds
manualGeneralBeds
manualOtherBeds

The three category fields are required for the form to work.
*/

function getManualHospitalFields() {
    return [
        "manualTotalBeds",
        "manualAvailableBeds",
        "manualOccupiedBeds",
        "manualAdmittedPatients",
        "manualICUBeds",
        "manualGeneralBeds",
        "manualOtherBeds"
    ];
}

function readManualHospitalForm() {
    const values = {};

    for (const id of getManualHospitalFields()) {
        const input = getElement(id);

        if (!input) {
            throw new Error(
                `The form field "${id}" was not found in dashboard.html.`
            );
        }

        const rawValue = input.value.trim();

        if (rawValue === "") {
            input.focus();
            throw new Error(
                "Please enter values in all seven hospital data fields."
            );
        }

        const value = Number(rawValue);

        if (!Number.isSafeInteger(value) || value < 0) {
            input.focus();
            throw new Error(
                "Enter non-negative whole numbers in all seven fields."
            );
        }

        values[id] = value;
    }

    return values;
}

function validateManualHospitalData(values) {
    const total = values.manualTotalBeds;
    const available = values.manualAvailableBeds;
    const occupied = values.manualOccupiedBeds;
    const admitted = values.manualAdmittedPatients;

    const icu = values.manualICUBeds;
    const general = values.manualGeneralBeds;
    const special = values.manualOtherBeds;

    if (total < 1) {
        return "Total beds must be at least 1.";
    }

    if (available + occupied !== total) {
        return "Available beds plus occupied beds must equal total beds.";
    }

    if (admitted > occupied) {
        return "Admitted patients cannot exceed occupied beds.";
    }

    if (icu + general + special > available) {
        return (
            "The combined ICU, General Ward and Special Room available beds " +
            "cannot exceed overall available beds."
        );
    }

    return null;
}

function updateHospitalOverview(values) {
    const cardUpdates = {
        totalBeds: values.manualTotalBeds,
        availableBeds: values.manualAvailableBeds,
        occupiedBeds: values.manualOccupiedBeds,
        admittedPatients: values.manualAdmittedPatients
    };

    for (const [id, value] of Object.entries(cardUpdates)) {
        setText(id, formatNumber(value));
    }

    [
        "totalBedsStatus",
        "availableBedsStatus",
        "occupiedBedsStatus",
        "admittedPatientsStatus"
    ].forEach((id) => {
        setText(id, "Manually entered");
    });

    setText(
        "hospitalUpdated",
        `Hospital information updated: ${new Date().toLocaleString("en-IN")}`
    );
}

function updateBedMonitoring(values) {
    setText("availableICUBeds", formatNumber(values.manualICUBeds));
    setText("availableGeneralBeds", formatNumber(values.manualGeneralBeds));
    setText("availableOtherBeds", formatNumber(values.manualOtherBeds));

    setText(
        "bedMonitoringStatus",
        "Bed availability updated manually. " +
        `ICU: ${formatNumber(values.manualICUBeds)}, ` +
        `General Ward: ${formatNumber(values.manualGeneralBeds)}, ` +
        `Special Rooms: ${formatNumber(values.manualOtherBeds)}.`
    );
}

function saveManualHospitalData(values) {
    try {
        localStorage.setItem(
            HOSPITAL_DATA_STORAGE_KEY,
            JSON.stringify({
                ...values,
                updatedAt: new Date().toISOString()
            })
        );

        return true;
    } catch (error) {
        console.error("Could not save hospital data:", error);
        return false;
    }
}

function loadSavedManualHospitalData() {
    try {
        const saved = localStorage.getItem(HOSPITAL_DATA_STORAGE_KEY);

        if (!saved) return null;

        const data = JSON.parse(saved);

        if (
            !data ||
            getManualHospitalFields().some(
                (id) =>
                    !Number.isSafeInteger(data[id]) ||
                    data[id] < 0
            )
        ) {
            return null;
        }

        if (validateManualHospitalData(data)) {
            return null;
        }

        return data;
    } catch (error) {
        console.error("Could not restore hospital data:", error);
        return null;
    }
}

function populateManualHospitalForm(values) {
    for (const id of getManualHospitalFields()) {
        const input = getElement(id);

        if (input && values[id] !== undefined) {
            input.value = values[id];
        }
    }
}

function applyManualHospitalData(values, showMessage = true) {
    const validationError = validateManualHospitalData(values);
    const message = getElement("manualHospitalMessage");

    if (validationError) {
        if (message) {
            message.textContent = validationError;
            message.style.color = "#dc2626";
        }

        return false;
    }

    updateHospitalOverview(values);
    updateBedMonitoring(values);

    const saved = saveManualHospitalData(values);

    if (message && showMessage) {
        message.textContent = saved
            ? "Dashboard updated successfully. Your values are saved in this browser."
            : "Dashboard updated, but the browser could not save your values.";

        message.style.color = saved ? "#15803d" : "#b45309";
    }

    return true;
}

function initializeManualHospitalData() {
    const form = getElement("manualHospitalDataForm");

    if (!form) return;

    // Restore previously saved values when the page opens.
    const savedValues = loadSavedManualHospitalData();

    if (savedValues) {
        populateManualHospitalForm(savedValues);
        applyManualHospitalData(savedValues, false);
    }

    // Avoid registering the submit event more than once.
    if (form.dataset.handlerAttached === "true") return;

    form.dataset.handlerAttached = "true";

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        try {
            const values = readManualHospitalForm();
            const validationError = validateManualHospitalData(values);

            if (validationError) {
                const message = getElement("manualHospitalMessage");

                if (message) {
                    message.textContent = validationError;
                    message.style.color = "#dc2626";
                }

                return;
            }

            applyManualHospitalData(values);
        } catch (error) {
            const message = getElement("manualHospitalMessage");

            if (message) {
                message.textContent = error.message;
                message.style.color = "#dc2626";
            }

            console.error("Manual hospital form error:", error);
        }
    });

    form.addEventListener("reset", () => {
        const message = getElement("manualHospitalMessage");

        if (message) {
            message.textContent =
                "Form cleared. The last saved dashboard values remain displayed.";
            message.style.color = "#647067";
        }
    });
}

/* =========================================================
   BACKEND CONNECTION STATUS
========================================================= */

async function checkBackendConnection() {
    try {
        const data = await apiRequest("/health");

        setText("backendStatus", "Connected");

        const systemStatus = getElement("systemStatus");

        if (systemStatus) {
            systemStatus.textContent = data.status
                ? `Backend: ${data.status}`
                : "Backend connected";
        }

        if ("model_loaded" in data) {
            setText(
                "modelServiceStatus",
                data.model_loaded ? "Connected" : "Unavailable"
            );
        }

        if ("supabase_configured" in data) {
            setText(
                "databaseStatus",
                data.supabase_configured ? "Configured" : "Unavailable"
            );
        }

        return data;
    } catch (error) {
        setText("backendStatus", "Disconnected");
        setText("modelServiceStatus", "Unavailable");

        const systemStatus = getElement("systemStatus");

        if (systemStatus) {
            systemStatus.textContent =
                "Backend unavailable. Start the Flask server.";
        }

        console.error("Backend connection error:", error);
        return null;
    }
}

/* =========================================================
   LIVE WEATHER
   Flask endpoint: GET /weather?city=Pune
========================================================= */

async function loadLiveWeather(city = "Pune") {
    setText("weatherStatus", "Loading weather information...");

    try {
        const data = await apiRequest(
            `/weather?city=${encodeURIComponent(city)}`
        );

        const temperature =
            data.temperature_c ?? data.temperature ?? data.temp;

        const humidity =
            data.humidity_pct ?? data.humidity;

        const description =
            data.description ?? data.weather ?? data.condition ?? "Unavailable";

        setText(
            "weatherTemperature",
            temperature != null ? `${formatNumber(temperature)} °C` : "Unavailable"
        );

        setText(
            "temperature",
            temperature != null ? `${formatNumber(temperature)} °C` : "Unavailable"
        );

        setText(
            "weatherHumidity",
            humidity != null ? `${formatNumber(humidity)} %` : "Unavailable"
        );

        setText(
            "humidity",
            humidity != null ? `${formatNumber(humidity)}%` : "Unavailable"
        );

        setText("weatherDescription", description);
        setText("weatherCity", data.city || city);
        setText("weatherStatus", `Weather loaded for ${data.city || city}.`);
        setText("weatherUpdated", `Last updated: ${new Date().toLocaleString("en-IN")}`);
        setText("weatherServiceStatus", "Connected");

        return data;
    } catch (error) {
        console.error("Weather loading error:", error);

        setText(
            "weatherStatus",
            "Unable to load weather. Check the Flask backend and API key."
        );

        setText("weatherServiceStatus", "Unavailable");

        return null;
    }
}

/* =========================================================
   HOSPITAL ATTENDANCE DATA
========================================================= */

async function loadHomeAttendance() {
    const tableBody = getElement("attendanceTableBody");
    const statusElement = getElement("attendanceDbStatus");

    if (!tableBody) return;

    tableBody.replaceChildren();

    const loadingRow = document.createElement("tr");
    const loadingCell = document.createElement("td");

    loadingCell.colSpan = 4;
    loadingCell.textContent = "Loading attendance records...";

    loadingRow.appendChild(loadingCell);
    tableBody.appendChild(loadingRow);

    if (statusElement) {
        statusElement.textContent = "Connecting to hospital database...";
    }

    try {
        const data = await apiRequest("/api/attendance");

        const records = Array.isArray(data)
            ? data
            : data.records || data.data || [];

        tableBody.replaceChildren();

        if (!records.length) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 4;
            cell.textContent = "No attendance records found.";

            row.appendChild(cell);
            tableBody.appendChild(row);

            if (statusElement) {
                statusElement.textContent = "No records available.";
            }

            return;
        }

        records.forEach((record) => {
            const row = document.createElement("tr");

            [
                formatDate(record.month),
                formatNumber(record.total_ae_attendances),
                record.avg_max_temp_c != null
                    ? formatNumber(record.avg_max_temp_c)
                    : "—",
                record.hot_days != null
                    ? formatNumber(record.hot_days)
                    : "—"
            ].forEach((value) => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            tableBody.appendChild(row);
        });

        if (statusElement) {
            statusElement.textContent =
                `${records.length} attendance record(s) loaded successfully.`;
        }
    } catch (error) {
        console.error("Attendance loading error:", error);

        tableBody.replaceChildren();

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 4;
        cell.textContent = "Could not load attendance records.";

        row.appendChild(cell);
        tableBody.appendChild(row);

        if (statusElement) {
            statusElement.textContent =
                "Database connection failed. Check the Flask server.";
        }
    }
}

/* =========================================================
   PREDICTION HISTORY
========================================================= */

async function loadPredictionHistory() {
    const tableBody =
        getElement("predictionHistoryBody") ||
        getElement("historyTableBody");

    const statusElement = getElement("historyStatus");

    if (!tableBody) return;

    tableBody.replaceChildren();

    try {
        const data = await apiRequest("/api/prediction-history");

        const records = Array.isArray(data)
            ? data
            : data.records || data.data || [];

        if (!records.length) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 4;
            cell.textContent = "No saved predictions yet.";

            row.appendChild(cell);
            tableBody.appendChild(row);

            if (statusElement) {
                statusElement.textContent = "No prediction history available.";
            }

            return;
        }

        records.forEach((record) => {
            const row = document.createElement("tr");

            const values = [
                formatDate(record.forecast_month),
                formatNumber(record.predicted_attendance),
                record.model_name || "XGBoost",
                record.created_at
                    ? new Date(record.created_at).toLocaleString("en-IN")
                    : "—"
            ];

            values.forEach((value) => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            tableBody.appendChild(row);
        });

        if (statusElement) {
            statusElement.textContent =
                `${records.length} saved prediction(s) loaded.`;
        }
    } catch (error) {
        console.error("Prediction history error:", error);

        tableBody.replaceChildren();

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 4;
        cell.textContent = "Unable to load prediction history.";

        row.appendChild(cell);
        tableBody.appendChild(row);

        if (statusElement) {
            statusElement.textContent =
                "Could not connect to prediction history.";
        }
    }
}

/* =========================================================
   SAVE PREDICTION HISTORY
========================================================= */

async function savePredictionHistory(forecastMonth, predictedAttendance) {
    const month = String(forecastMonth || "").trim();
    const attendance = Number(predictedAttendance);

    if (!/^\d{4}-\d{2}(-\d{2})?$/.test(month)) {
        throw new Error("Please provide a valid forecast month.");
    }

    if (!Number.isFinite(attendance) || attendance < 0) {
        throw new Error("The predicted attendance value is invalid.");
    }

    const monthDate = month.length === 7 ? `${month}-01` : month;

    const result = await apiRequest("/api/prediction-history", {
        method: "POST",
        body: JSON.stringify({
            forecast_month: monthDate,
            predicted_attendance: attendance
        })
    });

    await loadPredictionHistory();

    return result;
}

/* =========================================================
   AI PREDICTION
========================================================= */

async function runPrediction(event) {
    if (event) event.preventDefault();

    const button =
        getElement("predictButton") ||
        getElement("runPredictionButton");

    const statusElement =
        getElement("predictionStatus") ||
        getElement("predictionMessage");

    const originalButtonText = button?.textContent || "";

    const readNumber = (...ids) => {
        for (const id of ids) {
            const input = getElement(id);

            if (input) {
                return input.value.trim() === ""
                    ? NaN
                    : Number(input.value);
            }
        }

        return NaN;
    };

    const previousAttendance = readNumber(
        "previousMonthAttendance",
        "previousAttendance"
    );

    const maxTemperature = readNumber("avgMaxTemp", "avgMaxTempC");
    const minTemperature = readNumber("avgMinTemp", "avgMinTempC");
    const highestTemperature = readNumber("highestTemp", "highestTempC");
    const humidity = readNumber("avgHumidity", "avgHumidityPct");
    const hotDays = readNumber("hotDays");

    const monthInput =
        getElement("forecastMonth")?.value ||
        getElement("predictionMonth")?.value;

    const requiredValues = [
        previousAttendance,
        maxTemperature,
        minTemperature,
        highestTemperature,
        humidity,
        hotDays
    ];

    if (!monthInput || requiredValues.some((value) => !Number.isFinite(value))) {
        if (statusElement) {
            statusElement.textContent =
                "Please enter all required prediction values.";
        }

        return;
    }

    if (
        previousAttendance < 0 ||
        hotDays < 0 ||
        humidity < 0 ||
        humidity > 100
    ) {
        if (statusElement) {
            statusElement.textContent =
                "Check attendance, hot days and humidity values.";
        }

        return;
    }

    if (button) {
        button.disabled = true;
        button.textContent = "Predicting...";
    }

    if (statusElement) {
        statusElement.textContent = "Generating prediction...";
    }

    try {
        const data = await apiRequest("/predict", {
            method: "POST",
            body: JSON.stringify({
                previous_month_attendance: previousAttendance,
                avg_max_temp_c: maxTemperature,
                avg_min_temp_c: minTemperature,
                highest_temp_c: highestTemperature,
                avg_humidity_pct: humidity,
                hot_days: hotDays,
                forecast_month: monthInput
            })
        });

        const prediction =
            data.predicted_attendance ??
            data.prediction ??
            data.predicted_value;

        if (
            prediction == null ||
            !Number.isFinite(Number(prediction))
        ) {
            throw new Error(
                "The server did not return a valid prediction. Check app.py."
            );
        }

        const predictionValue = Number(prediction);

        setText("predictedAttendance", formatNumber(predictionValue));
        setText("predictionResult", formatNumber(predictionValue));
        setText("predictedDemand", formatNumber(predictionValue));
        setText("forecastPeriod", formatDate(monthInput));
        setText("predictionStatus", "Success");
        setText("predictionUpdated", `Updated: ${new Date().toLocaleString("en-IN")}`);

        if (statusElement) {
            statusElement.textContent = "Prediction generated successfully.";
        }

        try {
            await savePredictionHistory(monthInput, predictionValue);

            if (statusElement) {
                statusElement.textContent =
                    "Prediction generated and saved to history.";
            }
        } catch (saveError) {
            console.error("Saving prediction failed:", saveError);

            if (statusElement) {
                statusElement.textContent =
                    "Prediction generated, but saving history failed.";
            }
        }

        return data;
    } catch (error) {
        console.error("Prediction error:", error);

        if (statusElement) {
            statusElement.textContent =
                error.message || "Prediction failed. Check the Flask server.";
        }

        setText("predictionStatus", "Failed");

        return null;
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = originalButtonText || "Predict Demand";
        }
    }
}

/* =========================================================
   LOGIN - DEMO VALIDATION ONLY
========================================================= */

function handleLoginForm() {
    const form = getElement("loginForm");

    if (!form || form.dataset.handlerAttached === "true") return;

    form.dataset.handlerAttached = "true";

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const hospitalId = getElement("hospitalId")?.value.trim();
        const password = getElement("password")?.value;
        const messageElement = getElement("loginMessage");

        if (!hospitalId || !password) {
            if (messageElement) {
                messageElement.textContent =
                    "Enter your Hospital ID and password.";
                messageElement.className = "form-message error";
            }

            return;
        }

        if (messageElement) {
            messageElement.textContent =
                "Demo login successful. Opening dashboard...";
            messageElement.className = "form-message info";
        }

        // This is demo navigation, not secure authentication.
        window.location.href = "./dashboard.html";
    });
}

/* =========================================================
   REGISTER - DEMO VALIDATION ONLY
========================================================= */

function handleRegisterForm() {
    const form = getElement("hospitalRegisterForm");

    if (!form || form.dataset.handlerAttached === "true") return;

    form.dataset.handlerAttached = "true";

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const hospitalName = getElement("hospitalName")?.value.trim();
        const registrationNumber =
            getElement("registrationNumber")?.value.trim();
        const adminName = getElement("adminName")?.value.trim();
        const email = getElement("hospitalEmail")?.value.trim();
        const phone = getElement("hospitalPhone")?.value.trim();
        const password = getElement("hospitalPassword")?.value;
        const confirmPassword = getElement("confirmPassword")?.value;

        if (
            [
                hospitalName,
                registrationNumber,
                adminName,
                email,
                phone,
                password,
                confirmPassword
            ].some((value) => !value)
        ) {
            setMessage(
                "registerMessage",
                "Please complete all required fields.",
                "error"
            );

            return;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            setMessage(
                "registerMessage",
                "Please enter a valid email address.",
                "error"
            );

            return;
        }

        if (password.length < 8) {
            setMessage(
                "registerMessage",
                "Use a password with at least 8 characters.",
                "error"
            );

            return;
        }

        if (password !== confirmPassword) {
            setMessage(
                "registerMessage",
                "Passwords do not match.",
                "error"
            );

            return;
        }

        setMessage(
            "registerMessage",
            "Demo registration successful. You can now go to Login.",
            "success"
        );
    });
}

/* =========================================================
   PASSWORD VISIBILITY TOGGLE
========================================================= */

function setupPasswordToggles() {
    document.querySelectorAll(".toggle-password").forEach((button) => {
        if (button.dataset.handlerAttached === "true") return;

        button.dataset.handlerAttached = "true";

        button.addEventListener("click", () => {
            const targetId =
                button.dataset.passwordTarget ||
                (button.id === "togglePassword" ? "password" : null);

            const input = targetId
                ? getElement(targetId)
                : button.parentElement?.querySelector("input");

            if (!input) return;

            const show = input.type === "password";
            input.type = show ? "text" : "password";

            button.setAttribute(
                "aria-label",
                show ? "Hide password" : "Show password"
            );
        });
    });
}

/* =========================================================
   REFRESH BUTTONS
========================================================= */

function setupRefreshButtons() {
    const attendanceButton = getElement("refreshAttendance");

    if (
        attendanceButton &&
        attendanceButton.dataset.handlerAttached !== "true"
    ) {
        attendanceButton.dataset.handlerAttached = "true";
        attendanceButton.addEventListener("click", loadHomeAttendance);
    }

    const historyButton = getElement("refreshHistory");

    if (
        historyButton &&
        historyButton.dataset.handlerAttached !== "true"
    ) {
        historyButton.dataset.handlerAttached = "true";
        historyButton.addEventListener("click", loadPredictionHistory);
    }

    const weatherButton =
        getElement("refreshWeather") ||
        getElement("refreshWeatherButton");

    if (
        weatherButton &&
        weatherButton.dataset.handlerAttached !== "true"
    ) {
        weatherButton.dataset.handlerAttached = "true";

        weatherButton.addEventListener("click", () => {
            const city =
                getElement("weatherCityInput")?.value.trim() || "Pune";

            loadLiveWeather(city);
        });
    }
}

/* =========================================================
   INITIALIZE HEATCARE
========================================================= */

function initializeHeatcare() {
    handleLoginForm();
    handleRegisterForm();
    setupPasswordToggles();
    setupRefreshButtons();

    // Manual hospital form and saved values.
    initializeManualHospitalData();

    // Backend status.
    if (getElement("systemStatus") || getElement("backendStatus")) {
        checkBackendConnection();
    }

    // Attendance table.
    if (getElement("attendanceTableBody")) {
        loadHomeAttendance();
    }

    // Prediction history table.
    if (
        getElement("predictionHistoryBody") ||
        getElement("historyTableBody")
    ) {
        loadPredictionHistory();
    }

    // Weather.
    if (
        getElement("weatherStatus") ||
        getElement("temperature") ||
        getElement("humidity") ||
        getElement("weatherTemperature")
    ) {
        loadLiveWeather("Pune");
    }

    // Prediction form.
    const predictionForm =
        getElement("predictionForm") ||
        getElement("forecastForm");

    if (
        predictionForm &&
        predictionForm.dataset.handlerAttached !== "true"
    ) {
        predictionForm.dataset.handlerAttached = "true";
        predictionForm.addEventListener("submit", runPrediction);
    }

    const predictionButton = getElement("predictButton");

    if (
        predictionButton &&
        predictionButton.type !== "submit" &&
        predictionButton.dataset.handlerAttached !== "true"
    ) {
        predictionButton.dataset.handlerAttached = "true";
        predictionButton.addEventListener("click", runPrediction);
    }
}

/* =========================================================
   START APPLICATION
========================================================= */

if (document.readyState === "loading") {
    document.addEventListener(
        "DOMContentLoaded",
        initializeHeatcare,
        { once: true }
    );
} else {
    initializeHeatcare();
}
