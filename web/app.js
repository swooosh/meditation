// Initialize the app
let currentFilter = 'all';
const FILTER_LABELS = {
    ATTN: "Attention",
    ARC: "Breathwork",
    PERF: "Performance",
    RECON: "Emotional",
    SLEEP: "Sleep",
    CREA: "Creative",
    SENSE: "Sensory",
    META: "Self-Model",
    FLOW: "Flow State",
    BODY: "Somatic",
    SOC: "Social",
    PAIN: "Pain",
    SUN: "Small Universe"
};
const DIAGRAM_TYPES = [
    { key: "timeline", label: "Phase Timeline" },
    { key: "signal", label: "Signal Chain" },
    { key: "flow", label: "Practice Flow" }
];

function init() {
    if (window.mermaid) {
        window.mermaid.initialize({ startOnLoad: false, theme: "dark" });
    }
    renderStats();
    renderFilters();
    renderFamilies();
    setupFilters();
}

function setupFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            renderFamilies();
        });
    });
}

function renderFilters() {
    const filters = document.getElementById('filters');
    filters.innerHTML = '';

    const allButton = document.createElement('button');
    allButton.className = 'filter-btn active';
    allButton.dataset.filter = 'all';
    allButton.textContent = 'All Families';
    filters.appendChild(allButton);

    Object.keys(PROTOCOLS).forEach((familyId) => {
        const btn = document.createElement('button');
        btn.className = 'filter-btn';
        btn.dataset.filter = familyId;
        btn.textContent = FILTER_LABELS[familyId] || familyId;
        filters.appendChild(btn);
    });
}

function renderStats() {
    const familyCount = Object.keys(PROTOCOLS).length;
    const allProtocols = Object.values(PROTOCOLS).flatMap((family) => family.protocols);
    const protocolCount = allProtocols.length;
    const totalMinutes = allProtocols.reduce((sum, protocol) => sum + parseDurationMinutes(protocol.duration), 0);
    const totalHours = `${Math.round(totalMinutes / 60)}h`;

    document.getElementById('protocolCount').textContent = protocolCount;
    document.getElementById('familyCount').textContent = familyCount;
    document.getElementById('totalAudio').textContent = totalHours;
    document.getElementById('footerSummary').textContent = `${protocolCount} Protocols Across ${familyCount} Families`;
}

function parseDurationMinutes(duration) {
    const match = /^(\d+)m$/.exec(duration);
    return match ? Number(match[1]) : 0;
}

function getRenderStatus(protocolId) {
    const statusMap = typeof RENDER_STATUS !== 'undefined' ? RENDER_STATUS : {};
    const entry = statusMap[protocolId];

    if (!entry) {
        return { state: 'not-rendered', label: 'Not Rendered', playable: false };
    }
    if (entry.renderComplete && entry.qcExists && !entry.qcPassed) {
        return { state: 'qc-hold', label: 'QC Hold', playable: false };
    }
    if (entry.renderComplete && !entry.qcExists) {
        return { state: 'qc-pending', label: 'QC Pending', playable: true };
    }
    if (entry.renderComplete) {
        return { state: 'playable', label: 'Playable', playable: true };
    }
    if (entry.renderExists) {
        return { state: 'partial', label: 'Render In Progress', playable: false };
    }
    return { state: 'not-rendered', label: 'Not Rendered', playable: false };
}

function getAssetFamily(familyId, protocolId) {
    if (protocolId.startsWith('FSP-01')) return 'FSP';
    return familyId;
}

function getDocsFamily(familyId, protocolId) {
    if (protocolId.startsWith('FSP-')) return 'FSP';
    return familyId;
}

function getDocsPath(assetFamily, protocolId) {
    return `docs/${assetFamily}/${protocolId}.md`;
}

function getDiagramPath(assetFamily, diagramType) {
    const suffixByType = {
        timeline: "_phase_timeline.md",
        signal: "_signal_chain.md",
        flow: "_practice_flow.md"
    };
    const suffix = suffixByType[diagramType];
    return `docs/${assetFamily}/diagrams/${assetFamily}${suffix}`;
}

function getAudioPath(assetFamily, protocolId, guided = false) {
    const suffix = guided ? "_master-guided.wav" : "_master.wav";
    return `audio/${assetFamily}/${protocolId}${suffix}`;
}

async function fetchMarkdown(path) {
    const response = await fetch(path);
    if (!response.ok) {
        throw new Error(`Failed to fetch ${path}`);
    }
    return response.text();
}

