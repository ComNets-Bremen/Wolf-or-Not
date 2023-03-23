/*
 * Upload image by image
 */

num_elements = 0;
total_elements = 0;
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
        statusDiv.innerHTML="Upload Done: " + total_elements + " images.";
    }
}

window.onload = function () {
    const form = document.getElementById("uploadForm");

    form.addEventListener("submit", (e) => {
        const statusDiv = document.getElementById("uploadStatus");

        statusDiv.style.display = '';
        form.style.display="none";

        const images = document.getElementById("id_image");

        total_elements = images.files.length;

        let split_counter = 0

        let fd = new FormData(form);
        fd.delete("image");
        Array.from(images.files).forEach((file, i) => {
            split_counter++;
            if (split_counter >= 25) { // Upload in batches of 25 images
                split_counter = 0;
                forms.push(fd);
                fd = new FormData(form);
                fd.delete("image");
            }
            fd.append("image", file);
        });
        forms.push(fd);

        form.reset();
        num_elements = forms.length;
        e.preventDefault();
        sendForms();
    });
}



