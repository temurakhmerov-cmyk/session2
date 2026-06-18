// Global State
let currentTab = 'tree';
let systemState = {
    printers: [],
    heap: [],
    heap_size: 0,
    completed_jobs: [],
    logs: []
};

// SVG configuration for Tree rendering
const SVG_WIDTH = 800;
const SVG_HEIGHT = 320;

document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            currentTab = button.dataset.tab;
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`tab-${currentTab}`).classList.add('active');
            
            // Re-render
            renderHeap();
        });
    });

    // Toggle Printer Form expansion
    const togglePrinterFormBtn = document.getElementById('toggle-printer-form');
    const printerForm = document.getElementById('printer-form');
    const printerCard = togglePrinterFormBtn.closest('.card');
    
    togglePrinterFormBtn.addEventListener('click', () => {
        printerForm.classList.toggle('hidden');
        printerCard.classList.toggle('expanded');
    });

    // Form Submissions
    document.getElementById('job-form').addEventListener('submit', handleAddJob);
    document.getElementById('printer-form').addEventListener('submit', handleAddPrinter);

    // Header buttons
    document.getElementById('btn-generate').addEventListener('click', generateDummyJobs);
    document.getElementById('btn-clear').addEventListener('click', clearSystem);

    // File upload elements and handlers
    const fileDropzone = document.getElementById('file-dropzone');
    const fileInput = document.getElementById('job-file');
    const fileInfoChip = document.getElementById('file-info-chip');
    const fileChipName = document.getElementById('file-chip-name');
    const fileChipSize = document.getElementById('file-chip-size');
    const fileChipRemove = document.getElementById('file-chip-remove');
    const jobNameInput = document.getElementById('job-name');
    const jobPagesInput = document.getElementById('job-pages');

    fileDropzone.addEventListener('click', () => {
        fileInput.click();
    });

    fileDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileDropzone.classList.add('dragover');
    });

    fileDropzone.addEventListener('dragleave', () => {
        fileDropzone.classList.remove('dragover');
    });

    fileDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        fileDropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleSelectedFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleSelectedFile(fileInput.files[0]);
        }
    });

    fileChipRemove.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.value = '';
        fileInfoChip.classList.add('hidden');
        fileDropzone.classList.remove('hidden');
    });

    function handleSelectedFile(file) {
        fileChipName.innerText = file.name;
        const kb = file.size / 1024;
        const mb = kb / 1024;
        const sizeText = mb > 1 ? `(${mb.toFixed(1)} МБ)` : `(${kb.toFixed(1)} КБ)`;
        fileChipSize.innerText = sizeText;
        
        fileDropzone.classList.add('hidden');
        fileInfoChip.classList.remove('hidden');
        
        jobNameInput.value = file.name;
        
        let estimatedPages = 1;
        const ext = file.name.split('.').pop().toLowerCase();
        
        if (['txt', 'py', 'js', 'css', 'json', 'html', 'md'].includes(ext)) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const text = e.target.result;
                const lineCount = text.split('\n').length;
                estimatedPages = Math.max(1, Math.ceil(lineCount / 40));
                jobPagesInput.value = estimatedPages;
            };
            reader.readAsText(file);
        } else if (ext === 'pdf') {
            estimatedPages = Math.max(1, Math.ceil(file.size / 50000));
            jobPagesInput.value = estimatedPages;
        } else {
            estimatedPages = Math.max(1, Math.ceil(file.size / 10240));
            jobPagesInput.value = estimatedPages;
        }
    }

    // Initial load and start Polling
    fetchState();
    setInterval(fetchState, 500); // Опрашиваем сервер дважды в секунду для плавной анимации
});

// Fetch API state
async function fetchState() {
    try {
        const response = await fetch('/api/state');
        if (!response.ok) throw new Error('API error');
        systemState = await response.json();
        
        renderPrinters();
        renderHeap();
        renderHistory();
        renderLogs();
    } catch (err) {
        console.error('Ошибка получения состояния:', err);
    }
}

// Add Job
async function handleAddJob(e) {
    e.preventDefault();
    const nameInput = document.getElementById('job-name');
    const pagesInput = document.getElementById('job-pages');
    const userInput = document.getElementById('job-user');
    const priorityInput = document.querySelector('input[name="priority"]:checked');

    const payload = {
        name: nameInput.value.trim(),
        pages: parseInt(pagesInput.value),
        priority: parseInt(priorityInput.value),
        user: userInput.value.trim()
    };

    try {
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            // Reset form except user
            nameInput.value = '';
            pagesInput.value = '10';
            
            // Reset file input
            const fileInput = document.getElementById('job-file');
            const fileInfoChip = document.getElementById('file-info-chip');
            const fileDropzone = document.getElementById('file-dropzone');
            if (fileInput) fileInput.value = '';
            if (fileInfoChip) fileInfoChip.classList.add('hidden');
            if (fileDropzone) fileDropzone.classList.remove('hidden');
            
            fetchState();
        }
    } catch (err) {
        console.error(err);
    }
}