function renderMermaidIn(container) {
    if (!window.mermaid || !container) return;
    const nodes = container.querySelectorAll(".mermaid");
    if (!nodes.length) return;
    window.mermaid.run({ nodes });
}

function diagramButtonsMarkup(assetFamily, protocolId) {
    return DIAGRAM_TYPES.map((d, i) => (
        `<button class="btn btn-docs diagram-btn ${i === 0 ? "active" : ""}" data-diagram="${d.key}" onclick="loadDiagram('${assetFamily}', '${protocolId}', '${d.key}')">${d.label}</button>`
    )).join("");
}

function renderFamilies() {
    const grid = document.getElementById('familyGrid');
    grid.innerHTML = '';
    
    Object.entries(PROTOCOLS).forEach(([familyId, family]) => {
        if (currentFilter !== 'all' && currentFilter !== familyId) return;
        
        const card = document.createElement('div');
        card.className = 'family-card';
        card.dataset.family = familyId;
        
        const isExpanded = currentFilter !== 'all';
        
        card.innerHTML = `
            <div class="family-header">
                <div class="family-name">${family.name}</div>
                <div class="protocol-count">${family.protocols.length}</div>
            </div>
            <div class="family-description">${family.description}</div>
            <div class="protocols-list ${isExpanded ? 'show' : ''}" id="protocols-${familyId}">
                ${family.protocols.map(p => renderProtocol(familyId, p)).join('')}
            </div>
        `;
        
        card.querySelector('.family-header').addEventListener('click', () => {
            const list = card.querySelector('.protocols-list');
            list.classList.toggle('show');
        });
        
        grid.appendChild(card);
    });
}

function renderProtocol(familyId, protocol) {
    const renderStatus = getRenderStatus(protocol.id);
    const playLabel = renderStatus.playable ? '▶ Play' : 'Not Ready';
    const statusBadge = renderStatus.state === 'playable'
        ? ''
        : `<div class="status-badge status-${renderStatus.state}">${renderStatus.label}</div>`;

    return `
        <div class="protocol-item">
            <div class="protocol-header">
                <div class="protocol-title">${protocol.title}</div>
                <div class="protocol-duration">${protocol.duration}</div>
            </div>
            ${statusBadge}
            <div class="protocol-description">${protocol.goal}</div>
            <div class="protocol-actions">
                <button class="btn btn-play" onclick="playProtocol('${familyId}', '${protocol.id}')" ${renderStatus.playable ? '' : 'disabled'}>
                    ${playLabel}
                </button>
            </div>
        </div>
    `;
}

