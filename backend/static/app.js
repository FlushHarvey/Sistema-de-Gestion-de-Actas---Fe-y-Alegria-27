const dropZone = document.getElementById('drop-zone');
const folderInput = document.getElementById('folder-input');
const fileInput = document.getElementById('file-input');
const progressContainer = document.getElementById('progress-container');
const progressBar = document.getElementById('progress-bar');
const progressPercent = document.getElementById('progress-percent');
const resultsContainer = document.getElementById('results-container');
const resultsBody = document.getElementById('results-body');
const statSuccess = document.getElementById('stat-success');
const statFail = document.getElementById('stat-fail');
const btnDownload = document.getElementById('btn-download');

// --- Event Listeners ---

// Drag & Drop events
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('active'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('active'), false);
});

dropZone.addEventListener('drop', handleDrop, false);
folderInput.addEventListener('change', (e) => handleFiles(e.target.files), false);
fileInput.addEventListener('change', (e) => handleFiles(e.target.files), false);

// Dropzone click - Default to folder input, but now we have buttons so maybe disable this or ask user?
// User has explicit buttons now. Let's keep dropzone click pointing to folder input as default or remove it to avoid confusion?
// Given the buttons are inside the dropzone visual area, clicking the empty space might be ambiguous.
// Let's default to file input for "click on box" as it's more standard, or keep folder?
// The user explicitly asked for file selection. Let's make the box click open file selection (more common expectation) or remove the generic click.
// However, I'll comment out the generic dropZone click to force user to use the specific buttons.
// dropZone.addEventListener('click', () => folderInput.click());

btnDownload.addEventListener('click', () => {
    window.location.href = '/descargar';
});

// --- Handlers ---

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

async function handleFiles(files) {
    if (files.length === 0) return;

    // Solo archivos PDF
    const pdfFiles = [];
    for (let i = 0; i < files.length; i++) {
        if (files[i].name.toLowerCase().endsWith('.pdf')) {
            pdfFiles.push(files[i]);
        }
    }

    if (pdfFiles.length === 0) {
        alert("No se detectaron archivos PDF en la selección.");
        return;
    }

    // Reset UI
    progressContainer.classList.remove('hidden');
    resultsContainer.classList.remove('hidden');
    resultsBody.innerHTML = '';
    statSuccess.textContent = '0 Éxitos';
    statFail.textContent = '0 Errores';
    progressBar.style.width = '0%';
    progressPercent.textContent = '0%';

    let exitososTotal = 0;
    let fallidosTotal = 0;
    const batchSize = 10;
    const totalFiles = pdfFiles.length;

    for (let i = 0; i < totalFiles; i += batchSize) {
        const batch = pdfFiles.slice(i, i + batchSize);
        const formData = new FormData();
        batch.forEach(file => formData.append('files', file));

        const currentStep = i + batch.length;
        updateProgress(Math.round((i / totalFiles) * 100), `Procesando lote ${Math.floor(i / batchSize) + 1}... (${currentStep}/${totalFiles})`);

        try {
            const response = await fetch('/procesar-carpeta', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Error en el procesamiento del lote");
            }

            const data = await response.json();
            exitososTotal += data.exitosos;
            fallidosTotal += data.fallidos;

            appendResults(data.resultados, exitososTotal, fallidosTotal);
            updateProgress(Math.round((currentStep / totalFiles) * 100));

        } catch (error) {
            console.error(error);
            alert(`Error en lote: ${error.message}`);
        }
    }

    updateProgress(100, "¡Todo el procesamiento completado!");
}

function appendResults(resultados, exitosos, fallidos) {
    statSuccess.textContent = `${exitosos} Éxitos`;
    statFail.textContent = `${fallidos} Errores`;

    resultados.forEach(res => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-gray-50 transition border-b border-gray-100 text-sm animate-fade-in";

        const isError = res.estado === 'error';
        const statusClass = isError ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold';
        const meta = res.metadata || {};

        tr.innerHTML = `
            <td class="px-6 py-4">${meta.anio || '-'}</td>
            <td class="px-6 py-4">${meta.nivel || '-'}</td>
            <td class="px-6 py-4">${meta.grado_seccion || '-'}</td>
            <td class="px-6 py-4 ${statusClass}">${res.estado.toUpperCase()}</td>
            <td class="px-6 py-4 max-w-xs truncate" title="${res.nuevo_nombre || res.mensaje}">${res.nuevo_nombre || res.mensaje}</td>
        `;
        resultsBody.appendChild(tr);
    });
}

function updateProgress(percent, text) {
    progressBar.style.width = `${percent}%`;
    progressPercent.textContent = `${percent}%`;
    if (text) document.getElementById('status-text').textContent = text;
}

function renderResults(data) {
    progressContainer.classList.add('hidden');
    resultsContainer.classList.remove('hidden');

    statSuccess.textContent = `${data.exitosos} Éxitos`;
    statFail.textContent = `${data.fallidos} Errores`;

    data.resultados.forEach(res => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-gray-50 transition border-b border-gray-100 text-sm";

        const isError = res.estado === 'error';
        const statusClass = isError ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold';
        const meta = res.metadata || {};

        tr.innerHTML = `
            <td class="px-6 py-4">${meta.anio || '-'}</td>
            <td class="px-6 py-4">${meta.nivel || '-'}</td>
            <td class="px-6 py-4">${meta.grado_seccion || '-'}</td>
            <td class="px-6 py-4 ${statusClass}">${res.estado.toUpperCase()}</td>
            <td class="px-6 py-4 max-w-xs truncate" title="${res.nuevo_nombre || res.mensaje}">${res.nuevo_nombre || res.mensaje}</td>
        `;
        resultsBody.appendChild(tr);
    });
}