// Add Printer
async function handleAddPrinter(e) {
    e.preventDefault();
    const nameInput = document.getElementById('printer-name');
    const speedInput = document.getElementById('printer-speed');

    const payload = {
        name: nameInput.value.trim(),
        speed: parseFloat(speedInput.value)
    };

    try {
        const response = await fetch('/api/printers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (response.ok) {
            nameInput.value = '';
            speedInput.value = '1.5';
            // Collapse form
            document.getElementById('printer-form').classList.add('hidden');
            document.getElementById('toggle-printer-form').closest('.card').classList.remove('expanded');
            fetchState();
        }
    } catch (err) {
        console.error(err);
    }
}

// Toggle Printer status
async function togglePrinter(printerId) {
    try {
        await fetch(`/api/printers/${printerId}/toggle`, { method: 'POST' });
        fetchState();
    } catch (err) {
        console.error(err);
    }
}

// Generate random jobs
async function generateDummyJobs() {
    try {
        await fetch('/api/generate-dummy', { method: 'POST' });
        fetchState();
    } catch (err) {
        console.error(err);
    }
}

// Clear system state
async function clearSystem() {
    if (confirm('Вы уверены, что хотите сбросить очередь и очистить историю?')) {
        try {
            await fetch('/api/clear', { method: 'POST' });
            fetchState();
        } catch (err) {
            console.error(err);
        }
    }
}

// Renders
function renderPrinters() {
    const container = document.getElementById('printers-container');
    if (!systemState.printers || systemState.printers.length === 0) {
        container.innerHTML = '<div class="loading">Нет подключенных принтеров</div>';
        return;
    }

    container.innerHTML = systemState.printers.map(printer => {
        const isOffline = printer.status === 'offline';
        const isPrinting = printer.status === 'printing';
        
        let statusText = 'Свободен';
        let statusClass = 'status-idle';
        if (isOffline) {
            statusText = 'Выкл';
            statusClass = 'status-offline';
        } else if (isPrinting) {
            statusText = 'Печать';
            statusClass = 'status-printing';
        }

        const powerIcon = isOffline ? '🔌' : '🚫';
        const powerTitle = isOffline ? 'Включить принтер' : 'Отключить принтер';

        let progressHtml = '';
        if (isPrinting && printer.current_job) {
            const job = printer.current_job;
            const progress = ((job.pages - printer.remaining_pages) / job.pages) * 100;
            progressHtml = `
                <div class="printer-progress-details">
                    <div class="printer-job-title">${job.id}: ${job.name} (${Math.round(printer.remaining_pages)} / ${job.pages} стр.)</div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: ${progress}%"></div>
                    </div>
                </div>
            `;
        }

        return `
            <div class="printer-card">
                <div class="printer-info-row">
                    <div class="printer-name-group">
                        <span class="printer-name">${printer.name}</span>
                        <span class="printer-speed-desc">Скорость: ${printer.speed} стр/сек</span>
                    </div>
                    <div class="printer-actions">
                        <span class="status-badge ${statusClass}">${statusText}</span>
                        <button class="power-btn" onclick="togglePrinter('${printer.id}')" title="${powerTitle}">${powerIcon}</button>
                    </div>
                </div>
                ${progressHtml}
            </div>
        `;
    }).join('');
}

function renderHeap() {
    const heapSizeBadge = document.getElementById('heap-size-badge');
    heapSizeBadge.innerText = `Задач в очереди: ${systemState.heap_size}`;

    if (currentTab === 'tree') {
        renderHeapTree();
    } else {
        renderHeapArray();
    }
}