async function playProtocol(familyId, protocolId) {
    const family = PROTOCOLS[familyId];
    const protocol = family.protocols.find(p => p.id === protocolId);
    const assetFamily = getAssetFamily(familyId, protocolId);
    const docsFamily = getDocsFamily(familyId, protocolId);
    const renderStatus = getRenderStatus(protocolId);
    
    const modal = document.getElementById('protocolModal');
    const content = document.getElementById('modalContent');

    if (!renderStatus.playable) {
        content.innerHTML = `
            <h2>${protocol.title}</h2>
            <p style="color: #a0a0a0; margin: 10px 0 20px;">${family.name} • ${protocol.duration}</p>
            <div style="margin: 20px 0;">
                <h3 style="color: #00d4ff; margin-bottom: 10px;">Audio Availability</h3>
                <p style="color: #b0b0b0;">This protocol is currently marked <strong>${renderStatus.label}</strong>. You can still review the documentation and narration.</p>
            </div>
            <div style="margin-top: 20px;">
                <button class="btn btn-docs" onclick="showDocs('${familyId}', '${protocolId}')" style="width: 100%;">
                    View Documentation
                </button>
            </div>
        `;
        modal.classList.add('show');
        return;
    }
    
    const guidedDefault = false;
    const audioPath = getAudioPath(assetFamily, protocolId, guidedDefault);
    const docsPath = getDocsPath(docsFamily, protocolId);
    const narrationPath = `narration/${assetFamily}/${protocolId}_coaching.md`;
    
    content.innerHTML = `
        <h2>${protocol.title}</h2>
        <p style="color: #a0a0a0; margin: 10px 0 20px;">${family.name} • ${protocol.duration}</p>
        
        <div class="audio-player">
            <h3 style="color: #00d4ff; margin-bottom: 10px;">Audio Session</h3>
            <p style="color: #b0b0b0; margin-bottom: 10px;">${protocol.goal}</p>
            <audio id="protocolAudio" controls>
                <source src="${audioPath}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
            <div class="audio-mode-toggle">
                <label class="audio-mode-label">
                    <input type="checkbox" id="guidedToggle" onchange="toggleAudioVersion('${familyId}', '${protocolId}', this.checked)">
                    Guided
                </label>
                <span id="audioModeText" class="audio-mode-text">Unguided track</span>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <h3 style="color: #00d4ff; margin-bottom: 10px;">Documentation</h3>
            <div id="docsContent" class="docs-section" style="color: #b0b0b0;">Loading...</div>
        </div>

        <div style="margin-top: 20px;">
            <h3 style="color: #00d4ff; margin-bottom: 10px;">Session Diagrams</h3>
            <div class="diagram-controls">
                ${diagramButtonsMarkup(familyId, protocolId)}
            </div>
            <div id="diagramContent" class="docs-section" style="color: #b0b0b0;">Loading phase timeline...</div>
        </div>
        
        <div style="margin-top: 20px;">
            <h3 style="color: #00d4ff; margin-bottom: 10px;">Narration Guide</h3>
            <button class="btn btn-docs" onclick="loadNarration('${familyId}', '${protocolId}')" id="narrationBtn" style="width: 100%; margin-bottom: 10px;">
                Load Narration Script
            </button>
            <div id="narrationContent" class="docs-section" style="color: #b0b0b0; display: none;"></div>
        </div>
    `;
    
    modal.classList.add('show');
    
    // Load documentation
    try {
        const markdown = await fetchMarkdown(docsPath);
        document.getElementById('docsContent').innerHTML = renderMarkdown(markdown);
        renderMermaidIn(document.getElementById('docsContent'));
    } catch (error) {
        document.getElementById('docsContent').innerHTML = '<em>Documentation not available</em>';
    }

    await loadDiagram(familyId, protocolId, "timeline");
}

function toggleAudioVersion(familyId, protocolId, guided) {
    const assetFamily = getAssetFamily(familyId, protocolId);
    const audio = document.getElementById("protocolAudio");
    const modeText = document.getElementById("audioModeText");
    if (!audio) return;

    const wasPaused = audio.paused;
    const currentTime = audio.currentTime || 0;
    audio.src = getAudioPath(assetFamily, protocolId, guided);
    audio.load();

    audio.addEventListener("loadedmetadata", () => {
        if (Number.isFinite(currentTime) && currentTime > 0) {
            audio.currentTime = Math.min(currentTime, audio.duration || currentTime);
        }
        if (!wasPaused) {
            audio.play().catch(() => {});
        }
    }, { once: true });

    if (modeText) {
        modeText.textContent = guided ? "Guided track" : "Unguided track";
    }
}

async function loadNarration(familyId, protocolId) {
    const assetFamily = getAssetFamily(familyId, protocolId);
    const narrationPath = `narration/${assetFamily}/${protocolId}_coaching.md`;
    const narrationContent = document.getElementById('narrationContent');
    const narrationBtn = document.getElementById('narrationBtn');
    
    narrationContent.style.display = 'block';
    narrationContent.innerHTML = 'Loading...';
    narrationBtn.style.display = 'none';
    
    try {
        const response = await fetch(narrationPath);
        const markdown = await response.text();
        narrationContent.innerHTML = renderMarkdown(markdown);
    } catch (error) {
        narrationContent.innerHTML = '<em>Narration guide not available</em>';
    }
}

