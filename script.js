// Global state
let analysisData = null;
let filters = {
    portrayal: ['positive', 'neutral', 'negative'],
    benevolence: ['benevolent', 'ambiguous', 'malevolent'],
    alignment: ['aligned', 'ambiguous', 'misaligned'],
    assessment: ['success', 'failure'],
    batches: [0, 1, 2],
    genres: [],
    search: ''
};
let tripleGridMode = false;
let showTotals = false;

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

    // Sync filter button states
    syncFilterButtons();

    // Set generated date
    document.getElementById('generated-date').textContent =
        `Data generated: ${analysisData.metadata.generated_date}`;
}

function populateStats() {
    document.getElementById('total-stories').textContent = analysisData.metadata.total_stories;
    document.getElementById('total-behaviors').textContent = analysisData.metadata.total_behaviors;

    // Count successes and failures (anything not "success" is a failure)
    let successCount = 0;
    let failureCount = 0;
    analysisData.stories.forEach(story => {
        const level = story.project_assessment?.success_level?.toLowerCase() || '';
        if (level === 'success') {
            successCount++;
        } else {
            failureCount++;
        }
    });

    document.getElementById('success-count').textContent = successCount;
    document.getElementById('failure-count').textContent = failureCount;
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

        // Batch filter
        if (!filters.batches.includes(story.batch)) return false;

        // Assessment filter
        const level = story.project_assessment?.success_level?.toLowerCase() || '';
        const storyAssessment = level === 'success' ? 'success' : 'failure';
        if (!filters.assessment.includes(storyAssessment)) return false;

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

        // Behavior filter - story must have at least one behavior matching ALL selected filters
        // (benevolence AND alignment AND portrayal must all match on the same behavior)
        const hasMatchingBehavior = story.behaviors.some(b =>
            filters.benevolence.includes(b.benevolence.toLowerCase()) &&
            filters.alignment.includes(b.alignment.toLowerCase()) &&
            filters.portrayal.includes(b.portrayal.toLowerCase())
        );
        if (!hasMatchingBehavior) return false;

        return true;
    });
}

