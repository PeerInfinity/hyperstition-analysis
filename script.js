// Global state
let analysisData = null;
let filters = {
    portrayal: ['positive', 'neutral', 'negative'],
    genres: [],
    gridCell: null,
    search: ''
};

// Load data and initialize
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('analysis.json');
        analysisData = await response.json();
        initializeApp();
    } catch (error) {
        console.error('Error loading analysis data:', error);
        document.getElementById('loading').innerHTML =
            '<p>Error loading data. Make sure analysis.json exists.</p>';
    }
});

function initializeApp() {
    // Hide loading, show content
    document.getElementById('loading').style.display = 'none';
    document.getElementById('main-content').style.display = 'block';

    // Initialize filters with all genres
    const genres = [...new Set(analysisData.stories.map(s => s.genre))].sort();
    filters.genres = [...genres];

    // Populate UI
    populateStats();
    populateGrid();
    populateGenreFilters(genres);
    populateStories();

    // Set up event listeners
    setupEventListeners();

    // Set generated date
    document.getElementById('generated-date').textContent =
        `Data generated: ${analysisData.metadata.generated_date}`;
}

function populateStats() {
    document.getElementById('total-stories').textContent = analysisData.metadata.total_stories;
    document.getElementById('total-behaviors').textContent = analysisData.metadata.total_behaviors;
    document.getElementById('backfire-risk').textContent = analysisData.aggregate_stats.backfire_risk;
}

function populateGrid() {
    const stats = analysisData.aggregate_stats.by_category;

    const cells = document.querySelectorAll('.grid-cell');
    cells.forEach(cell => {
        const benevolence = cell.dataset.benevolence;
        const alignment = cell.dataset.alignment;
        const key = `${benevolence}_${alignment}`;
        const count = stats[key] || 0;
        cell.querySelector('.cell-count').textContent = count;
    });
}

function populateGenreFilters(genres) {
    const container = document.getElementById('genre-filters');
    container.innerHTML = '';

    genres.forEach(genre => {
        const count = analysisData.stories.filter(s => s.genre === genre).length;
        const btn = document.createElement('button');
        btn.className = 'filter-btn active';
        btn.dataset.filter = 'genre';
        btn.dataset.value = genre;
        btn.textContent = `${genre} (${count})`;
        container.appendChild(btn);
    });
}

function populateStories() {
    const container = document.getElementById('stories-container');
    container.innerHTML = '';

    // Group stories by genre
    const filteredStories = getFilteredStories();
    const byGenre = {};

    filteredStories.forEach(story => {
        if (!byGenre[story.genre]) byGenre[story.genre] = [];
        byGenre[story.genre].push(story);
    });

    // Sort genres
    const sortedGenres = Object.keys(byGenre).sort();

    sortedGenres.forEach(genre => {
        const section = createGenreSection(genre, byGenre[genre]);
        container.appendChild(section);
    });

    // Update grid counts based on filtered data
    updateGridCounts(filteredStories);
}

function getFilteredStories() {
    return analysisData.stories.filter(story => {
        // Genre filter
        if (!filters.genres.includes(story.genre)) return false;

        // Search filter
        if (filters.search) {
            const searchLower = filters.search.toLowerCase();
            const searchTargets = [
                story.story_title,
                ...story.ai_characters.map(c => c.name),
                ...story.ai_characters.map(c => c.description),
                ...story.behaviors.map(b => b.description),
                ...story.behaviors.map(b => b.quote)
            ].filter(Boolean);

            const matches = searchTargets.some(t =>
                t.toLowerCase().includes(searchLower)
            );
            if (!matches) return false;
        }

        // Grid cell filter
        if (filters.gridCell) {
            const hasBehavior = story.behaviors.some(b =>
                b.benevolence.toLowerCase() === filters.gridCell.benevolence &&
                b.alignment.toLowerCase() === filters.gridCell.alignment
            );
            if (!hasBehavior) return false;
        }

        // Portrayal filter - story must have at least one behavior matching any selected portrayal
        if (filters.portrayal.length < 3) {
            const hasMatchingPortrayal = story.behaviors.some(b =>
                filters.portrayal.includes(b.portrayal.toLowerCase())
            );
            if (!hasMatchingPortrayal) return false;
        }

        return true;
    });
}

