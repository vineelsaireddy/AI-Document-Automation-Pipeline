const API_BASE = '/api';

// DOM Elements
const statTotal = document.getElementById('stat-total');
const statCompleted = document.getElementById('stat-completed');
const statFailed = document.getElementById('stat-failed');
const statPending = document.getElementById('stat-pending');
const tableBody = document.getElementById('documents-body');
const fileInput = document.getElementById('file-input');
const uploadStatus = document.getElementById('upload-status');
const chartContainer = document.getElementById('classification-chart');

// Modal Elements
const modal = document.getElementById('doc-modal');
const modalClose = document.getElementById('modal-close');
const modalTitle = document.getElementById('modal-title');
const modalFilename = document.getElementById('modal-filename');
const modalType = document.getElementById('modal-type');
const modalConfidence = document.getElementById('modal-confidence');
const modalStatus = document.getElementById('modal-status');
const modalSummary = document.getElementById('modal-summary');
const modalFields = document.getElementById('modal-fields');

async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE}/dashboard/stats`);
        const data = await response.json();

        statTotal.textContent = data.total_documents;
        statCompleted.textContent = data.completed;
        statFailed.textContent = data.failed;
        statPending.textContent = data.pending;

        updateTable(data.recent_documents);
        updateChart(data.classification_breakdown, data.total_documents);
    } catch (e) {
        console.error("Failed to fetch stats", e);
    }
}

function updateTable(documents) {
    tableBody.innerHTML = '';
    documents.forEach(doc => {
        const tr = document.createElement('tr');

        const date = new Date(doc.upload_time).toLocaleString();

        tr.innerHTML = `
            <td>#${doc.id}</td>
            <td>${doc.filename}</td>
            <td><span class="badge">${doc.doc_type || 'processing'}</span></td>
            <td class="text-${doc.status === 'completed' ? 'success' : doc.status === 'failed' ? 'danger' : 'warning'}">
                ${doc.status}
            </td>
            <td>${date}</td>
            <td><button class="btn btn-primary btn-sm" onclick="viewDocument(${doc.id})">View</button></td>
        `;
        tableBody.appendChild(tr);
    });
}

function updateChart(breakdown, total) {
    chartContainer.innerHTML = '';
    if (total === 0) return;

    for (const [category, count] of Object.entries(breakdown)) {
        const percent = Math.round((count / total) * 100);
        const div = document.createElement('div');
        div.className = 'chart-bar-container';
        div.innerHTML = `
            <div class="chart-label">${category}</div>
            <div class="chart-bar" style="width: ${Math.max(percent, 5)}%"></div>
            <div class="chart-value">${count}</div>
        `;
        chartContainer.appendChild(div);
    }
}

async function handleUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    uploadStatus.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (response.ok) {
            uploadStatus.textContent = "Upload and AI processing completed successfully!";
            uploadStatus.style.color = "var(--success)";
            fetchStats();
            setTimeout(() => viewDocument(result.id), 1000);
        } else {
            uploadStatus.textContent = `Error: ${result.detail}`;
            uploadStatus.style.color = "var(--danger)";
        }
    } catch (e) {
        uploadStatus.textContent = "Failed to upload document.";
        uploadStatus.style.color = "var(--danger)";
    }

    setTimeout(() => {
        uploadStatus.classList.add('hidden');
        uploadStatus.textContent = "Processing document... this may take a few seconds.";
        uploadStatus.style.color = "var(--primary)";
    }, 5000);
}

async function viewDocument(id) {
    try {
        const response = await fetch(`${API_BASE}/documents/${id}`);
        const data = await response.json();

        modalFilename.textContent = data.filename;
        modalType.textContent = data.doc_type || 'Unknown';
        modalConfidence.textContent = data.confidence ? `${(data.confidence * 100).toFixed(1)}%` : 'N/A';
        modalStatus.textContent = data.status;
        modalStatus.className = `text-${data.status === 'completed' ? 'success' : 'danger'}`;

        modalSummary.textContent = data.summary || (data.error_message ? `Failed: ${data.error_message}` : 'Processing or failed without summary.');

        if (data.extracted_fields) {
            modalFields.textContent = JSON.stringify(data.extracted_fields, null, 2);
        } else {
            modalFields.textContent = '{}';
        }

        modal.classList.remove('hidden');
    } catch (e) {
        console.error("Failed to load document", e);
    }
}

// Event Listeners
fileInput.addEventListener('change', handleUpload);
modalClose.addEventListener('click', () => modal.classList.add('hidden'));

// Initial load
fetchStats();
// Refresh stats every 10 seconds to show webhook ingestion
setInterval(fetchStats, 10000);
