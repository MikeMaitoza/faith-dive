// Faith Dive App JavaScript

const API_BASE = '/api/v1';
let bibleVersions = [];
let deferredPrompt;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadBibleVersions();
    registerServiceWorker();
    setupInstallPrompt();
});

// PWA Install functionality
function setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        showInstallPrompt();
    });

    document.getElementById('installButton').addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to install prompt: ${outcome}`);
            deferredPrompt = null;
            hideInstallPrompt();
        }
    });
}

function showInstallPrompt() {
    document.getElementById('installPrompt').classList.remove('hidden');
}

function hideInstallPrompt() {
    document.getElementById('installPrompt').classList.add('hidden');
}

// Service Worker Registration
async function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register('/sw.js');
            console.log('SW registered: ', registration);
        } catch (registrationError) {
            console.log('SW registration failed: ', registrationError);
        }
    }
}

// Navigation
function showSection(section) {
    // Hide all sections
    document.getElementById('searchSection').classList.add('hidden');
    document.getElementById('journalSection').classList.add('hidden');
    document.getElementById('favoritesSection').classList.add('hidden');
    
    // Show selected section
    document.getElementById(section + 'Section').classList.remove('hidden');
    
    // Load data for the section
    if (section === 'journal') {
        loadJournalEntries();
    } else if (section === 'favorites') {
        loadFavorites();
    }
}

// Bible API Functions
async function loadBibleVersions() {
    try {
        const response = await fetch(`${API_BASE}/bibles`);
        bibleVersions = await response.json();
        
        const select = document.getElementById('bibleVersion');
        select.innerHTML = '<option value="">Select a Bible version...</option>';
        
        bibleVersions.forEach(bible => {
            const option = document.createElement('option');
            option.value = bible.id;
            option.textContent = `${bible.name} (${bible.abbreviation})`;
            select.appendChild(option);
        });
        
        // Select first version by default
        if (bibleVersions.length > 0) {
            select.value = bibleVersions[0].id;
        }
    } catch (error) {
        console.error('Error loading Bible versions:', error);
        showNotification('Error loading Bible versions', 'error');
    }
}

async function searchVerses() {
    const query = document.getElementById('searchQuery').value.trim();
    if (!query) {
        showNotification('Please enter a search term', 'warning');
        return;
    }
    
    const bibleId = document.getElementById('bibleVersion').value;
    const loading = document.getElementById('searchLoading');
    const results = document.getElementById('searchResults');
    
    loading.style.display = 'block';
    results.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                bible_id: bibleId || null,
                limit: 10
            })
        });
        
        const searchResults = await response.json();
        displaySearchResults(searchResults);
        
    } catch (error) {
        console.error('Error searching verses:', error);
        showNotification('Error searching verses', 'error');
    } finally {
        loading.style.display = 'none';
    }
}

function displaySearchResults(results) {
    const container = document.getElementById('searchResults');
    
    if (results.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No verses found. Try different search terms.</div>';
        return;
    }
    
    container.innerHTML = results.map(result => `
        <div class="verse-card">
            <div class="verse-reference">${result.verse.reference}</div>
            <div class="verse-text">${result.verse.content}</div>
            <div class="d-flex gap-2">
                <button class="btn btn-sm btn-primary" 
                        onclick="openJournalModal('${result.verse.reference}', '${escapeHtml(result.verse.content)}', '${result.bible_name}', '${result.bible_id}')">
                    Journal
                </button>
                <button class="btn btn-sm btn-outline-primary" 
                        onclick="addToFavorites('${result.verse.reference}', '${escapeHtml(result.verse.content)}', '${result.bible_name}', '${result.bible_id}')">
                    ♥ Favorite
                </button>
            </div>
        </div>
    `).join('');
}

// Journal Functions
function openJournalModal(reference, text, bibleVersion, bibleId) {
    document.getElementById('journalVerseRef').value = reference;
    document.getElementById('journalVerseText').value = text;
    document.getElementById('journalBibleVersion').value = bibleVersion;
    document.getElementById('journalBibleId').value = bibleId;
    
    document.getElementById('modalVerseReference').textContent = reference;
    document.getElementById('modalVerseText').textContent = text;
    
    // Clear form
    document.getElementById('journalTitle').value = '';
    document.getElementById('journalContent').value = '';
    document.getElementById('journalTags').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('journalModal'));
    modal.show();
}

async function saveJournalEntry() {
    const entryData = {
        verse_reference: document.getElementById('journalVerseRef').value,
        verse_text: document.getElementById('journalVerseText').value,
        bible_version: document.getElementById('journalBibleVersion').value,
        bible_id: document.getElementById('journalBibleId').value,
        title: document.getElementById('journalTitle').value,
        content: document.getElementById('journalContent').value,
        tags: document.getElementById('journalTags').value.split(',').map(tag => tag.trim()).filter(tag => tag)
    };
    
    if (!entryData.content) {
        showNotification('Please enter your thoughts', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/journal`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(entryData)
        });
        
        if (response.ok) {
            showNotification('Journal entry saved successfully!', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('journalModal'));
            modal.hide();
        } else {
            throw new Error('Failed to save journal entry');
        }
    } catch (error) {
        console.error('Error saving journal entry:', error);
        showNotification('Error saving journal entry', 'error');
    }
}