async function showDocs(familyId, protocolId) {
    const family = PROTOCOLS[familyId];
    const protocol = family.protocols.find(p => p.id === protocolId);
    const assetFamily = getAssetFamily(familyId, protocolId);
    const docsFamily = getDocsFamily(familyId, protocolId);
    
    const modal = document.getElementById('protocolModal');
    const content = document.getElementById('modalContent');
    
    const docsPath = getDocsPath(docsFamily, protocolId);
    const narrationPath = `narration/${assetFamily}/${protocolId}_coaching.md`;
    
    content.innerHTML = `
        <h2>${protocol.title}</h2>
        <p style="color: #a0a0a0; margin: 10px 0 20px;">${family.name} • ${protocol.duration}</p>
        
        <div style="margin: 20px 0;">
            <h3 style="color: #00d4ff; margin-bottom: 10px;">Goal</h3>
            <p style="color: #b0b0b0;">${protocol.goal}</p>
        </div>
        
        <div style="margin: 20px 0;">
            <h3 style="color: #00d4ff; margin-bottom: 10px;">Documentation</h3>
            <div id="docsContent" class="docs-section" style="color: #b0b0b0;">Loading...</div>
        </div>

        <div style="margin: 20px 0;">
            <h3 style="color: #00d4ff; margin-bottom: 10px;">Session Diagrams</h3>
            <div class="diagram-controls">
                ${diagramButtonsMarkup(familyId, protocolId)}
            </div>
            <div id="diagramContent" class="docs-section" style="color: #b0b0b0;">Loading phase timeline...</div>
        </div>
        
        <div style="margin: 20px 0;">
            <h3 style="color: #00d4ff; margin-bottom: 10px;">Narration Script</h3>
            <div id="narrationContent" class="docs-section" style="color: #b0b0b0;">Loading...</div>
        </div>
        
        <div style="margin-top: 30px;">
            <button class="btn btn-play" onclick="playProtocol('${familyId}', '${protocolId}')" style="width: 100%;">
                ▶ Play Protocol
            </button>
        </div>
    `;
    
    modal.classList.add('show');
    
    // Load documentation
    try {
        const markdown = await fetchMarkdown(docsPath);
        document.getElementById('docsContent').innerHTML = renderMarkdown(markdown);
        renderMermaidIn(document.getElementById('docsContent'));
    } catch (error) {
        document.getElementById('docsContent').innerHTML = '<em>Documentation not available</em>';
    }
    
    // Load narration
    try {
        const markdown = await fetchMarkdown(narrationPath);
        document.getElementById('narrationContent').innerHTML = renderMarkdown(markdown);
    } catch (error) {
        document.getElementById('narrationContent').innerHTML = '<em>Narration guide not available</em>';
    }

    await loadDiagram(familyId, protocolId, "timeline");
}

async function loadDiagram(assetFamily, protocolId, diagramType) {
    const diagramContent = document.getElementById('diagramContent');
    if (!diagramContent) return;

    document.querySelectorAll('.diagram-btn').forEach((btn) => {
        btn.classList.toggle('active', btn.dataset.diagram === diagramType);
    });

    diagramContent.innerHTML = "Loading...";
    const diagramPath = getDiagramPath(assetFamily, diagramType);
    try {
        const markdown = await fetchMarkdown(diagramPath);
        diagramContent.innerHTML = renderMarkdown(markdown);
        renderMermaidIn(diagramContent);
    } catch (error) {
        diagramContent.innerHTML = "<em>Diagram not available</em>";
    }
}

function closeModal() {
    const modal = document.getElementById('protocolModal');
    modal.classList.remove('show');
    
    // Stop any playing audio
    const audio = modal.querySelector('audio');
    if (audio) {
        audio.pause();
        audio.currentTime = 0;
    }
}

