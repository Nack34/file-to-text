// ---------- Selección de elementos ----------
const fileInput = document.getElementById('fileUpload');
const fileNameDisplay = document.getElementById('fileName');
const errorMessage = document.getElementById('errorMessage');

const downloadBtn = document.getElementById('downloadBtn');
const uploadBtn = document.getElementById('uploadBtn');
const uploadText = uploadBtn ? uploadBtn.querySelector('.upload-text') : null;
const uploadSpinner = uploadBtn ? uploadBtn.querySelector('.spinner') : null;

const processBtn = document.getElementById('processBtn');

const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const controls = document.getElementById('controls');

let fileTime = null;
let newFilename = null;
let isUploading = false;
let isProcessing = false;

// ---------- Helpers UI ----------
function showElement(el) { if (el) el.style.display = ''; }
function hideElement(el) { if (el) el.style.display = 'none'; }

function setUploadLoading(on) {
  isUploading = on;
  if (fileInput) fileInput.disabled = on;
  if (!uploadBtn || !uploadText || !uploadSpinner) return;
  if (on) {
    uploadBtn.classList.add('loading');
    uploadSpinner.style.display = 'inline-block';
    uploadText.textContent = 'Subiendo...';
    uploadBtn.setAttribute('aria-busy', 'true');
  } else {
    uploadBtn.classList.remove('loading');
    uploadSpinner.style.display = 'none';
    uploadText.textContent = 'Cargar pdf';
    uploadBtn.removeAttribute('aria-busy');
  }
}

function showFullLoading(text = 'Procesando...') {
  if (loadingText) loadingText.textContent = text;
  if (loadingOverlay) loadingOverlay.style.display = 'flex';
}

function hideFullLoading() {
  if (loadingOverlay) loadingOverlay.style.display = 'none';
}

function resetToInitialState() {
  fileTime = null;
  newFilename = null;
  if (fileNameDisplay) fileNameDisplay.textContent = '';
  if (errorMessage) errorMessage.textContent = '';

  hideElement(processBtn);
  hideElement(downloadBtn);

  showElement(uploadBtn);
  showElement(controls);
  hideFullLoading();
}

// ---------- Subida ----------
if (fileInput) {
  fileInput.addEventListener('change', async () => {
    if (isUploading || isProcessing) return;
    const file = fileInput.files[0];
    if (!file) return;

    fileTime = null;
    newFilename = null;
    hideElement(processBtn);
    hideElement(downloadBtn);
    if (errorMessage) errorMessage.textContent = '';
    if (fileNameDisplay) fileNameDisplay.textContent = file.name;

    const formData = new FormData();
    formData.append('file', file);

    setUploadLoading(true);
    try {
      const resp = await fetch('/pdf_to_text/send_file', { method: 'POST', body: formData });
      if (!resp.ok) {
        let errText = resp.statusText;
        try {
          const errJson = await resp.json();
          errText = errJson.error || errJson.detail || JSON.stringify(errJson);
        } catch (e) {
          try { errText = await resp.text(); } catch {}
        }
        if (errorMessage) errorMessage.textContent = `Error al enviar el archivo: ${errText}`;
        return;
      }
      const result = await resp.json();
      if (result.error) {
        if (errorMessage) errorMessage.textContent = `Error al enviar el archivo: ${result.error}`;
        return;
      }
      if (result.file_time) {
        fileTime = result.file_time;
        showElement(processBtn);
        hideElement(downloadBtn);
        if (errorMessage) errorMessage.textContent = '';
      } else {
        if (errorMessage) errorMessage.textContent = 'No se recibió file_time del backend.';
      }
    } catch (error) {
      if (errorMessage) errorMessage.textContent = `Error al enviar el archivo: ${error.message}`;
    } finally {
      setUploadLoading(false);
      fileInput.value = '';
    }
  });
}

// ---------- Proceso ----------
if (processBtn) {
  processBtn.addEventListener('click', async () => {
    if (!fileTime) {
      if (errorMessage) errorMessage.textContent = 'No hay file_time. Primero cargá un pdf.';
      return;
    }
    if (isProcessing || isUploading) return;

    isProcessing = true;
    if (errorMessage) errorMessage.textContent = '';
    if (controls) controls.style.display = 'none';
    showFullLoading('Procesando pdf...');

    try {
      const resp = await fetch(`/pdf_to_text/proc_file/${encodeURIComponent(fileTime)}`);
      if (!resp.ok) {
        let errText = resp.statusText;
        try {
          const errJson = await resp.json();
          errText = errJson.error || errJson.detail || JSON.stringify(errJson);
        } catch (e) {
          try { errText = await resp.text(); } catch {}
        }
        hideFullLoading();
        if (controls) controls.style.display = '';
        resetToInitialState();
        if (errorMessage) errorMessage.textContent = `Error al procesar el pdf: ${errText}`;
        return;
      }
      const result = await resp.json();
      if (result.error) {
        hideFullLoading();
        if (controls) controls.style.display = '';
        resetToInitialState();
        if (errorMessage) errorMessage.textContent = `Error al procesar el pdf: ${result.error}`;
        return;
      }
      if (result.new_filename) {
        newFilename = result.new_filename;
        hideFullLoading();
        if (controls) controls.style.display = '';
        showElement(uploadBtn);
        showElement(downloadBtn);
        hideElement(processBtn);
        if (fileNameDisplay) fileNameDisplay.textContent = `Resultado: ${newFilename}`;
        if (errorMessage) errorMessage.textContent = '';
      } else {
        hideFullLoading();
        if (controls) controls.style.display = '';
        resetToInitialState();
        if (errorMessage) errorMessage.textContent = 'No se recibió new_filename del backend.';
      }
    } catch (error) {
      hideFullLoading();
      if (controls) controls.style.display = '';
      resetToInitialState();
      if (errorMessage) errorMessage.textContent = `Error al procesar el pdf: ${error.message}`;
    } finally {
      isProcessing = false;
    }
  });
}

// ---------- Descarga ----------
if (downloadBtn) {
  downloadBtn.addEventListener('click', async () => {
    if (!newFilename) return;
    downloadBtn.disabled = true;
    const originalText = downloadBtn.textContent;
    downloadBtn.textContent = 'Descargando...';
    try {
      const resp = await fetch(`/pdf_to_text/download_file/${encodeURIComponent(newFilename)}`);
      if (!resp.ok) {
        let errText = resp.statusText;
        try {
          const errJson = await resp.json();
          errText = errJson.detail || JSON.stringify(errJson);
        } catch {
          try { errText = await resp.text(); } catch {}
        }
        if (errorMessage) errorMessage.textContent = `Error al descargar el archivo: ${errText}`;
        return;
      }
      const blob = await resp.blob();
      const a = document.createElement('a');
      const url = URL.createObjectURL(blob);
      a.href = url;
      a.download = newFilename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      if (errorMessage) errorMessage.textContent = `Error al descargar el archivo: ${error.message}`;
    } finally {
      downloadBtn.disabled = false;
      downloadBtn.textContent = originalText;
    }
  });
}

// ---------- Init ----------
document.addEventListener('DOMContentLoaded', () => { resetToInitialState(); });
