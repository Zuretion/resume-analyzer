// URL backend. Локально — адрес uvicorn; после деплоя (этап 5 роадмапа)
// замените на адрес задеплоенного backend (Render/Railway).
const API_URL = "http://127.0.0.1:8000/api/analyze";

const form = document.getElementById("analyze-form");
const submitBtn = document.getElementById("submit-btn");
const resultSection = document.getElementById("result");
const resultLabel = document.getElementById("result-label");
const resultScore = document.getElementById("result-score");
const scoreBar = document.getElementById("score-bar");
const suggestionsList = document.getElementById("suggestions-list");
const errorMessage = document.getElementById("error-message");

const LABEL_STYLES = {
  "Good Fit": "bg-green-100 text-green-700",
  "Potential Fit": "bg-amber-100 text-amber-700",
  "No Fit": "bg-red-100 text-red-700",
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const resumeText = document.getElementById("resume").value.trim();
  const jobText = document.getElementById("job").value.trim();
  const resumeFile = document.getElementById("resume-file").files[0];
  const jobFile = document.getElementById("job-file").files[0];

  hideError();
  setLoading(true);

  try {
    const formData = new FormData();

    // Priority: File over Text
    if (resumeFile) {
      formData.append("resume_file", resumeFile);
    } else {
      formData.append("resume_text", resumeText);
    }

    if (jobFile) {
      formData.append("job_description_file", jobFile);
    } else {
      formData.append("job_description_text", jobText);
    }

    const response = await fetch(API_URL, {
      method: "POST",
      body: formData,
      // Note: Content-Type is automatically set to multipart/form-data by the browser
    });

    if (!response.ok) {
      throw new Error(`Сервер ответил с ошибкой: ${response.status}`);
    }

    const data = await response.json();
    renderResult(data);
  } catch (err) {
    // Самая частая причина на этом этапе — backend не запущен
    // или не настроен CORS (см. этап 4 роадмапа).
    showError("Не удалось получить ответ от сервера. Убедитесь, что backend запущен.");
    console.error(err);
  } finally {
    setLoading(false);
  }
});

function renderResult(data) {
  resultSection.classList.remove("hidden");

  resultScore.textContent = `${data.score}/100`;
  scoreBar.style.width = `${data.score}%`;

  resultLabel.textContent = data.label;
  resultLabel.className = `text-sm font-medium px-3 py-1 rounded-full ${
    LABEL_STYLES[data.label] || "bg-slate-100 text-slate-700"
  }`;

  suggestionsList.innerHTML = "";
  data.suggestions.forEach((suggestion) => {
    const li = document.createElement("li");
    li.className = "flex gap-2";
    li.innerHTML = `<span class="text-slate-400">&bull;</span><span>${escapeHtml(suggestion)}</span>`;
    suggestionsList.appendChild(li);
  });
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.textContent = isLoading ? "Анализируем..." : "Проанализировать";
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.remove("hidden");
}

function hideError() {
  errorMessage.classList.add("hidden");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
