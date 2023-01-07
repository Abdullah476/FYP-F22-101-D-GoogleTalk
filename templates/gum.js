navigator.mediaDevices.getUserMedia({audio: true})
.then(() => {console.log("Done!");})
.catch((error) => {console.log(error);});