// Close modal on background click
document.getElementById('protocolModal').addEventListener('click', (e) => {
    if (e.target.id === 'protocolModal') {
        closeModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

function renderMarkdown(markdown) {
    const escapeHtml = (text) => text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    const formatInline = (text) => {
        return escapeHtml(text)
            .replace(/`([^`]+)`/g, "<code>$1</code>")
            .replace(/\*\*([^*]+)\*\*/g, '<strong style="color: #ffffff;">$1</strong>')
            .replace(/\*([^*]+)\*/g, "<em>$1</em>");
    };

    const source = (markdown || "").replace(/\r\n/g, "\n");
    const codeBlocks = [];
    const withPlaceholders = source.replace(/```([a-zA-Z0-9_-]+)?\n([\s\S]*?)```/g, (_, lang, body) => {
        const idx = codeBlocks.length;
        codeBlocks.push({ lang: (lang || "").toLowerCase(), body });
        return `__CODEBLOCK_${idx}__`;
    });

    const lines = withPlaceholders.split("\n");
    const out = [];
    const listStack = [];
    let i = 0;

    const closeLists = () => {
        while (listStack.length) {
            out.push(`</${listStack.pop()}>`);
        }
    };

    const ensureListDepth = (depth, type) => {
        while (listStack.length > depth) {
            out.push(`</${listStack.pop()}>`);
        }
        if (listStack.length === depth && listStack[depth - 1] && listStack[depth - 1] !== type) {
            out.push(`</${listStack.pop()}>`);
        }
        while (listStack.length < depth) {
            out.push(`<${type}>`);
            listStack.push(type);
        }
    };

    while (i < lines.length) {
        const line = lines[i];
        const trimmed = line.trim();

        if (!trimmed) {
            closeLists();
            i += 1;
            continue;
        }

        const codeMatch = /^__CODEBLOCK_(\d+)__$/.exec(trimmed);
        if (codeMatch) {
            closeLists();
            out.push(trimmed);
            i += 1;
            continue;
        }

        if (/^>\s?/.test(line)) {
            closeLists();
            const quoteLines = [];
            while (i < lines.length && /^>\s?/.test(lines[i])) {
                quoteLines.push(lines[i].replace(/^>\s?/, ""));
                i += 1;
            }
            out.push(`<blockquote class="md-quote">${renderMarkdown(quoteLines.join("\n"))}</blockquote>`);
            continue;
        }

        const h3 = /^###\s+(.+)$/.exec(line);
        if (h3) {
            closeLists();
            out.push(`<h4 style="color: #00d4ff; margin: 15px 0 10px;">${formatInline(h3[1])}</h4>`);
            i += 1;
            continue;
        }
        const h2 = /^##\s+(.+)$/.exec(line);
        if (h2) {
            closeLists();
            out.push(`<h3 style="color: #00d4ff; margin: 20px 0 10px;">${formatInline(h2[1])}</h3>`);
            i += 1;
            continue;
        }
        const h1 = /^#\s+(.+)$/.exec(line);
        if (h1) {
            closeLists();
            out.push(`<h2 style="color: #00d4ff; margin: 25px 0 15px;">${formatInline(h1[1])}</h2>`);
            i += 1;
            continue;
        }

        const next = lines[i + 1] ? lines[i + 1].trim() : "";
        const isTableRow = line.includes("|");
        const isTableSep = /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(next);
        if (isTableRow && isTableSep) {
            closeLists();
            const parseRow = (row) => row.split("|").map((c) => c.trim()).filter((_, idx, arr) => {
                if (arr.length <= 1) return true;
                if (idx === 0 && row.trim().startsWith("|") && arr[idx] === "") return false;
                if (idx === arr.length - 1 && row.trim().endsWith("|") && arr[idx] === "") return false;
                return true;
            });

            const headers = parseRow(line);
            out.push('<table><thead><tr>');
            headers.forEach((h) => out.push(`<th>${formatInline(h)}</th>`));
            out.push('</tr></thead><tbody>');

            i += 2;
            while (i < lines.length) {
                const row = lines[i];
                if (!row.trim() || !row.includes("|")) break;
                const cells = parseRow(row);
                out.push("<tr>");
                cells.forEach((c) => out.push(`<td>${formatInline(c)}</td>`));
                out.push("</tr>");
                i += 1;
            }
            out.push("</tbody></table>");
            continue;
        }

        const ul = /^[-*]\s+(.+)$/.exec(line);
        const ulNested = /^(\s*)[-*]\s+(.+)$/.exec(line);
        if (ul || ulNested) {
            const indent = ulNested ? ulNested[1].length : 0;
            const content = ulNested ? ulNested[2] : ul[1];
            const depth = Math.floor(indent / 2) + 1;
            ensureListDepth(depth, "ul");
            out.push(`<li>${formatInline(content)}</li>`);
            i += 1;
            continue;
        }

        const ol = /^\d+\.\s+(.+)$/.exec(line);
        const olNested = /^(\s*)\d+\.\s+(.+)$/.exec(line);
        if (ol || olNested) {
            const indent = olNested ? olNested[1].length : 0;
            const content = olNested ? olNested[2] : ol[1];
            const depth = Math.floor(indent / 2) + 1;
            ensureListDepth(depth, "ol");
            out.push(`<li>${formatInline(content)}</li>`);
            i += 1;
            continue;
        }

        closeLists();
        out.push(`<p style="margin: 10px 0;">${formatInline(line)}</p>`);
        i += 1;
    }

    closeLists();
    let html = out.join("\n");
    codeBlocks.forEach((block, idx) => {
        const token = `__CODEBLOCK_${idx}__`;
        const replacement = block.lang === "mermaid"
            ? `<div class="mermaid">${escapeHtml(block.body)}</div>`
            : `<pre><code>${escapeHtml(block.body)}</code></pre>`;
        html = html.replace(token, replacement);
    });
    return html;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
