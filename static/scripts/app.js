// API запросы
const api = {
    async getFaculties() {
        const response = await fetch('/faculties');
        const data = await response.json();
        return data.faculties || [];
    },

    async renderPDF(facultyName) {
        const response = await fetch('/render', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ faculty_name: facultyName })
        });

        if (!response.ok) {
            if (response.status === 404) {
                const error = await response.json();
                throw new Error(error.detail || 'Факультет не найден');
            }
            throw new Error('Ошибка сервера: ' + response.status);
        }

        const blob = await response.blob();
        if (blob.type !== 'application/pdf') {
            throw new Error('Сервер вернул некорректный файл');
        }

        return blob;
    }
};

// UI функции
const ui = {
    async loadFaculties() {
        const select = $('facultiesSelect');
        try {
            const faculties = await api.getFaculties();

            select.innerHTML = '<option value="">-- Выберите факультет --</option>';

            faculties.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                select.appendChild(option);
            });
        } catch (error) {
            console.error('Ошибка загрузки факультетов:', error);
            select.innerHTML = '<option value="">Ошибка загрузки</option>';
            showMessage('error', 'Не удалось загрузить список факультетов');
        }
    },

    async createAndDownload() {
        const selectedValue = $('facultiesSelect').value;

        if (!selectedValue) {
            showMessage('error', 'Пожалуйста, выберите факультет');
            return;
        }

        setButtonLoading(true);
        showLoader(true);

        try {
            const blob = await api.renderPDF(selectedValue);
            const filename = formatFilename(selectedValue);
            downloadBlob(blob, filename);
            showMessage('success', 'PDF для факультета "' + selectedValue + '" успешно скачан!');
        } catch (error) {
            console.error('Ошибка:', error);
            showMessage('error', 'Ошибка: ' + error.message);
        } finally {
            setButtonLoading(false);
            showLoader(false);
        }
    }
};

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    $('createButton').addEventListener('click', () => ui.createAndDownload());
    ui.loadFaculties();
});