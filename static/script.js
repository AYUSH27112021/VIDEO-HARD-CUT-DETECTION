const form = document.querySelector('form');

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const fileInput = document.querySelector('input[type="file"]');
    const progressBar = document.createElement('progress');
    const submitButton = document.querySelector('button[type="submit"]');

    submitButton.disabled = true;
    submitButton.style.cursor = 'wait';

    form.appendChild(progressBar);

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/');
    xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
            progressBar.value = (event.loaded / event.total) * 100;
        }
    });
    xhr.addEventListener('load', () => {
        submitButton.disabled = false;
        submitButton.style.cursor = 'pointer';
        progressBar.remove();
        location.reload();
    });
    xhr.send(formData);
});
