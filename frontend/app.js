(() => {
  const API_BASE = "/api";

  const els = {
    age: document.getElementById("age"),
    gender: document.getElementById("gender"),
    preconditions: document.getElementById("preconditions"),
    findings: document.getElementById("findings"),
    dictateBtn: document.getElementById("dictateBtn"),
    analyzeBtn: document.getElementById("analyzeBtn"),
    status: document.getElementById("status"),
    resultsCard: document.getElementById("resultsCard"),
    diagnosesList: document.getElementById("diagnosesList"),
    disclaimer: document.getElementById("disclaimer"),
    reportSection: document.getElementById("reportSection"),
    reportMarkdown: document.getElementById("reportMarkdown"),
    copyReportBtn: document.getElementById("copyReportBtn"),
  };

  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;

  function setStatus(message, spinner = true) {
    els.status.innerHTML = spinner
      ? `<span class="spinner" aria-hidden="true"></span> ${message}`
      : message;
  }

  function clearStatus() {
    els.status.innerHTML = "";
  }

  async function transcribeAudio() {
    setStatus("Requesting microphone access...");
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      setStatus("Microphone access denied or unavailable.", false);
      return;
    }
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: "audio/webm" });
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");

      setStatus("Transcribing audio...");
      try {
        const response = await fetch(`${API_BASE}/transcribe`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.detail || `Transcription failed (${response.status})`);
        }

        const data = await response.json();
        els.findings.value = data.text || "";
        setStatus(`Transcription complete (${data.backend || "unknown"} backend).`, false);
        setTimeout(clearStatus, 2000);
      } catch (err) {
        setStatus(`Transcription error: ${err.message}`, false);
      } finally {
        stream.getTracks().forEach((track) => track.stop());
      }
    };

    mediaRecorder.start();
    isRecording = true;
    els.dictateBtn.textContent = "Stop Dictation";
    setStatus("Recording...", true);
  }

  function stopDictation() {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      isRecording = false;
      els.dictateBtn.textContent = "Dictate";
    }
  }

  async function analyzeFindings() {
    const age = parseInt(els.age.value, 10);
    const gender = els.gender.value;
    const preconditions = els.preconditions.value.trim();
    const findings = els.findings.value.trim();

    if (isNaN(age) || age < 0) {
      setStatus("Please enter a valid age (0 or greater).", false);
      return;
    }
    if (!findings) {
      setStatus("Please provide findings before analyzing.", false);
      return;
    }

    setStatus("Analyzing findings...");
    els.analyzeBtn.disabled = true;

    try {
      const response = await fetch(`${API_BASE}/analyze-diagnose`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ age, gender, preconditions, findings }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `Analysis failed (${response.status})`);
      }

      const data = await response.json();
      renderDiagnoses(data.diagnoses || [], data.disclaimer || "", data);
      setStatus("Analysis complete.", false);
      setTimeout(clearStatus, 2000);
    } catch (err) {
      setStatus(`Analysis error: ${err.message}`, false);
    } finally {
      els.analyzeBtn.disabled = false;
    }
  }

  function renderDiagnoses(diagnoses, disclaimer, reportData = {}) {
    els.diagnosesList.innerHTML = "";
    diagnoses.forEach((text) => {
      const li = document.createElement("li");
      li.textContent = text;
      els.diagnosesList.appendChild(li);
    });
    els.disclaimer.textContent = disclaimer;

    if (reportData.report_markdown) {
      els.reportMarkdown.textContent = reportData.report_markdown;
      els.reportSection.hidden = false;
    } else {
      els.reportSection.hidden = true;
    }

    els.resultsCard.hidden = false;
  }

  async function copyReport() {
    const text = els.reportMarkdown.textContent;
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      const original = els.copyReportBtn.textContent;
      els.copyReportBtn.textContent = "Copied!";
      setTimeout(() => {
        els.copyReportBtn.textContent = original;
      }, 1500);
    } catch (err) {
      setStatus("Failed to copy report.", false);
    }
  }

  els.dictateBtn.addEventListener("click", () => {
    if (isRecording) {
      stopDictation();
    } else {
      transcribeAudio();
    }
  });

  els.analyzeBtn.addEventListener("click", analyzeFindings);
  els.copyReportBtn.addEventListener("click", copyReport);

  // Enable analyze when findings change
  els.findings.addEventListener("input", () => {
    els.analyzeBtn.disabled = !els.findings.value.trim();
  });
})();
