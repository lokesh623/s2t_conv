let mediaRecorder;
let audioChunks = [];

async function startRecording() {
    console.log("Start recording...");

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            console.log("Data available...");
            audioChunks.push(event.data);
        };

        mediaRecorder.onstart = () => {
            console.log("Recording started");
        };

        mediaRecorder.onstop = () => {
            console.log("Recording stopped");
        };

        mediaRecorder.onerror = event => {
            console.error("Recording error: ", event.error);
        };

        mediaRecorder.start();
    } catch (error) {
        console.error("Error accessing microphone: ", error);
    }
}

async function stopRecording() {
    console.log("Stop recording...");

    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();

        mediaRecorder.onstop = async () => {
            console.log("Processing recording...");

            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('file', audioBlob, 'audio.wav');

            // Clear the previous transcription
            document.getElementById('transcription').textContent = 'Processing...';

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                document.getElementById('transcription').textContent = result.transcription || result.error;
            } catch (error) {
                console.error("Error uploading audio: ", error);
                document.getElementById('transcription').textContent = 'Error uploading audio';
            }

            // Clear the audio chunks for the next recording
            audioChunks = [];
        };
    } else {
        console.log("MediaRecorder is not recording");
    }
}

// Event listeners for the single button
document.addEventListener("DOMContentLoaded", function () {
    const recordButton = document.getElementById('recordButton');
    recordButton.addEventListener('mousedown', startRecording);
    recordButton.addEventListener('mouseup', stopRecording);
});
