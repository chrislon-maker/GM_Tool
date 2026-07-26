const form = document.querySelector("#process-form");
const textInput = document.querySelector("#text-input");
const submitButton = document.querySelector("#submit-button");
const clearButton = document.querySelector("#clear-button");
const resultBox = document.querySelector("#result");
const backendStatus = document.querySelector("#backend-status");


form.addEventListener("submit", async (event) => {
    // Prevent the browser from reloading the page.
    event.preventDefault();

    const text = textInput.value.trim();

    if (!text) {
        showResult("Please enter some text.", "error");
        return;
    }

    setLoading(true);

    try {
        const response = await fetch("/api/process", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: text
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "The backend returned an error."
            );
        }

        showResult(data.result, "success");
        backendStatus.textContent = "Complete";
    } catch (error) {
        showResult(error.message, "error");
        backendStatus.textContent = "Error";
    } finally {
        setLoading(false);
    }
});


clearButton.addEventListener("click", () => {
    textInput.value = "";

    resultBox.textContent = "No result yet.";
    resultBox.className = "result-box";

    backendStatus.textContent = "Waiting";

    textInput.focus();
});


function setLoading(isLoading) {
    submitButton.disabled = isLoading;
    clearButton.disabled = isLoading;

    submitButton.textContent = isLoading
        ? "Processing..."
        : "Run process";

    backendStatus.textContent = isLoading
        ? "Processing"
        : backendStatus.textContent;
}


function showResult(message, type) {
    resultBox.textContent = message;
    resultBox.className = `result-box ${type}`;
}