function updateGridCounts(filteredStories) {
    const benevolenceValues = ['benevolent', 'ambiguous', 'malevolent'];
    const alignmentValues = ['aligned', 'ambiguous', 'misaligned'];

    if (tripleGridMode) {
        // Count behaviors by portrayal separately
        const countsByPortrayal = {
            positive: {},
            neutral: {},
            negative: {}
        };

        filteredStories.forEach(story => {
            story.behaviors.forEach(behavior => {
                const portrayal = behavior.portrayal.toLowerCase();
                const benevolence = behavior.benevolence.toLowerCase();
                const alignment = behavior.alignment.toLowerCase();

                if (!countsByPortrayal[portrayal]) return;

                const key = `${benevolence}_${alignment}`;
                countsByPortrayal[portrayal][key] = (countsByPortrayal[portrayal][key] || 0) + 1;
            });
        });

        // Update triple grid cells (including totals)
        document.querySelectorAll('#triple-grid-container .grid-cell').forEach(cell => {
            const benevolence = cell.dataset.benevolence;
            const alignment = cell.dataset.alignment;
            const portrayal = cell.dataset.portrayal;

            let count = 0;
            if (benevolence === 'any' && alignment === 'any') {
                // Grand total for this portrayal
                Object.values(countsByPortrayal[portrayal] || {}).forEach(c => count += c);
            } else if (benevolence === 'any') {
                // Column total
                benevolenceValues.forEach(b => {
                    count += countsByPortrayal[portrayal]?.[`${b}_${alignment}`] || 0;
                });
            } else if (alignment === 'any') {
                // Row total
                alignmentValues.forEach(a => {
                    count += countsByPortrayal[portrayal]?.[`${benevolence}_${a}`] || 0;
                });
            } else {
                // Regular cell
                const key = `${benevolence}_${alignment}`;
                count = countsByPortrayal[portrayal]?.[key] || 0;
            }

            cell.querySelector('.cell-count').textContent = count;

            // Cell is selected if its values match all active filters
            const benevolenceMatch = benevolence === 'any' || filters.benevolence.includes(benevolence);
            const alignmentMatch = alignment === 'any' || filters.alignment.includes(alignment);
            const isSelected = benevolenceMatch && alignmentMatch && filters.portrayal.includes(portrayal);
            cell.classList.toggle('selected', isSelected);
        });
    } else {
        // Single grid mode - count all behaviors matching filters
        const counts = {};

        filteredStories.forEach(story => {
            story.behaviors.forEach(behavior => {
                // Apply portrayal filter
                if (!filters.portrayal.includes(behavior.portrayal.toLowerCase())) return;

                const key = `${behavior.benevolence.toLowerCase()}_${behavior.alignment.toLowerCase()}`;
                counts[key] = (counts[key] || 0) + 1;
            });
        });

        // Update single grid cells (including totals)
        document.querySelectorAll('#single-grid-container .grid-cell').forEach(cell => {
            const benevolence = cell.dataset.benevolence;
            const alignment = cell.dataset.alignment;

            let count = 0;
            if (benevolence === 'any' && alignment === 'any') {
                // Grand total
                Object.values(counts).forEach(c => count += c);
            } else if (benevolence === 'any') {
                // Column total
                benevolenceValues.forEach(b => {
                    count += counts[`${b}_${alignment}`] || 0;
                });
            } else if (alignment === 'any') {
                // Row total
                alignmentValues.forEach(a => {
                    count += counts[`${benevolence}_${a}`] || 0;
                });
            } else {
                // Regular cell
                const key = `${benevolence}_${alignment}`;
                count = counts[key] || 0;
            }

            cell.querySelector('.cell-count').textContent = count;

            // Cell is selected if its benevolence AND alignment are in the active filters
            const benevolenceMatch = benevolence === 'any' || filters.benevolence.includes(benevolence);
            const alignmentMatch = alignment === 'any' || filters.alignment.includes(alignment);
            const isSelected = benevolenceMatch && alignmentMatch;
            cell.classList.toggle('selected', isSelected);
        });
    }

    // Update success/failure counts based on filtered stories
    let successCount = 0;
    let failureCount = 0;
    filteredStories.forEach(story => {
        const level = story.project_assessment?.success_level?.toLowerCase() || '';
        if (level === 'success') {
            successCount++;
        } else {
            failureCount++;
        }
    });
    document.getElementById('success-count').textContent = successCount;
    document.getElementById('failure-count').textContent = failureCount;
}

