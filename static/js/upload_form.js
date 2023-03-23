/*
 * Upload image by image
 */

num_elements = 0;
const forms = [];

function sendForms() {
    const statusDiv = document.getElementById("uploadStatus");
    let form = forms.pop();
    if (form) {
        const request = new XMLHttpRequest();

        request.addEventListener("load", (event) => {
            statusDiv.innerHTML = "Upload status: " + Math.round((num_elements - forms.length)/num_elements*100) + "%";
            setTimeout(function() {sendForms();}, 5); // Give the browser time to render the UI
        });

        request.addEventListener("error", (event) => {
            statusDiv.innerHTML = "Upload Error";
        });

        request.open("POST", "", false);
        request.send(form);
    } else {
        statusDiv.innerHTML="Upload Done";
    }
}

window.onload = function () {
    const form = document.getElementById("uploadForm");

    form.addEventListener("submit", (e) => {
        const statusDiv = document.getElementById("uploadStatus");

        statusDiv.style.display = '';
        form.style.display="none";

        const images = document.getElementById("id_image");
        let max_files = images.files.length;

        Array.from(images.files).forEach((file, i) => {
            const fd = new FormData(form);
            fd.set("image", file);
            forms.push(fd);
        });
        form.reset();
        num_elements = forms.length;
        e.preventDefault();
        sendForms();
    });
}



