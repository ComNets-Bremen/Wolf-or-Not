/*
 * Limit number of uploaded files to a certain number
 */

window.onload = function () {
    const file_input = document.getElementById('id_image');
    file_input.addEventListener('change', (event) => {
        if (file_input.files.length >= 1000){
            alert("Maximum 1000 files can be uploaded at once. Selected number of files: " + file_input.files.length);
            file_input.value = "";
        }
    });
}
