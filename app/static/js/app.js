let currentTaskId = null;
let pollInterval = null;
let transcriptData = [];
let player = null; // YT Player

// --- API Calls ---

async function submitYoutube() {
    const url = document.getElementById('ytUrl').value;
    const lang = document.getElementById('ytLang').value;
    if(!url) return alert("Enter URL");

    const formData = new FormData();
    formData.append('url', url);
    formData.append('language', lang);

    startTask('/api/transcribe/youtube', formData);
}

async function submitFile() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        return alert("Please select a file first.");
    }
    const file = fileInput.files[0];
    const lang = document.getElementById('fileLang').value;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', lang);

    startTask('/api/transcribe/upload', formData);
}

async function startTask(endpoint, formData) {
    const statusDiv = document.getElementById('statusMsg');
    statusDiv.classList.remove('hidden');
    statusDiv.innerText = "Uploading & initializing... (Please wait)";
    
    try {
        const res = await fetch(endpoint, { method: 'POST', body: formData });
        if (!res.ok) throw new Error("Server Error: " + res.statusText);
        
        const data = await res.json();
        currentTaskId = data.task_id;
        pollStatus();
    } catch (e) {
        statusDiv.innerText = "Error: " + e.message;
        alert("Error starting task: " + e.message);
    }
}

function pollStatus() {
    pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`/api/status/${currentTaskId}`);
            const data = await res.json();

            document.getElementById('statusMsg').innerText = `Status: ${data.status.toUpperCase()}`;

            if (data.status === 'completed') {
                clearInterval(pollInterval);
                loadWorkspace(data);
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                document.getElementById('statusMsg').innerText = "Transcription Failed. Check console/logs.";
                alert("Transcription failed.");
            }
        } catch (e) {
            console.error("Polling error", e);
        }
    }, 2000);
}

// --- Workspace Logic ---

function loadWorkspace(data) {
    document.getElementById('workspace').classList.remove('hidden');
    document.getElementById('videoTitle').innerText = data.video_title || "Processed Video";
    document.getElementById('summaryText').innerText = data.summary || "No summary available.";
    
    transcriptData = data.transcript || [];
    renderTranscript();
    setupPlayer(data);
}

function setupPlayer(data) {
    const container = document.getElementById('videoContainer');
    container.innerHTML = ''; 

    // Simple check to decide if we show YT iframe or a Placeholder
    // (Real implementation would pass YT ID properly)
    if (data.video_source === 'youtube' || (data.video_url && data.video_url.includes('youtube'))) {
        container.innerHTML = '<iframe id="ytplayer" type="text/html" width="100%" height="100%" src="https://www.youtube.com/embed/?enablejsapi=1" frameborder="0"></iframe>';
        // Initialize YT Player API if loaded
        if (window.YT && window.YT.Player) {
            player = new YT.Player('ytplayer', {
                events: { 'onStateChange': () => {} }
            });
        }
    } else {
        container.innerHTML = '<div class="flex items-center justify-center h-full text-gray-400 bg-gray-900">Video Sync Simulation<br>(Local File Mode)</div>';
    }
}

function renderTranscript() {
    const container = document.getElementById('transcriptContainer');
    container.innerHTML = '';

    if (!transcriptData || transcriptData.length === 0) {
        container.innerHTML = '<div class="p-4 text-gray-500">No transcript segments found.</div>';
        return;
    }

    transcriptData.forEach((seg, index) => {
        const div = document.createElement('div');
        div.className = "transcript-line p-2 rounded transition border-l-2 border-transparent hover:bg-blue-50";
        div.id = `seg-${index}`;
        div.dataset.start = seg.start;
        
        const timestamp = formatTime(seg.start);
        
        div.innerHTML = `
            <div class="flex gap-2 mb-1">
                <span onclick="seekVideo(${seg.start})" class="text-blue-600 font-mono text-xs font-bold cursor-pointer hover:underline">[${timestamp}]</span>
                <span class="text-xs font-bold text-gray-600">${seg.speaker || 'Speaker'}</span>
            </div>
            <p contenteditable="true" onblur="updateText(${index}, this.innerText)" class="text-sm leading-relaxed outline-none focus:bg-white border border-transparent focus:border-gray-200 p-1 rounded">${seg.text}</p>
        `;
        
        container.appendChild(div);
    });
}

function formatTime(seconds) {
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
}

function updateText(index, newText) {
    if (transcriptData[index]) {
        transcriptData[index].text = newText;
    }
}

async function saveChanges() {
    if (!currentTaskId) return;
    try {
        await fetch(`/api/update/${currentTaskId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ segments: transcriptData })
        });
        alert("Changes saved to database!");
    } catch (e) {
        alert("Save failed: " + e);
    }
}

// --- Export Logic ---

function downloadFormat(format) {
    let content = "";
    
    // Using explicit string concatenation to avoid syntax errors with backslashes
    if (format === 'srt') {
        transcriptData.forEach((seg, i) => {
            content += (i + 1) + "\n";
            content += formatTimeSRT(seg.start) + " --> " + formatTimeSRT(seg.end) + "\n";
            content += seg.text + "\n\n";
        });
    } else if (format === 'txt') {
        transcriptData.forEach(seg => {
            content += "[" + formatTime(seg.start) + "] " + seg.speaker + ": " + seg.text + "\n";
        });
    } else if (format === 'vtt') {
        content = "WEBVTT\n\n";
        transcriptData.forEach((seg) => {
            content += formatTimeSRT(seg.start) + " --> " + formatTimeSRT(seg.end) + "\n";
            content += seg.text + "\n\n";
        });
    }

    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function formatTimeSRT(seconds) {
    if (!seconds && seconds !== 0) return "00:00:00,000";
    const date = new Date(0);
    date.setSeconds(seconds);
    const iso = date.toISOString().substr(11, 8);
    return iso + ",000"; 
}

function seekVideo(time) {
    if (player && typeof player.seekTo === 'function') {
        player.seekTo(time, true);
    }
    
    // UI Highlight
    document.querySelectorAll('.transcript-line').forEach(el => el.classList.remove('active-segment', 'bg-blue-100'));
    const segs = Array.from(document.querySelectorAll('.transcript-line'));
    const active = segs.find(el => {
        const start = parseFloat(el.dataset.start);
        return start <= time && (start + 5) >= time; // Approximate active window
    });
    if(active) active.classList.add('active-segment', 'bg-blue-100');
}