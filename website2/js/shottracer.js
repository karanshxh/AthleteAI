const getValuesFromInputs = () => {
    const uploadTrainee = document.getElementById("upload-trainee-input").files[0];

    console.log(uploadTrainee);
    return uploadTrainee;
}

const convertInputValues = () => {
    const uploadTrainee = getValuesFromInputs();

    const uploadTraineeURL = URL.createObjectURL(uploadTrainee);

    return uploadTraineeURL;
}

const addInputToCard = () => {
    const traineeURL = convertInputValues();

    document.getElementById("trainee-video").setAttribute('src', traineeURL);
}


const traineeInput = document.getElementById("upload-trainee-input");
traineeInput.addEventListener("change", handleTraineeInput, false);

function handleTraineeInput() {
    const traineeFile = this.files[0];
    console.log(traineeFile);

    const uploadTraineeURL = URL.createObjectURL(this.files[0]);
    console.log(uploadTraineeURL);
    console.log(traineeFile["type"]);

    document.getElementById("trainee-video").pause();
    document.getElementById("trainee-source").setAttribute('src', uploadTraineeURL);
    document.getElementById("trainee-source").setAttribute('type', traineeFile["type"]);

    //document.getElementById("trainee-video").setAttribute("visibility", "visible");
    document.getElementById("trainee-video").load();
    document.getElementById("trainee-video").play();
}