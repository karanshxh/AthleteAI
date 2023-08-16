const traineeInput = document.getElementById("upload-trainee-input");
const traineeSource = document.getElementById("trainee-source");
const traineeVideo = document.getElementById("trainee-video");

const coachSource = document.getElementById("coach-source");
const coachVideo = document.getElementById("coach-video");

const showTennisServe = document.getElementById("show-serve-button");
const showTableTennis = document.getElementById("show-tt-button");
const docSearchInput = document.getElementById("input-question");
const docSearchButton = document.getElementById("ask-button");


const convertTo3D = document.getElementById("convert-button");

traineeInput.addEventListener("change", handleTraineeInput, false);
showTennisServe.addEventListener("click", handleShowTennisServe, false);
showTableTennis.addEventListener("click", handleShowTableTennis, false);
convertTo3D.addEventListener("click", handleConvertClick, false);

docSearchButton.addEventListener("click", handleDocSearch, false);
console.log("Loaded");

function handleTraineeInput() {
    const traineeFile = this.files[0];
    console.log(traineeFile);

    const uploadTraineeURL = URL.createObjectURL(this.files[0]);
    console.log(uploadTraineeURL);
    console.log(traineeFile["type"]);

    const formData = new FormData();
    formData.append('file', traineeFile, 'uploaded_video.mp4');

    fetch('/upload', {
    method: 'POST',
    body: formData
    })
    .then(response => response.json())
    .then(data => {
    console.log('Upload successful:', data);
    })
    .catch(error => {
    console.error('Error uploading:', error);
    });

    traineeVideo.pause();
    traineeSource.setAttribute('src', uploadTraineeURL);
    traineeSource.setAttribute('type', traineeFile["type"]);

    traineeVideo.setAttribute("controls", "controls");
    traineeVideo.load();
    traineeVideo.play();

    console.log(traineeFile);

    $.ajax({
        url: '/process',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({"value": traineeFile["name"]}),
        success: function(response) {
            //$("#output").text(response.result);
            console.log(response.result);
        },
        error: function(error) {
            console.log(error);
        }
    });
}

function handleShowTennisServe() {
    console.log("Tennis Serve");
    handleShowCoachVideo("static/videos/TennisSwing.mp4");

    $.ajax({
        url: '/coach_select',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({"value": "TennisSwing.mp4"}),
        success: function(response) {
            //$("#output").text(response.result);
            console.log(response.result);
        },
        error: function(error) {
            console.log(error);
        }
    });
}

function handleShowTableTennis() {
    handleShowCoachVideo("static/videos/TableTennis.mp4");

    $.ajax({
        url: '/coach_select',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({"value": "TableTennis.mp4"}),
        success: function(response) {
            //$("#output").text(response.result);
            console.log(response.result);
        },
        error: function(error) {
            console.log(error);
        }
    });
}

function handleShowCoachVideo(video_url) {
    coachVideo.pause();
    coachSource.setAttribute('src', video_url);
    coachSource.setAttribute("type", "video/mp4");

    coachSource.setAttribute("controls", "controls");
    coachVideo.load();
    coachVideo.play();
}

function handleConvertClick() {
    $.ajax({
        url: '/convert',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({"value": "convert"}),
        success: function(response) {
            console.log('converting');

            
        var iframe = document.getElementById( 'trainee-fbx' );
        var uid = response[0];

        // By default, the latest version of the viewer API will be used.
        var client = new Sketchfab( iframe );

        // Alternatively, you can request a specific version.
        // var client = new Sketchfab( '1.12.1', iframe );

        client.init( uid, {
            success: function onSuccess( api ){
                api.start();
                api.addEventListener( 'viewerready', function() {
                    console.log( 'Viewer is ready' );

                } );
            },
            error: function onError() {
                console.log( 'Viewer error' );
            }
        });
            },
            error: function(error) {
                console.log(error);
            }
    });
}

function handleDocSearch() {
    console.log("Doc Search");
    console.log(docSearchInput.value);

    $.ajax({
        url: '/search',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({"question": docSearchInput.value}),
        success: function(response) {
            $("#generatedText").text(response.result);
            console.log(response.result);
        },
        error: function(error) {
            console.log(error);
        }
    });
}

/*
function handleTraineeInput() {
    const traineeFile = this.files[0];
    console.log(traineeFile);

    const reader = new FileReader();

    reader.onload = function(event) {
        const dataURL = event.target.result;

        traineeVideo.pause();
        traineeSource.setAttribute('src', dataURL);
        traineeSource.setAttribute('type', traineeFile.type);

        console.log(dataURL);

        traineeVideo.setAttribute("controls", "controls");
        traineeVideo.load();
        traineeVideo.play();
    };

    reader.readAsDataURL(traineeFile);
}*/