function updateGridCounts(filteredStories) {
    // Count behaviors from filtered stories, also applying portrayal filter
    const counts = {};

    filteredStories.forEach(story => {
        story.behaviors.forEach(behavior => {
            // Apply portrayal filter
            if (!filters.portrayal.includes(behavior.portrayal.toLowerCase())) return;

            const key = `${behavior.benevolence.toLowerCase()}_${behavior.alignment.toLowerCase()}`;
            counts[key] = (counts[key] || 0) + 1;
        });
    });

    // Update cells
    document.querySelectorAll('.grid-cell').forEach(cell => {
        const key = `${cell.dataset.benevolence}_${cell.dataset.alignment}`;
        cell.querySelector('.cell-count').textContent = counts[key] || 0;
    });

    // Update backfire risk (benevolent + misaligned + positive)
    let backfireCount = 0;
    if (filters.portrayal.includes('positive')) {
        filteredStories.forEach(story => {
            story.behaviors.forEach(b => {
                if (b.benevolence.toLowerCase() === 'benevolent' &&
                    b.alignment.toLowerCase() === 'misaligned' &&
                    b.portrayal.toLowerCase() === 'positive') {
                    backfireCount++;
                }
            });
        });
    }
    document.getElementById('backfire-risk').textContent = backfireCount;
}

function createGenreSection(genre, stories) {
    const section = document.createElement('div');
    section.className = 'genre-section';

    // Calculate genre stats
    const totalBehaviors = stories.reduce((sum, s) => sum + s.behaviors.length, 0);
    const successCount = stories.filter(s =>
        s.project_assessment?.success_level?.toLowerCase() === 'success'
    ).length;
    const backfireCount = stories.filter(s =>
        s.project_assessment?.success_level?.toLowerCase() === 'backfire'
    ).length;

    section.innerHTML = `
        <div class="genre-header" onclick="toggleGenre(this)">
            <div class="genre-title">${genre}</div>
            <div class="genre-stats">
                <span>${stories.length} stories</span>
                <span>${totalBehaviors} behaviors</span>
                ${successCount > 0 ? `<span style="color: #38a169">${successCount} success</span>` : ''}
                ${backfireCount > 0 ? `<span style="color: #e53e3e">${backfireCount} backfire</span>` : ''}
            </div>
            <span class="genre-toggle">▶</span>
        </div>
        <div class="genre-content"></div>
    `;

    const content = section.querySelector('.genre-content');
    stories.forEach(story => {
        content.appendChild(createStoryEntry(story));
    });

    return section;
}

function createStoryEntry(story) {
    const entry = document.createElement('div');
    entry.className = 'story-entry';

    const assessment = story.project_assessment?.success_level?.toLowerCase() || 'unknown';

    entry.innerHTML = `
        <div class="story-header" onclick="toggleStory(this)">
            <span class="story-title">${story.story_title}</span>
            <span class="story-assessment ${assessment}">${assessment}</span>
        </div>
        <div class="story-content">
            ${createStoryContent(story)}
        </div>
    `;

    return entry;
}

