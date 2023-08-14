const traineeInput = document.getElementById("upload-trainee-input");
const traineeSource = document.getElementById("trainee-source");
const traineeVideo = document.getElementById("trainee-video");

const coachSource = document.getElementById("coach-source");
const coachVideo = document.getElementById("coach-video");

const showTennisServe = document.getElementById("show-serve-button");
const showTableTennis = document.getElementById("show-tt-button");

traineeInput.addEventListener("change", handleTraineeInput, false);
showTennisServe.addEventListener("click", handleShowTennisServe, false);
showTableTennis.addEventListener("click", handleShowTableTennis, false);

function handleTraineeInput() {
    const traineeFile = this.files[0];
    console.log(traineeFile);

    const uploadTraineeURL = URL.createObjectURL(this.files[0]);
    console.log(uploadTraineeURL);
    console.log(traineeFile["type"]);

    traineeVideo.pause();
    traineeSource.setAttribute('src', uploadTraineeURL);
    traineeSource.setAttribute('type', traineeFile["type"]);

    traineeVideo.setAttribute("controls", "controls");
    traineeVideo.load();
    traineeVideo.play();
}

function handleShowTennisServe() {
    handleShowCoachVideo("../videos/TennisSwing.mp4");
}

function handleShowTableTennis() {
    handleShowCoachVideo("../videos/TableTennis.mp4");
}

function handleShowCoachVideo(video_url) {
    coachVideo.pause();
    coachSource.setAttribute('src', video_url);
    coachSource.setAttribute("type", "video/mp4");

    coachSource.setAttribute("controls", "controls");
    coachVideo.load();
    coachVideo.play();
}