async function loadJournalEntries() {
    try {
        const response = await fetch(`${API_BASE}/journal`);
        const entries = await response.json();
        displayJournalEntries(entries);
    } catch (error) {
        console.error('Error loading journal entries:', error);
        showNotification('Error loading journal entries', 'error');
    }
}

function displayJournalEntries(entries) {
    const container = document.getElementById('journalEntries');
    
    if (entries.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No journal entries yet. Start by searching for verses and adding your thoughts!</div>';
        return;
    }
    
    container.innerHTML = entries.map(entry => `
        <div class="journal-entry-card">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                    <h5 class="mb-1">${entry.title || 'Untitled'}</h5>
                    <small class="text-muted">${new Date(entry.created_at).toLocaleDateString()}</small>
                </div>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteJournalEntry(${entry.id})">×</button>
            </div>
            <div class="verse-reference mb-1">${entry.verse_reference}</div>
            <div class="verse-text mb-2">${entry.verse_text}</div>
            <div class="mb-2">${entry.content}</div>
            ${entry.tags.length > 0 ? `<div class="tags">${entry.tags.map(tag => `<span class="badge bg-secondary me-1">${tag}</span>`).join('')}</div>` : ''}
        </div>
    `).join('');
}

async function deleteJournalEntry(entryId) {
    if (!confirm('Are you sure you want to delete this journal entry?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/journal/${entryId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Journal entry deleted', 'success');
            loadJournalEntries();
        } else {
            throw new Error('Failed to delete journal entry');
        }
    } catch (error) {
        console.error('Error deleting journal entry:', error);
        showNotification('Error deleting journal entry', 'error');
    }
}

// Favorites Functions
async function addToFavorites(reference, text, bibleVersion, bibleId) {
    try {
        const response = await fetch(`${API_BASE}/favorites`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                verse_reference: reference,
                verse_text: text,
                bible_version: bibleVersion,
                bible_id: bibleId
            })
        });
        
        if (response.ok) {
            showNotification('Added to favorites!', 'success');
        } else {
            throw new Error('Failed to add to favorites');
        }
    } catch (error) {
        console.error('Error adding to favorites:', error);
        showNotification('Error adding to favorites', 'error');
    }
}

async function loadFavorites() {
    try {
        const response = await fetch(`${API_BASE}/favorites`);
        const favorites = await response.json();
        displayFavorites(favorites);
    } catch (error) {
        console.error('Error loading favorites:', error);
        showNotification('Error loading favorites', 'error');
    }
}

function displayFavorites(favorites) {
    const container = document.getElementById('favoritesList');
    
    if (favorites.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No favorite verses yet. Add some verses to your favorites!</div>';
        return;
    }
    
    container.innerHTML = favorites.map(fav => `
        <div class="verse-card">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <div class="verse-reference">${fav.verse_reference}</div>
                    <div class="verse-text">${fav.verse_text}</div>
                    <small class="text-muted">Added: ${new Date(fav.created_at).toLocaleDateString()}</small>
                </div>
                <button class="btn btn-sm btn-outline-danger" onclick="removeFavorite(${fav.id})">×</button>
            </div>
        </div>
    `).join('');
}

async function removeFavorite(favoriteId) {
    try {
        const response = await fetch(`${API_BASE}/favorites/${favoriteId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Removed from favorites', 'success');
            loadFavorites();
        } else {
            throw new Error('Failed to remove from favorites');
        }
    } catch (error) {
        console.error('Error removing favorite:', error);
        showNotification('Error removing favorite', 'error');
    }
}

// Utility Functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}