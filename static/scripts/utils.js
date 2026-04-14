// DOM хелпер
function $(id) {
    return document.getElementById(id);
}

// Показать сообщение
function showMessage(type, text) {
    const errorDiv = $('errorMessage');
    const successDiv = $('successMessage');

    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    if (type === 'error') {
        errorDiv.textContent = text;
        errorDiv.style.display = 'block';
        setTimeout(() => errorDiv.style.display = 'none', 5000);
    } else if (type === 'success') {
        successDiv.textContent = text;
        successDiv.style.display = 'block';
        setTimeout(() => successDiv.style.display = 'none', 3000);
    }
}

// Показать/скрыть загрузчик
function showLoader(show) {
    const overlay = $('loaderOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

// Скачать файл
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Форматировать имя файла
function formatFilename(facultyName) {
    const date = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    return facultyName + '_' + date + '.pdf';
}

// Заблокировать/разблокировать кнопку
function setButtonLoading(loading) {
    const btn = $('createButton');
    if (loading) {
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = '<span class="button-spinner"></span> Создание...';
        btn.disabled = true;
    } else {
        btn.innerHTML = btn.dataset.originalText || 'Создать и скачать PDF';
        btn.disabled = false;
    }
}