var emailAddress = undefined;

// Start a three-way handshake process

chrome.runtime.sendMessage({ data: "handshake" }, function (response) {
  // send message to background.js
  console.log(response);
  emailAddress = response.email;
});

// const loggedIn = document.getElementById("loggedIn");
const audio = document.getElementById("placeholder");
const responseTab = document.getElementById("response");

let chunks = [];
let mediaRecorder;
let button = document.getElementById("butn");

// Start the recording
const startRecording = async () => {
  const mimeType = "audio/webm;codecs=opus"; // This works for Opera GX too, apparently
  if (!MediaRecorder.isTypeSupported(mimeType)) {
    alert("mime type " + mimeType + " is not supported!");
    return;
  }
  const options = {
    audioBitsPerSecond: 128000,
    mimeType,
  };
  const mediaStream = await getLocalMediaStream();
  window.mediaStream = mediaStream;
  mediaRecorder = new MediaRecorder(mediaStream, options);
  mediaRecorder.ondataavailable = ({ data }) => {
    if (data.size > 0) {
      chunks.push(data);
    }
  };
  mediaRecorder.onstop = () => {
    saveFile();
    mediaRecorder.ondataavailable = undefined;
    mediaRecorder.onstop = undefined;
    mediaRecorder = undefined;
  };
  mediaRecorder.start(1000);
  button.removeEventListener("click", startRecording);
  button.addEventListener("click", stopRecording);
  button.style.transform = "scale(1.25)";
  button.classList.add("pulse");
};

const stopRecording = async () => {
  if (!mediaRecorder) {
    return;
  }
  button.removeEventListener("click", stopRecording);
  mediaRecorder.stop();
  window.mediaStream.getTracks().forEach((track) => track.stop());
};

button.addEventListener("click", startRecording);

const getLocalMediaStream = async () => {
  const mediaStream = await navigator.mediaDevices.getUserMedia({
    audio: true,
    video: false,
  });
  audio.srcObject = mediaStream;
  return mediaStream;
};

// Reset the button for recording again
function reset() {
  button.addEventListener("click", startRecording);
  button.disabled = false;
  button.style.transform = "none";
  button.classList.remove("blur");
  button.style.cursor = "pointer";
}

function sendEmail() {
  console.log("Email address: " + emailAddress);
  fetch("http://127.0.0.1:8086/email", {
    headers: {
      "Content-Type": "application/json",
    },
    method: "POST",
    body: JSON.stringify({
      email: emailAddress,
    }),
  })
    .then(function (response) {
      console.log(response.json());
    })
    .catch(function (error) {
      console.log(error);
    });
}

const saveFile = () => {
  sendEmail();
  responseTab.innerText = "Processing...";
  button.disabled = true;
  button.style.transform = "none";
  button.classList.add("blur");
  button.classList.remove("pulse");
  button.style.cursor = "wait";
  const blob = new Blob(chunks, { type: "audio/webm" });
  chunks = [];
  var formData = new FormData();
  formData.append("audio", blob, "output.webm");
  fetch("http://127.0.0.1:8086/receive", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      return response.json();
    })
    .then((json) => {
      console.log(json);
      responseTab.innerText = json;
      reset();
    })
    .catch((error) => {
      console.log(error);
      reset();
      responseTab.innerText = "No connection to server established.";
    });
};
