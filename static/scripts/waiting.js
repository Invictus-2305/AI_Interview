let currentQuestionIndex = 0;
let questions = [];
let mediaRecorder;
let audioChunks = [];
let countdownTimer;
let mediaStream; // To hold the media stream for stopping it later

// Play the intro audio when the page loads
window.onload = function () {
  fetchQuestions();
};

function fetchQuestions() {
  fetch("/check_questions")
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "done") {
        questions = data.questions;
        const introAudio = new Audio("/static/audios/intro.wav");
        introAudio
          .play()
          .then(() => {
            console.log("Intro audio is playing");
            document.getElementsByTagName("h1")[0].textContent =
              "Interview Process";
            introAudio.addEventListener("ended", () => {
              console.log("Intro audio finished");
              startRecordingProcess(); // Start the recording process after the intro
            });
          })
          .catch((error) => {
            console.error("Intro audio playback failed:", error);
            alert("Failed to play intro audio. Click OK to retry.");
          });
      } else {
        setTimeout(fetchQuestions, 5000); // Retry after 5 seconds
      }
    })
    .catch((error) => console.error("Failed to fetch questions:", error));
}

// Load the next question
function loadNextQuestion() {
  if (currentQuestionIndex < questions.length) {
    const question = questions[currentQuestionIndex];
    document.getElementById("question").textContent = question.question;

    const questionAudio = new Audio(
      `/static/audios/question_${currentQuestionIndex + 1}.wav`
    );
    questionAudio
      .play()
      .then(() => {
        console.log("Question audio is playing");
        questionAudio.addEventListener("ended", () => {
          console.log("Question audio finished");
          startRecordingProcess(); // Start the recording process after the question audio
        });
      })
      .catch((error) => {
        console.error("Failed to play question audio:", error);
        alert("Failed to play question audio. Click OK to retry.");
      });

    
  } else {
    endInterview(); // End the interview if no more questions are left
  }
  currentQuestionIndex++;
}

function endInterview() {
  document.getElementById("status").textContent =
    "Interview completed. Thank you!";
  document.getElementById("question").textContent = "";
  document.getElementById("timer").textContent = "";
  document.getElementById("stopRecording").style.display = "none";

  // Stop the media stream and release microphone
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
    console.log("Microphone access stopped.");
  }

  // Export the DataFrame to CSV
  // exportCSV();
}

// function exportCSV() {
//   fetch("/export_csv", {
//     method: "GET",
//   })
//     .then((response) => {
//       if (response.ok) {
//         return response.blob();
//       } else {
//         throw new Error("Failed to export CSV");
//       }
//     })
//     .then((blob) => {
//       // Create a link element to download the CSV file
//       const url = window.URL.createObjectURL(blob);
//       const a = document.createElement("a");
//       a.href = url;
//       a.download = "interview_responses.csv";
//       document.body.appendChild(a);
//       a.click();
//       document.body.removeChild(a);
//       window.URL.revokeObjectURL(url);
//     })
//     .catch((error) => {
//       console.error("Error exporting CSV:", error);
//       alert("Failed to export CSV. Please try again.");
//     });
// }

// Start recording
function startRecording() {
  navigator.mediaDevices
    .getUserMedia({ audio: true })
    .then((stream) => {
      mediaStream = stream; // Save the stream to stop it later
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();
      audioChunks = [];

      mediaRecorder.addEventListener("dataavailable", (event) => {
        audioChunks.push(event.data);
      });

      mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" }); // Default format is webm
        convertToWav(audioBlob).then((wavBlob) => {
          sendAudioToBackend(wavBlob);
        });
      });

      document.getElementById("status").textContent =
        "Recording in progress...";
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

  // Write WAV header
  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  writeString(view, 0, "RIFF"); // RIFF header
  view.setUint32(4, 36 + buffer.length * numOfChan * 2, true); // File length
  writeString(view, 8, "WAVE"); // WAVE header
  writeString(view, 12, "fmt "); // fmt chunk
  view.setUint32(16, 16, true); // Length of fmt data
  view.setUint16(20, 1, true); // PCM format
  view.setUint16(22, numOfChan, true); // Number of channels
  view.setUint32(24, buffer.sampleRate, true); // Sample rate
  view.setUint32(28, buffer.sampleRate * numOfChan * 2, true); // Byte rate
  view.setUint16(32, numOfChan * 2, true); // Block align
  view.setUint16(34, 16, true); // Bits per sample
  writeString(view, 36, "data"); // data chunk
  view.setUint32(40, buffer.length * numOfChan * 2, true); // Data length

  // Write PCM audio data
  let offset = 44;
  for (let i = 0; i < buffer.numberOfChannels; i++) {
    const channel = buffer.getChannelData(i);
    for (let j = 0; j < channel.length; j++) {
      const sample = Math.max(-1, Math.min(1, channel[j])); // Clamp sample to [-1, 1]
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

  // Send the current question index along with the audio
  // The introduction is at index 0, so questions start from index 1
  // Subtract 1 from currentQuestionIndex to align with backend logic
  formData.append("question_index", currentQuestionIndex - 1);
  console.log(currentQuestionIndex);

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

// Start the recording process
function startRecordingProcess() {
  document.getElementById("status").textContent =
    "Recording will start in 5 seconds...";
  startCountdown(5, () => {
    startRecording();
    document.getElementById("stopRecording").style.display = "block";

    // Start the recording duration timer
    startCountdown(15, () => {
      stopRecording(); // Automatically stop recording when the timer ends
    });
  });
}

// Start a countdown timer
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
      callback(); // Trigger the callback when the countdown ends
    }
  }, 1000);
}

// Stop recording
function stopRecording(manualStop = false) {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();

    // Clear the countdown timer
    clearInterval(countdownTimer);
    document.getElementById("timer").textContent = "";

    if (manualStop) {
      document.getElementById("status").textContent =
        "Recording stopped by user.";
    } else {
      document.getElementById("status").textContent =
        "Recording stopped automatically.";
    }

    document.getElementById("stopRecording").style.display = "none";

    // Load the next question
    loadNextQuestion();
  }
}

// Add event listener for the Stop Recording button
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("stopRecording").addEventListener("click", () => {
    stopRecording(true); // Manually stop recording
  });
});