// Render Heap as Binary Tree (SVG)
function renderHeapTree() {
    const svg = document.getElementById('heap-svg');
    const emptyMsg = document.getElementById('empty-heap-msg');
    
    // Clear SVG
    svg.innerHTML = '';
    
    const heap = systemState.heap;
    if (!heap || heap.length === 0) {
        emptyMsg.classList.remove('hidden');
        return;
    }
    
    emptyMsg.classList.add('hidden');
    
    // Вычисляем необходимую высоту SVG на основе количества уровней кучи
    const maxIndex = heap.length - 1;
    const levels = Math.floor(Math.log2(maxIndex + 1)) + 1;
    const computedHeight = Math.max(320, levels * 75 + 40);
    svg.setAttribute('height', computedHeight);
    svg.setAttribute('viewBox', `0 0 800 ${computedHeight}`);
    
    // Calculate node coordinates
    const nodes = [];
    for (let i = 0; i < heap.length; i++) {
        const level = Math.floor(Math.log2(i + 1));
        const pos = i - (Math.pow(2, level) - 1);
        const levelNodesCount = Math.pow(2, level);
        
        // Node Y position
        const y = 40 + level * 75;
        
        // Node X position: divide SVG width by number of nodes at this level
        const span = SVG_WIDTH / levelNodesCount;
        const x = (pos + 0.5) * span;
        
        nodes.push({ x, y, job: heap[i].item, priority: heap[i].priority, index: i });
    }

    // 1. Draw connection lines first (so they are under circles)
    for (let i = 1; i < nodes.length; i++) {
        const parentIdx = Math.floor((i - 1) / 2);
        const parent = nodes[parentIdx];
        const child = nodes[i];
        
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', parent.x);
        line.setAttribute('y1', parent.y);
        line.setAttribute('x2', child.x);
        line.setAttribute('y2', child.y);
        line.setAttribute('class', 'tree-connection-line');
        svg.appendChild(line);
    }

    // 2. Draw node circles and text
    nodes.forEach(node => {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        
        // Circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', node.x);
        circle.setAttribute('cy', node.y);
        circle.setAttribute('r', '22');
        circle.setAttribute('class', `tree-node-circle node-prio-${node.priority}`);
        
        // Shorten JOB_001 to J01
        let shortId = node.job.id;
        if (shortId.startsWith('JOB_')) {
            shortId = 'J' + shortId.substring(4);
        }
        
        // Text for ID (e.g. J01)
        const textId = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textId.setAttribute('x', node.x);
        textId.setAttribute('y', node.y - 2);
        textId.setAttribute('class', 'tree-node-text-id');
        textId.textContent = shortId;
        
        // Text for Index (e.g., [0], [1])
        const textIdx = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textIdx.setAttribute('x', node.x);
        textIdx.setAttribute('y', node.y + 14);
        textIdx.setAttribute('class', 'tree-node-text-prio');
        textIdx.textContent = `[${node.index}]`;

        // Tooltip description
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `Индекс: ${node.index}\nID: ${node.job.id}\nДокумент: ${node.job.name}\nПриоритет: ${node.priority}\nСтраниц: ${node.job.pages}\nАвтор: ${node.job.user}`;
        
        group.appendChild(circle);
        group.appendChild(textId);
        group.appendChild(textIdx);
        group.appendChild(title);
        svg.appendChild(group);
    });
}

// Render Heap as Array layout
function renderHeapArray() {
    const container = document.getElementById('array-container');
    const heap = systemState.heap;
    
    if (!heap || heap.length === 0) {
        container.innerHTML = '<div class="empty-msg">Очередь пуста. Задачи отсутствуют.</div>';
        return;
    }

    container.innerHTML = heap.map((entry, index) => {
        const job = entry.item;
        let shortId = job.id;
        if (shortId.startsWith('JOB_')) {
            shortId = 'J' + shortId.substring(4);
        }

        return `
            <div class="array-cell cell-prio-${entry.priority}" title="Имя: ${job.name}\nАвтор: ${job.user}\nСтраниц: ${job.pages}">
                <div class="array-cell-index">[${index}]</div>
                <div class="array-cell-id">${shortId}</div>
                <div class="array-cell-prio">P: ${entry.priority}</div>
            </div>
        `;
    }).join('');
}

function renderHistory() {
    const body = document.getElementById('history-body');
    const completed = systemState.completed_jobs;

    if (!completed || completed.length === 0) {
        body.innerHTML = `
            <tr>
                <td colspan="4" class="no-history">История пуста</td>
            </tr>
        `;
        return;
    }

    // Render in reverse chronological order (newest first)
    const reversed = [...completed].reverse();
    body.innerHTML = reversed.map(job => {
        return `
            <tr>
                <td style="font-family: var(--font-mono); font-weight:bold;">${job.id}</td>
                <td title="${job.name}">${job.name}</td>
                <td>${job.pages}</td>
                <td>${job.user}</td>
            </tr>
        `;
    }).join('');
}

function renderLogs() {
    const consoleLogs = document.getElementById('console-logs');
    const logs = systemState.logs;

    if (!logs || logs.length === 0) {
        consoleLogs.innerHTML = '<div>Система запущена. Ожидание задач...</div>';
        return;
    }

    const previousLogCount = consoleLogs.children.length;
    consoleLogs.innerHTML = logs.map(log => `<div>${escapeHtml(log)}</div>`).join('');

    // Scroll to bottom if new logs arrived
    if (logs.length > previousLogCount) {
        consoleLogs.scrollTop = consoleLogs.scrollHeight;
    }
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
