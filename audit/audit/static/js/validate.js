function validateFile() {
    const fileInput = document.querySelector('input[type="file"]');
    const errorDiv = document.getElementById('file-error');
    const file = fileInput.files[0];
    if (!file) return true;

    const allowedExtensions = ['sol', 'txt'];
    const fileExtension = file.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
        errorDiv.textContent = "Неподдерживаемый формат файла. Разрешены только .sol и .txt";
        return false;
    }

    errorDiv.textContent = "";
    return true;
}

document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("file-upload");
    const fileNameSpan = document.getElementById("file-name");

    if (fileInput) {
        fileInput.addEventListener("change", function () {
            const file = fileInput.files[0];
            fileNameSpan.textContent = file ? file.name : "Файл не выбран";
        });
    }
});