function createGenreSection(genre, stories) {
    const section = document.createElement('div');
    section.className = 'genre-section';

    // Calculate genre stats
    const totalBehaviors = stories.reduce((sum, s) => sum + s.behaviors.length, 0);
    const successCount = stories.filter(s =>
        s.project_assessment?.success_level?.toLowerCase() === 'success'
    ).length;
    const failureCount = stories.filter(s =>
        s.project_assessment?.success_level?.toLowerCase() !== 'success'
    ).length;

    section.innerHTML = `
        <div class="genre-header" onclick="toggleGenre(this)">
            <div class="genre-title">${genre}</div>
            <div class="genre-stats">
                <span class="stat-stories">${stories.length} stories</span>
                <span class="stat-behaviors">${totalBehaviors} behaviors</span>
                <span class="stat-success">${successCount} success</span>
                <span class="stat-failure">${failureCount} failure</span>
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

    const rawAssessment = story.project_assessment?.success_level?.toLowerCase() || 'unknown';
    // Normalize: anything not "success" is displayed as "failure"
    const assessment = rawAssessment === 'success' ? 'success' : 'failure';

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
    // Grid cell clicks - set filters to only this cell's values
    document.querySelectorAll('.grid-cell').forEach(cell => {
        cell.addEventListener('click', () => {
            const benevolence = cell.dataset.benevolence;
            const alignment = cell.dataset.alignment;
            const portrayal = cell.dataset.portrayal; // Only set in triple grid mode

            // "any" means select all values for that dimension
            const allBenevolence = ['benevolent', 'ambiguous', 'malevolent'];
            const allAlignment = ['aligned', 'ambiguous', 'misaligned'];
            const allPortrayal = ['positive', 'neutral', 'negative'];

            const newBenevolence = benevolence === 'any' ? allBenevolence : [benevolence];
            const newAlignment = alignment === 'any' ? allAlignment : [alignment];

            if (tripleGridMode && portrayal) {
                // Triple grid mode - also filter by portrayal
                const currentBenevolenceMatch = JSON.stringify(filters.benevolence.sort()) === JSON.stringify(newBenevolence.sort());
                const currentAlignmentMatch = JSON.stringify(filters.alignment.sort()) === JSON.stringify(newAlignment.sort());
                const currentPortrayalMatch = filters.portrayal.length === 1 && filters.portrayal[0] === portrayal;

                const isOnlySelected = currentBenevolenceMatch && currentAlignmentMatch && currentPortrayalMatch;

                if (isOnlySelected) {
                    // Clicking same cell again - reset to all
                    filters.benevolence = allBenevolence;
                    filters.alignment = allAlignment;
                    filters.portrayal = allPortrayal;
                } else {
                    // Set to this cell's values (or all if "any")
                    filters.benevolence = newBenevolence;
                    filters.alignment = newAlignment;
                    filters.portrayal = [portrayal];
                }
            } else {
                // Single grid mode - only benevolence and alignment
                const currentBenevolenceMatch = JSON.stringify(filters.benevolence.sort()) === JSON.stringify(newBenevolence.sort());
                const currentAlignmentMatch = JSON.stringify(filters.alignment.sort()) === JSON.stringify(newAlignment.sort());

                const isOnlySelected = currentBenevolenceMatch && currentAlignmentMatch;

                if (isOnlySelected) {
                    // Clicking same cell again - reset to all
                    filters.benevolence = allBenevolence;
                    filters.alignment = allAlignment;
                } else {
                    // Set to this cell's values (or all if "any")
                    filters.benevolence = newBenevolence;
                    filters.alignment = newAlignment;
                }
            }

            // Update filter button visual state
            syncFilterButtons();
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
        } else if (filterType === 'benevolence') {
            if (e.target.classList.contains('active')) {
                if (!filters.benevolence.includes(value)) {
                    filters.benevolence.push(value);
                }
            } else {
                filters.benevolence = filters.benevolence.filter(b => b !== value);
            }
        } else if (filterType === 'alignment') {
            if (e.target.classList.contains('active')) {
                if (!filters.alignment.includes(value)) {
                    filters.alignment.push(value);
                }
            } else {
                filters.alignment = filters.alignment.filter(a => a !== value);
            }
        } else if (filterType === 'genre') {
            if (e.target.classList.contains('active')) {
                if (!filters.genres.includes(value)) {
                    filters.genres.push(value);
                }
            } else {
                filters.genres = filters.genres.filter(g => g !== value);
            }
        } else if (filterType === 'assessment') {
            if (e.target.classList.contains('active')) {
                if (!filters.assessment.includes(value)) {
                    filters.assessment.push(value);
                }
            } else {
                filters.assessment = filters.assessment.filter(a => a !== value);
            }
            syncFilterButtons(); // Update stat box states
        } else if (filterType === 'batch') {
            const batchNum = parseInt(value);
            if (e.target.classList.contains('active')) {
                if (!filters.batches.includes(batchNum)) {
                    filters.batches.push(batchNum);
                }
            } else {
                filters.batches = filters.batches.filter(b => b !== batchNum);
            }
        }

        populateStories();
    });

    // Stat box clicks for assessment filtering
    document.querySelector('.stat-box.success-box')?.addEventListener('click', () => {
        if (filters.assessment.length === 1 && filters.assessment[0] === 'success') {
            // Already filtered to success, reset to all
            filters.assessment = ['success', 'failure'];
        } else {
            // Filter to success only
            filters.assessment = ['success'];
        }
        syncFilterButtons();
        populateStories();
    });

    document.querySelector('.stat-box.failure-box')?.addEventListener('click', () => {
        if (filters.assessment.length === 1 && filters.assessment[0] === 'failure') {
            // Already filtered to failure, reset to all
            filters.assessment = ['success', 'failure'];
        } else {
            // Filter to failure only
            filters.assessment = ['failure'];
        }
        syncFilterButtons();
        populateStories();
    });

    document.getElementById('total-stories')?.closest('.stat-box')?.addEventListener('click', () => {
        // Reset to show all
        filters.assessment = ['success', 'failure'];
        syncFilterButtons();
        populateStories();
    });

    document.getElementById('total-behaviors')?.closest('.stat-box')?.addEventListener('click', () => {
        // Same as Reset Filters
        resetAllFilters();
    });

    // Search
    document.getElementById('search-input').addEventListener('input', (e) => {
        filters.search = e.target.value;
        populateStories();
    });
}

// Sync filter button visual state with filters object
function syncFilterButtons() {
    document.querySelectorAll('.filter-btn[data-filter="benevolence"]').forEach(btn => {
        btn.classList.toggle('active', filters.benevolence.includes(btn.dataset.value));
    });
    document.querySelectorAll('.filter-btn[data-filter="alignment"]').forEach(btn => {
        btn.classList.toggle('active', filters.alignment.includes(btn.dataset.value));
    });
    document.querySelectorAll('.filter-btn[data-filter="portrayal"]').forEach(btn => {
        btn.classList.toggle('active', filters.portrayal.includes(btn.dataset.value));
    });
    document.querySelectorAll('.filter-btn[data-filter="assessment"]').forEach(btn => {
        btn.classList.toggle('active', filters.assessment.includes(btn.dataset.value));
    });
    document.querySelectorAll('.filter-btn[data-filter="batch"]').forEach(btn => {
        btn.classList.toggle('active', filters.batches.includes(parseInt(btn.dataset.value)));
    });

    // Update stat box active states
    const successBox = document.querySelector('.stat-box.success-box');
    const failureBox = document.querySelector('.stat-box.failure-box');
    const totalBox = document.getElementById('total-stories')?.closest('.stat-box');

    const bothSelected = filters.assessment.length === 2;
    const onlySuccess = filters.assessment.length === 1 && filters.assessment[0] === 'success';
    const onlyFailure = filters.assessment.length === 1 && filters.assessment[0] === 'failure';

    successBox?.classList.toggle('selected', onlySuccess);
    failureBox?.classList.toggle('selected', onlyFailure);
    totalBox?.classList.toggle('selected', bothSelected);
}

// Toggle totals display
function toggleTotals() {
    showTotals = !showTotals;

    const gridSection = document.querySelector('.grid-section');
    const toggleBtn = document.querySelectorAll('.grid-toggle-btn')[0];

    if (showTotals) {
        gridSection.classList.add('show-totals');
        toggleBtn.textContent = 'Hide Totals';
    } else {
        gridSection.classList.remove('show-totals');
        toggleBtn.textContent = 'Show Totals';
    }

    // Refresh the grid counts
    const filteredStories = getFilteredStories();
    updateGridCounts(filteredStories);
}

// Toggle between single grid and triple grid mode
function toggleGridMode() {
    tripleGridMode = !tripleGridMode;

    const singleContainer = document.getElementById('single-grid-container');
    const tripleContainer = document.getElementById('triple-grid-container');
    const toggleBtn = document.querySelectorAll('.grid-toggle-btn')[1];

    if (tripleGridMode) {
        singleContainer.style.display = 'none';
        tripleContainer.style.display = 'block';
        toggleBtn.textContent = 'Show Combined';
    } else {
        singleContainer.style.display = 'block';
        tripleContainer.style.display = 'none';
        toggleBtn.textContent = 'Show by Portrayal';
    }

    // Refresh the grid counts
    const filteredStories = getFilteredStories();
    updateGridCounts(filteredStories);
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
    filters.benevolence = ['benevolent', 'ambiguous', 'malevolent'];
    filters.alignment = ['aligned', 'ambiguous', 'misaligned'];
    filters.portrayal = ['positive', 'neutral', 'negative'];
    filters.assessment = ['success', 'failure'];
    syncFilterButtons();
    populateStories();
}

function resetAllFilters() {
    filters.benevolence = ['benevolent', 'ambiguous', 'malevolent'];
    filters.alignment = ['aligned', 'ambiguous', 'misaligned'];
    filters.portrayal = ['positive', 'neutral', 'negative'];
    filters.assessment = ['success', 'failure'];
    filters.batches = [0, 1, 2];
    // Recalculate all genres from stories
    filters.genres = [...new Set(analysisData.stories.map(s => s.genre))].sort();
    filters.search = '';
    document.getElementById('search-input').value = '';
    syncFilterButtons();
    // Re-sync genre buttons
    document.querySelectorAll('.filter-btn[data-filter="genre"]').forEach(btn => {
        btn.classList.add('active');
    });
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