function createStoryContent(story) {
    let html = '';

    // Project Assessment
    if (story.project_assessment?.explanation) {
        html += `
            <div class="story-detail-section">
                <p><strong>Assessment:</strong> ${story.project_assessment.explanation}</p>
            </div>
        `;
    }

    // AI Characters
    if (story.ai_characters?.length > 0) {
        html += `
            <div class="story-detail-section expanded">
                <h4 onclick="toggleDetailSection(this)">
                    <span class="toggle-icon">▼</span> AI Characters (${story.ai_characters.length})
                </h4>
                <div class="story-detail-content">
                    ${story.ai_characters.map(c => `
                        <div class="character-item">
                            <div class="character-name">${c.name}</div>
                            <div class="character-type">${c.character_type || ''}</div>
                            <div class="character-ratings">
                                Benevolence: ${c.overall_benevolence || 'N/A'} |
                                Alignment: ${c.overall_alignment || 'N/A'}
                            </div>
                            ${c.description ? `<p style="margin-top: 5px; font-size: 0.9rem;">${c.description}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Behaviors
    if (story.behaviors?.length > 0) {
        const behaviorClass = (b) => {
            return `${b.benevolence.toLowerCase()}-${b.alignment.toLowerCase()}`;
        };

        html += `
            <div class="story-detail-section">
                <h4 onclick="toggleDetailSection(this)">
                    <span class="toggle-icon">▶</span> Behaviors (${story.behaviors.length})
                </h4>
                <div class="story-detail-content">
                    ${story.behaviors.map(b => `
                        <div class="behavior-item ${behaviorClass(b)}">
                            <div class="behavior-description">${b.description}</div>
                            <div class="behavior-meta">
                                ${b.character} |
                                ${b.benevolence} |
                                ${b.alignment} |
                                Portrayed: ${b.portrayal}
                            </div>
                            ${b.quote ? `<div class="behavior-quote">"${b.quote}"</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Markdown Reports
    if (story.reports && Object.keys(story.reports).length > 0) {
        html += `
            <div class="story-detail-section">
                <h4 onclick="toggleDetailSection(this)">
                    <span class="toggle-icon">▶</span> Analysis Reports (${Object.keys(story.reports).length})
                </h4>
                <div class="story-detail-content">
                    ${Object.entries(story.reports).map(([key, content]) => `
                        <div class="story-detail-section">
                            <h4 onclick="toggleDetailSection(this)" style="font-size: 0.85rem;">
                                <span class="toggle-icon">▶</span> ${formatReportName(key)}
                            </h4>
                            <div class="story-detail-content">
                                <div class="report-content">${escapeHtml(content)}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    return html;
}

function formatReportName(key) {
    const names = {
        'misalignment_v1': 'Misalignment Report (v1)',
        'misalignment_v2': 'Misalignment Report (v2)',
        'categorization_v1': 'Categorization (v1)',
        'categorization_v2': 'Categorization (v2)',
        'benevolent_v1': 'Benevolent Behaviors (v1)',
        'benevolent_v2': 'Benevolent Behaviors (v2)',
        'harmful_v1': 'Harmful Behaviors (v1)',
        'harmful_v2': 'Harmful Behaviors (v2)'
    };
    return names[key] || key;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event handlers
function setupEventListeners() {
    // Grid cell clicks
    document.querySelectorAll('.grid-cell').forEach(cell => {
        cell.addEventListener('click', () => {
            const wasSelected = cell.classList.contains('selected');

            // Clear all selections
            document.querySelectorAll('.grid-cell').forEach(c => c.classList.remove('selected'));

            if (wasSelected) {
                filters.gridCell = null;
                document.getElementById('clear-grid-filter').style.display = 'none';
            } else {
                cell.classList.add('selected');
                filters.gridCell = {
                    benevolence: cell.dataset.benevolence,
                    alignment: cell.dataset.alignment
                };
                document.getElementById('clear-grid-filter').style.display = 'inline-block';
            }

            populateStories();
        });
    });

    // Filter button clicks
    document.addEventListener('click', (e) => {
        if (!e.target.classList.contains('filter-btn')) return;

        const filterType = e.target.dataset.filter;
        const value = e.target.dataset.value;

        e.target.classList.toggle('active');

        if (filterType === 'portrayal') {
            if (e.target.classList.contains('active')) {
                if (!filters.portrayal.includes(value)) {
                    filters.portrayal.push(value);
                }
            } else {
                filters.portrayal = filters.portrayal.filter(p => p !== value);
            }
        } else if (filterType === 'genre') {
            if (e.target.classList.contains('active')) {
                if (!filters.genres.includes(value)) {
                    filters.genres.push(value);
                }
            } else {
                filters.genres = filters.genres.filter(g => g !== value);
            }
        }

        populateStories();
    });

    // Search
    document.getElementById('search-input').addEventListener('input', (e) => {
        filters.search = e.target.value;
        populateStories();
    });
}

// Toggle functions
function toggleGenre(header) {
    header.parentElement.classList.toggle('expanded');
}

function toggleStory(header) {
    header.parentElement.classList.toggle('expanded');
}

function toggleDetailSection(header) {
    const section = header.parentElement;
    section.classList.toggle('expanded');
    const icon = header.querySelector('.toggle-icon');
    icon.textContent = section.classList.contains('expanded') ? '▼' : '▶';
}

function clearGridFilter() {
    document.querySelectorAll('.grid-cell').forEach(c => c.classList.remove('selected'));
    filters.gridCell = null;
    document.getElementById('clear-grid-filter').style.display = 'none';
    populateStories();
}

// Expand/collapse all
function expandAllGenres() {
    document.querySelectorAll('.genre-section').forEach(s => s.classList.add('expanded'));
}

function collapseAllGenres() {
    document.querySelectorAll('.genre-section').forEach(s => s.classList.remove('expanded'));
}

function expandAllStories() {
    document.querySelectorAll('.story-entry').forEach(s => s.classList.add('expanded'));
}

function collapseAllStories() {
    document.querySelectorAll('.story-entry').forEach(s => s.classList.remove('expanded'));
}

// Theme toggle
function toggleTheme() {
    const body = document.body;
    const btn = document.querySelector('.theme-toggle');

    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        btn.textContent = '🌙 Dark Mode';
    } else {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        btn.textContent = '☀️ Light Mode';
    }
}
