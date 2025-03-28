// Audio Visualizer Variables
let audioContext, analyser, dataArray, source;
let rafId;
let smoothVolume = 0;
const shockwaves = [];
const particles = [];
const audioElement = document.getElementById("audioElement");

// Initialize floating particles (reduced to 20)
function initParticles() {
  const canvas = document.getElementById("visualizer");
  for (let i = 0; i < 20; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 3 + 1,
      speedX: (Math.random() - 0.5) * 0.8,
      speedY: (Math.random() - 0.5) * 0.8,
      color: `hsla(${Math.random() * 15 + 45}, 100%, 60%, ${
        Math.random() * 0.5 + 0.3
      })`,
    });
  }
}

// Initialize audio context for visualizer
function initAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 128;

    source = audioContext.createMediaElementSource(audioElement);
    source.connect(analyser);
    analyser.connect(audioContext.destination);

    dataArray = new Uint8Array(analyser.frequencyBinCount);
    initParticles();
  }
}

// Visualizer drawing function with balanced reactivity
function drawVisualizer() {
  rafId = requestAnimationFrame(drawVisualizer);

  const canvas = document.getElementById("visualizer");
  const ctx = canvas.getContext("2d");
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const maxRadius = Math.min(canvas.width, canvas.height) * 0.3;

  // Clear canvas with fading effect
  ctx.fillStyle = "rgba(26, 26, 26, 0.1)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Always move particles
  particles.forEach((particle) => {
    particle.x += particle.speedX;
    particle.y += particle.speedY;

    // Wrap around screen edges
    if (particle.x < 0) particle.x = canvas.width;
    if (particle.x > canvas.width) particle.x = 0;
    if (particle.y < 0) particle.y = canvas.height;
    if (particle.y > canvas.height) particle.y = 0;

    ctx.beginPath();
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
    ctx.fillStyle = particle.color;
    ctx.fill();
  });

  if (audioContext && analyser) {
    analyser.getByteFrequencyData(dataArray);

    // Balanced volume calculation
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i];
    }

    // Moderate volume boost (25% more than original)
    const targetVolume = Math.min(1, (sum / dataArray.length / 255) * 1.25);
    smoothVolume = smoothVolume * 0.65 + targetVolume * 0.35; // Slightly faster response

    // Balanced pulse range
    const pulseRadius = maxRadius * (0.45 + 0.55 * smoothVolume);

    // Subtle glow gradient
    const innerGlow = ctx.createRadialGradient(
      centerX,
      centerY,
      pulseRadius * 0.3,
      centerX,
      centerY,
      pulseRadius * 1.5
    );
    innerGlow.addColorStop(0, `rgba(255, 215, 0, ${0.5 + smoothVolume * 0.4})`);
    innerGlow.addColorStop(1, `rgba(255, 195, 0, 0)`);

    // Draw core with moderate intensity
    ctx.beginPath();
    ctx.arc(centerX, centerY, pulseRadius, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255, 215, 0, ${0.4 + smoothVolume * 0.5})`;
    ctx.fill();

    // Add glow
    ctx.beginPath();
    ctx.arc(centerX, centerY, pulseRadius * 1.5, 0, Math.PI * 2);
    ctx.fillStyle = innerGlow;
    ctx.fill();
  }
}

// Set up visualizer
function setupVisualizer() {
  const canvas = document.getElementById("visualizer");
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
  initParticles();

  // Handle window resize
  window.addEventListener("resize", function () {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
  });
}

// Interview Process Variables
let currentQuestionIndex = 0;
let questions = [];
let mediaRecorder;
let audioChunks = [];
let countdownTimer;
let mediaStream;
let progress = 0;

// Update progress bar
function updateProgressBar(percentage, message) {
  const progressBar = document.getElementById("progressBar");
  const progressBarContainer = document.getElementById("progressBarContainer");

  progressBar.style.width = percentage + "%";
  progressBar.textContent = percentage + "%";
  document.getElementById("status").textContent = message;

  if (percentage >= 100) {
    setTimeout(() => {
      progressBarContainer.style.display = "none";
    }, 500);
  }
}

// Smooth progress updates
function smoothProgressUpdate(targetProgress, message) {
  const increment = 1;
  const intervalTime = 50;

  const interval = setInterval(() => {
    if (progress < targetProgress) {
      progress += increment;
      if (progress > targetProgress) progress = targetProgress;
      updateProgressBar(progress, message);
    } else {
      clearInterval(interval);
    }
  }, intervalTime);
}

// Fetch questions from backend
function fetchQuestions() {
  if (progress === 0) {
    smoothProgressUpdate(10, "Processing JD and Resume");
  }

  setTimeout(() => {
    smoothProgressUpdate(40, "Extracting skills, projects, requirements, etc.");

    setTimeout(() => {
      smoothProgressUpdate(41, "Generating questions");

      fetch("/check_questions")
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "done") {
            smoothProgressUpdate(80, "Finalizing");

            setTimeout(() => {
              smoothProgressUpdate(100, "Completed");
              questions = data.questions;
              startIntroAudio();
            }, 2000);
          } else {
            setTimeout(() => {
              if (progress < 78) {
                progress += 1;
                updateProgressBar(progress, "Generating questions");
              }
              fetchQuestions();
            }, 5000);
          }
        })
        .catch((error) => console.error("Failed to fetch questions:", error));
    }, 2000);
  }, 2000);
}

// Start intro audio
function startIntroAudio() {
  // Show visualizer when audio starts
  document.querySelector(".visualizer-container").classList.add("visible");

  // Initialize audio context when first playing audio
  initAudioContext();

  audioElement
    .play()
    .then(() => {
      document.getElementsByTagName("h1")[0].textContent = "Interview Process";
      document.getElementById("question").textContent =
        "We will be starting with your interview soon. Please introduce yourself.";

      // Start visualizer animation
      drawVisualizer();

      audioElement.addEventListener("ended", () => {
        cancelAnimationFrame(rafId);
        startRecordingProcess();
      });
    })
    .catch((error) => {
      console.error("Intro audio playback failed:", error);
      alert("Failed to play intro audio. Click OK to retry.");
    });
}

// Load next question
function loadNextQuestion() {
  if (currentQuestionIndex < questions.length) {
    const question = questions[currentQuestionIndex];
    document.getElementById("question").textContent = question.question;

    const questionAudio = new Audio(
      `/static/audios/question_${currentQuestionIndex + 1}.wav`
    );

    // Set up audio context for question audio
    const questionAudioContext = new (window.AudioContext ||
      window.webkitAudioContext)();
    const questionAnalyser = questionAudioContext.createAnalyser();
    questionAnalyser.fftSize = 128;

    const questionSource =
      questionAudioContext.createMediaElementSource(questionAudio);
    questionSource.connect(questionAnalyser);
    questionAnalyser.connect(questionAudioContext.destination);

    const questionDataArray = new Uint8Array(
      questionAnalyser.frequencyBinCount
    );

    // Visualizer for question audio
    function drawQuestionVisualizer() {
      rafId = requestAnimationFrame(drawQuestionVisualizer);

      questionAnalyser.getByteFrequencyData(questionDataArray);

      const canvas = document.getElementById("visualizer");
      const ctx = canvas.getContext("2d");
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const maxRadius = Math.min(canvas.width, canvas.height) * 0.32; // Slightly larger base

      // Clear canvas with soft fade
      ctx.fillStyle = "rgba(26, 26, 26, 0.1)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Smooth particle movement
      particles.forEach((particle) => {
        particle.x += particle.speedX;
        particle.y += particle.speedY;

        // Gentle wrap-around
        if (particle.x < 0) particle.x = canvas.width;
        if (particle.x > canvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = canvas.height;
        if (particle.y > canvas.height) particle.y = 0;

        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = particle.color;
        ctx.fill();
      });

      // Balanced volume calculation
      let sum = 0;
      for (let i = 0; i < questionDataArray.length; i++) {
        // Slight emphasis on mid frequencies
        const boost =
          i > questionDataArray.length / 4 &&
          i < (questionDataArray.length * 3) / 4
            ? 1.3
            : 1;
        sum += questionDataArray[i] * boost;
      }

      // Moderate volume boost
      const targetVolume = Math.min(
        1.2,
        (sum / questionDataArray.length / 255) * 1.6
      );
      smoothVolume = smoothVolume * 0.6 + targetVolume * 0.4; // Balanced response

      // Pleasant pulse range
      const pulseRadius = maxRadius * (0.45 + 0.6 * smoothVolume);

      // Elegant glow gradient
      const innerGlow = ctx.createRadialGradient(
        centerX,
        centerY,
        pulseRadius * 0.25,
        centerX,
        centerY,
        pulseRadius * 1.6
      );
      innerGlow.addColorStop(
        0,
        `rgba(255, 215, 0, ${0.5 + smoothVolume * 0.4})`
      );
      innerGlow.addColorStop(1, `rgba(255, 195, 0, 0)`);

      // Draw core with nice glow
      ctx.beginPath();
      ctx.arc(centerX, centerY, pulseRadius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 215, 0, ${0.45 + smoothVolume * 0.5})`;
      ctx.fill();

      // Add subtle glow
      ctx.beginPath();
      ctx.arc(centerX, centerY, pulseRadius * 1.6, 0, Math.PI * 2);
      ctx.fillStyle = innerGlow;
      ctx.fill();

      // Very subtle ripple on strong peaks
      if (smoothVolume > 0.7) {
        ctx.beginPath();
        ctx.arc(centerX, centerY, pulseRadius * 1.3, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 215, 0, ${(smoothVolume - 0.7) * 0.4})`;
        ctx.lineWidth = 1 + smoothVolume * 2;
        ctx.stroke();
      }
    }

    questionAudio
      .play()
      .then(() => {
        // Start visualizer for question audio
        drawQuestionVisualizer();

        questionAudio.addEventListener("ended", () => {
          cancelAnimationFrame(rafId);
          startRecordingProcess();
        });
      })
      .catch((error) => {
        console.error("Failed to play question audio:", error);
        alert("Failed to play question audio. Click OK to retry.");
      });
  } else {
    endInterview();
  }
  currentQuestionIndex++;
}

// End interview
function endInterview() {
  document.getElementById("status").textContent =
    "Interview completed. Thank you!";
  document.getElementById("question").textContent = "";
  document.getElementById("timer").textContent = "";
  document.getElementById("stopRecording").style.display = "none";

  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
}

// Start recording
function startRecording() {
  navigator.mediaDevices
    .getUserMedia({ audio: true })
    .then((stream) => {
      mediaStream = stream;
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();
      audioChunks = [];

      mediaRecorder.addEventListener("dataavailable", (event) => {
        audioChunks.push(event.data);
      });

      mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        convertToWav(audioBlob).then((wavBlob) => {
          sendAudioToBackend(wavBlob);
        });
      });

      document.getElementById("status").textContent =
        "Recording in progress...";
      document.getElementById("recordingIndicator").style.display = "block";
    })
    .catch((error) => {
      console.error("Microphone access denied:", error);
      alert("Microphone access is required. Please allow access.");
    });
}

// Convert audio to WAV format
async function convertToWav(audioBlob) {
  const audioContext = new AudioContext();
  const arrayBuffer = await audioBlob.arrayBuffer();
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

  const wavBlob = audioBufferToWav(audioBuffer);
  return wavBlob;
}

// Convert AudioBuffer to WAV Blob
function audioBufferToWav(buffer) {
  const numOfChan = buffer.numberOfChannels;
  const length = buffer.length * numOfChan * 2 + 44;
  const bufferOut = new ArrayBuffer(length);
  const view = new DataView(bufferOut);

  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + buffer.length * numOfChan * 2, true);
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, numOfChan, true);
  view.setUint32(24, buffer.sampleRate, true);
  view.setUint32(28, buffer.sampleRate * numOfChan * 2, true);
  view.setUint16(32, numOfChan * 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, "data");
  view.setUint32(40, buffer.length * numOfChan * 2, true);

  let offset = 44;
  for (let i = 0; i < buffer.numberOfChannels; i++) {
    const channel = buffer.getChannelData(i);
    for (let j = 0; j < channel.length; j++) {
      const sample = Math.max(-1, Math.min(1, channel[j]));
      view.setInt16(
        offset,
        sample < 0 ? sample * 0x8000 : sample * 0x7fff,
        true
      );
      offset += 2;
    }
  }

  return new Blob([bufferOut], { type: "audio/wav" });
}

// Send audio to backend
async function sendAudioToBackend(audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.wav");
  formData.append("question_index", currentQuestionIndex - 1);

  fetch("/s_t_t", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Audio sent to backend:", data);
    })
    .catch((error) => {
      console.error("Failed to send audio to backend:", error);
    });
}

// Start recording process
function startRecordingProcess() {
  document.getElementById("status").textContent =
    "Recording will start in 5 seconds...";
  startCountdown(5, () => {
    startRecording();
    document.getElementById("stopRecording").style.display = "block";
    startCountdown(15, () => {
      stopRecording();
    });
  });
}

// Start countdown timer
function startCountdown(seconds, callback) {
  let remainingSeconds = seconds;
  document.getElementById(
    "timer"
  ).textContent = `Time remaining: ${remainingSeconds} seconds`;

  countdownTimer = setInterval(() => {
    remainingSeconds--;

    if (remainingSeconds > 0) {
      document.getElementById(
        "timer"
      ).textContent = `Time remaining: ${remainingSeconds} seconds`;
    } else {
      clearInterval(countdownTimer);
      document.getElementById("timer").textContent = "";
      callback();
    }
  }, 1000);
}

// Stop recording
function stopRecording(manualStop = false) {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    clearInterval(countdownTimer);
    document.getElementById("timer").textContent = "";
    document.getElementById("recordingIndicator").style.display = "none";

    if (manualStop) {
      document.getElementById("status").textContent =
        "Recording stopped by user.";
    } else {
      document.getElementById("status").textContent =
        "Recording stopped automatically.";
    }

    document.getElementById("stopRecording").style.display = "none";
    loadNextQuestion();
  }
}

// Initialize when page loads
window.onload = function () {
  setupVisualizer();
  fetchQuestions();

  // Start particle animation immediately
  drawVisualizer();

  document.getElementById("stopRecording").addEventListener("click", () => {
    stopRecording(true);
  });
};
