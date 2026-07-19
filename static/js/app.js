// AgriCare Frontend Controller (SPA Client)

const state = {
    user: null, // { id, email, role } or null
    view: 'catalog', // catalog, crop-detail, messages, admin
    crops: [],
    currentCropId: null,
    activeChatUserId: null,
    pollingInterval: null,
    unreadMessages: 0
};

// --- DOM ELEMENTS ---
const sections = {
    hero: document.getElementById('hero-section'),
    catalog: document.getElementById('view-catalog'),
    cropDetail: document.getElementById('view-crop-detail'),
    messages: document.getElementById('view-messages'),
    admin: document.getElementById('view-admin')
};

const navLinks = {
    catalog: document.getElementById('nav-catalog'),
    messages: document.getElementById('nav-messages'),
    admin: document.getElementById('nav-admin'),
    logo: document.getElementById('nav-logo')
};

// Toast notification helper
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type === 'error' ? 'error' : ''}`;
    toast.innerHTML = `
        <i class="fa-solid ${type === 'error' ? 'fa-circle-exmark' : 'fa-circle-check'}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    
    // Auto-remove toast after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'toastFadeOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Check session status on app start
async function checkAuth() {
    try {
        const res = await fetch('/api/auth/status');
        const data = await res.json();
        if (data.authenticated) {
            state.user = data.user;
            updateAuthHeader();
            enableProtectedNavigation();
            startMessagePolling();
        } else {
            state.user = null;
            updateAuthHeader();
            disableProtectedNavigation();
            stopMessagePolling();
        }
    } catch (err) {
        console.error("Error checking auth status:", err);
    }
}

// Update authentication header UI
function updateAuthHeader() {
    const container = document.getElementById('header-auth-section');
    if (state.user) {
        container.innerHTML = `
            <div class="user-profile-widget">
                <i class="fa-solid fa-circle-user"></i>
                <span class="user-email">${state.user.email}</span>
                <button class="btn btn-secondary btn-sm" id="btn-logout"><i class="fa-solid fa-sign-out-alt"></i> Logout</button>
            </div>
        `;
        document.getElementById('btn-logout').addEventListener('click', handleLogout);
        
        // Show/hide comment input area
        document.getElementById('comment-input-area')?.classList.remove('hidden');
        document.getElementById('comment-auth-prompt')?.classList.add('hidden');
    } else {
        container.innerHTML = `
            <button class="auth-btn btn-primary" id="btn-show-login"><i class="fa-solid fa-sign-in-alt"></i> Login</button>
        `;
        document.getElementById('btn-show-login').addEventListener('click', () => toggleAuthModal(true));
        
        // Show/hide comment input area
        document.getElementById('comment-input-area')?.classList.add('hidden');
        document.getElementById('comment-auth-prompt')?.classList.remove('hidden');
        
        // If logged out from messages or admin view, route back to catalog
        if (state.view === 'messages' || state.view === 'admin') {
            switchView('catalog');
        }
    }
}

function enableProtectedNavigation() {
    navLinks.messages.classList.remove('hidden');
    if (state.user && state.user.role === 'admin') {
        navLinks.admin.classList.remove('hidden');
    } else {
        navLinks.admin.classList.add('hidden');
    }
}

function disableProtectedNavigation() {
    navLinks.messages.classList.add('hidden');
    navLinks.admin.classList.add('hidden');
}

// Router View Switcher
function switchView(targetView) {
    state.view = targetView;
    
    // Hide all views
    Object.values(sections).forEach(sec => sec.classList.add('hidden'));
    
    // Deactivate all navigation links
    Object.values(navLinks).forEach(link => link.classList.remove('active'));
    
    // Show/activate target
    if (targetView === 'catalog') {
        sections.hero.classList.remove('hidden');
        sections.catalog.classList.remove('hidden');
        navLinks.catalog.classList.add('active');
        fetchCrops();
    } else if (targetView === 'crop-detail') {
        sections.cropDetail.classList.remove('hidden');
    } else if (targetView === 'messages') {
        if (!state.user) {
            switchView('catalog');
            return;
        }
        sections.messages.classList.remove('hidden');
        navLinks.messages.classList.add('active');
        loadMessagesDashboard();
    } else if (targetView === 'admin') {
        if (!state.user || state.user.role !== 'admin') {
            switchView('catalog');
            return;
        }
        sections.admin.classList.remove('hidden');
        navLinks.admin.classList.add('active');
        loadAdminDashboard();
    }
    
    // Scroll window back to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// --- CROPS & CATALOG ENGINE ---

async function fetchCrops() {
    try {
        const res = await fetch('/api/crops');
        const data = await res.json();
        if (Array.isArray(data)) {
            state.crops = data;
            renderCrops(state.crops);
        }
    } catch (err) {
        console.error("Error fetching crops:", err);
        showToast("Failed to load crops list.", "error");
    }
}

function renderCrops(cropsList) {
    const container = document.getElementById('crops-grid-container');
    container.innerHTML = '';
    
    if (cropsList.length === 0) {
        container.innerHTML = `
            <div class="empty-results card w-100 text-center">
                <i class="fa-solid fa-face-frown" style="font-size: 32px; color: var(--text-muted); margin-bottom: 12px;"></i>
                <p>No crops match your search criteria. Try different keywords.</p>
            </div>
        `;
        return;
    }
    
    cropsList.forEach(crop => {
        const card = document.createElement('div');
        card.className = 'crop-card';
        card.innerHTML = `
            <div class="crop-card-img" style="background-image: url('${crop.primary_image || '/static/images/default.jpg'}')"></div>
            <div class="crop-card-body">
                <h3>${crop.common_name}</h3>
                <span class="sc-name">${crop.scientific_name}</span>
                <p class="benefit-preview">${crop.medicinal_benefit || 'Authoritative crop health profile.'}</p>
                <div class="crop-card-footer">
                    <span><i class="fa-solid fa-shield-halved"></i> Verified Profile</span>
                    <span>Details <i class="fa-solid fa-arrow-right"></i></span>
                </div>
            </div>
        `;
        card.addEventListener('click', () => showCropDetail(crop.id));
        container.appendChild(card);
    });
}

// Live Global Search Filter
document.getElementById('global-search-input').addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase().trim();
    
    // Wait, let's also query the server or search our client-side cache
    // Let's filter the crops based on query matching common_name, scientific_name, or diseases
    // If the crop details are cached, we can search disease names too.
    // For now, we can search:
    const filtered = state.crops.filter(crop => {
        const matchCommon = crop.common_name.toLowerCase().includes(query);
        const matchScientific = crop.scientific_name.toLowerCase().includes(query);
        const matchBenefit = crop.medicinal_benefit ? crop.medicinal_benefit.toLowerCase().includes(query) : false;
        return matchCommon || matchScientific || matchBenefit;
    });
    
    renderCrops(filtered);
});

// --- CROP DETAILS & ACCORDION ---

async function showCropDetail(cropId) {
    state.currentCropId = cropId;
    switchView('crop-detail');
    
    try {
        const res = await fetch(`/api/crops/${cropId}`);
        const crop = await res.json();
        
        if (crop.error) {
            showToast(crop.error, "error");
            switchView('catalog');
            return;
        }
        
        // Render texts
        document.getElementById('detail-common-name').textContent = crop.common_name;
        document.getElementById('detail-scientific-name').textContent = crop.scientific_name;
        document.getElementById('detail-medicinal-benefits').textContent = crop.medicinal_benefit || 'No medicinal benefits listed.';
        
        // Render images side by side
        const healthyGallery = document.getElementById('healthy-gallery');
        const infectedGallery = document.getElementById('infected-gallery');
        healthyGallery.innerHTML = '';
        infectedGallery.innerHTML = '';
        
        const healthyImages = crop.images.filter(img => img.type === 'healthy');
        const infectedImages = crop.images.filter(img => img.type === 'infected');
        
        if (healthyImages.length === 0) {
            healthyGallery.innerHTML = `<p class="subtitle">No healthy images uploaded.</p>`;
        } else {
            healthyImages.forEach(img => {
                healthyGallery.appendChild(createImageThumbnail(img, cropId));
            });
        }
        
        if (infectedImages.length === 0) {
            infectedGallery.innerHTML = `<p class="subtitle">No infected images uploaded.</p>`;
        } else {
            infectedImages.forEach(img => {
                infectedGallery.appendChild(createImageThumbnail(img, cropId));
            });
        }
        
        // Render diseases accordion
        const accordion = document.getElementById('disease-accordion');
        accordion.innerHTML = '';
        
        if (crop.diseases.length === 0) {
            accordion.innerHTML = `
                <div class="empty-accordion card text-center">
                    <p><i class="fa-solid fa-face-smile" style="color: var(--healthy-color);"></i> No recorded diseases for this crop.</p>
                </div>
            `;
        } else {
            crop.diseases.forEach((dis, idx) => {
                const item = document.createElement('div');
                item.className = 'accordion-item';
                item.innerHTML = `
                    <button class="accordion-header">
                        <span>
                            ${dis.disease_name}
                            <span class="disease-badge ${dis.is_treatable ? 'badge-treatable' : 'badge-untreatable'}">
                                ${dis.is_treatable ? 'Treatable' : 'No Cure / Severe'}
                            </span>
                        </span>
                        <i class="fa-solid fa-chevron-down accordion-icon"></i>
                    </button>
                    <div class="accordion-content">
                        <div class="accordion-content-inner">
                            <h5>Description & Symptoms:</h5>
                            <p>${dis.description}</p>
                            <h5>Recommended Action & Treatment Plan:</h5>
                            <div class="treatment-plan-box">
                                <p>${dis.treatment}</p>
                            </div>
                        </div>
                    </div>
                `;
                
                // Expand collapse animation listener
                const header = item.querySelector('.accordion-header');
                header.addEventListener('click', () => {
                    // Close others
                    accordion.querySelectorAll('.accordion-item').forEach(otherItem => {
                        if (otherItem !== item) otherItem.classList.remove('active');
                    });
                    // Toggle this one
                    item.classList.toggle('active');
                });
                
                accordion.appendChild(item);
            });
        }
        
        // Render comments
        renderComments(crop.comments);
        
    } catch (err) {
        console.error("Error showing crop detail:", err);
        showToast("Error loading crop profiles.", "error");
    }
}

function createImageThumbnail(img, cropId) {
    const wrapper = document.createElement('div');
    wrapper.className = 'gallery-img-wrapper';
    wrapper.innerHTML = `
        <img src="${img.url}" alt="Crop visual detail">
    `;
    
    // If admin, show delete button on images
    if (state.user && state.user.role === 'admin') {
        const delBtn = document.createElement('button');
        delBtn.className = 'btn-delete-img';
        delBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
        delBtn.title = 'Remove Image';
        delBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            if (confirm("Are you sure you want to delete this reference image?")) {
                try {
                    const res = await fetch(`/api/crops/${cropId}/images/${img.id}`, { method: 'DELETE' });
                    const resData = await res.json();
                    if (resData.message) {
                        showToast(resData.message);
                        showCropDetail(cropId);
                    } else {
                        showToast(resData.error, "error");
                    }
                } catch (err) {
                    showToast("Error removing image.", "error");
                }
            }
        });
        wrapper.appendChild(delBtn);
    }
    
    return wrapper;
}

function renderComments(comments) {
    const list = document.getElementById('comments-list-container');
    list.innerHTML = '';
    
    if (comments.length === 0) {
        list.innerHTML = `<p class="subtitle text-center">No comments or questions posted yet. Be the first to start the conversation!</p>`;
        return;
    }
    
    comments.forEach(c => {
        const card = document.createElement('div');
        card.className = 'comment-card';
        
        let deleteBtnHtml = '';
        if (state.user && state.user.role === 'admin') {
            deleteBtnHtml = `<button class="btn-delete-comment" data-comment-id="${c.id}"><i class="fa-solid fa-trash"></i> Delete</button>`;
        }
        
        card.innerHTML = `
            <div class="comment-meta">
                <span class="comment-author">${c.email}</span>
                <span class="comment-date">${new Date(c.timestamp).toLocaleString()}</span>
            </div>
            <div class="comment-body">${c.text}</div>
            ${deleteBtnHtml}
        `;
        
        if (state.user && state.user.role === 'admin') {
            card.querySelector('.btn-delete-comment').addEventListener('click', async () => {
                if (confirm("Do you want to delete this comment for violating terms?")) {
                    try {
                        const res = await fetch(`/api/comments/${c.id}`, { method: 'DELETE' });
                        const resData = await res.json();
                        if (resData.message) {
                            showToast(resData.message);
                            showCropDetail(state.currentCropId);
                        } else {
                            showToast(resData.error, "error");
                        }
                    } catch (err) {
                        showToast("Error deleting comment.", "error");
                    }
                }
            });
        }
        
        list.appendChild(card);
    });
}

// Post Comment Submission
document.getElementById('comment-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const txtArea = document.getElementById('comment-text');
    const text = txtArea.value.trim();
    
    if (!text) return;
    
    // Client-side quick ToS check before sending (Banned words warnings)
    const banned = ['scam', 'spam', 'hack', 'buy online', 'fuck', 'shit', 'idiot', 'advertising', 'viagra'];
    const found = banned.filter(word => text.toLowerCase().includes(word));
    if (found.length > 0) {
        showToast("Your comment contains keywords that violate our Terms of Service (ToS). Please edit.", "error");
        return;
    }
    
    try {
        const res = await fetch(`/api/crops/${state.currentCropId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        
        const data = await res.json();
        if (data.message) {
            showToast(data.message);
            txtArea.value = '';
            showCropDetail(state.currentCropId);
        } else {
            showToast(data.error, "error");
            // If user got logged out or banned
            checkAuth();
        }
    } catch (err) {
        showToast("Error posting comment.", "error");
    }
});

// --- MESSAGES / PRIVATE CHAT ---

async function loadMessagesDashboard() {
    try {
        const res = await fetch('/api/messages');
        const data = await res.json();
        
        if (data.error) {
            showToast(data.error, "error");
            switchView('catalog');
            return;
        }
        
        // 1. Render recent chats (conversations user is in)
        const recentList = document.getElementById('recent-chats-list');
        recentList.innerHTML = '';
        if (data.recent_chats.length === 0) {
            recentList.innerHTML = `<li class="subtitle text-center">No active chats</li>`;
        } else {
            data.recent_chats.forEach(u => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <button class="chat-item ${state.activeChatUserId === u.id ? 'active' : ''}" data-user-id="${u.id}">
                        <i class="fa-solid fa-circle-user"></i>
                        <span>${u.email}</span>
                    </button>
                `;
                li.querySelector('button').addEventListener('click', () => openPrivateChat(u.id, u.email));
                recentList.appendChild(li);
            });
        }
        
        // 2. Render all available contacts
        const allList = document.getElementById('all-users-list');
        allList.innerHTML = '';
        if (data.all_users.length === 0) {
            allList.innerHTML = `<li class="subtitle text-center">No users available</li>`;
        } else {
            data.all_users.forEach(u => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <button class="chat-item ${state.activeChatUserId === u.id ? 'active' : ''}" data-user-id="${u.id}">
                        <i class="fa-regular fa-comment"></i>
                        <span>${u.email} ${u.role === 'admin' ? '<span class="status-badge active" style="font-size:9px; padding:1px 4px; border:none; background:rgba(16,185,129,0.15)">Admin</span>' : ''}</span>
                    </button>
                `;
                li.querySelector('button').addEventListener('click', () => openPrivateChat(u.id, u.email));
                allList.appendChild(li);
            });
        }
        
        // 3. Keep current history loaded if open
        if (state.activeChatUserId) {
            fetchChatHistory(state.activeChatUserId);
        }
        
    } catch (err) {
        console.error("Error loading messages dashboard:", err);
    }
}

async function openPrivateChat(userId, email) {
    state.activeChatUserId = userId;
    
    // Visual indicators toggle
    document.querySelectorAll('.chat-item').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll(`.chat-item[data-user-id="${userId}"]`).forEach(btn => btn.classList.add('active'));
    
    document.getElementById('chat-empty-state').classList.add('hidden');
    document.getElementById('chat-active-state').classList.remove('hidden');
    document.getElementById('chat-partner-name').textContent = email;
    
    fetchChatHistory(userId);
}

async function fetchChatHistory(userId) {
    try {
        const res = await fetch(`/api/messages?with_user_id=${userId}`);
        if (res.status === 404) {
            // Target user doesn't exist anymore or banned
            state.activeChatUserId = null;
            document.getElementById('chat-active-state').classList.add('hidden');
            document.getElementById('chat-empty-state').classList.remove('hidden');
            loadMessagesDashboard();
            return;
        }
        
        const history = await res.json();
        const container = document.getElementById('chat-messages-body');
        
        // Check if list changed to avoid flickering scrolling
        const currentCount = container.children.length;
        
        container.innerHTML = '';
        if (history.length === 0) {
            container.innerHTML = `
                <div class="chat-empty-state" style="padding-top:20px;">
                    <p>No messages yet. Send a message to start conversing!</p>
                </div>
            `;
        } else {
            history.forEach(msg => {
                const bubble = document.createElement('div');
                const isSent = msg.sender_id === state.user.id;
                bubble.className = `chat-bubble ${isSent ? 'sent' : 'received'}`;
                bubble.innerHTML = `
                    <span>${msg.text}</span>
                    <span class="chat-time">${new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                `;
                container.appendChild(bubble);
            });
        }
        
        // Auto scroll to bottom for new messages
        if (history.length !== currentCount) {
            container.scrollTop = container.scrollHeight;
        }
        
    } catch (err) {
        console.error("Error loading chat history:", err);
    }
}

// Send Chat Message Form
document.getElementById('chat-send-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const input = document.getElementById('chat-message-text');
    const text = input.value.trim();
    
    if (!text || !state.activeChatUserId) return;
    
    try {
        const res = await fetch('/api/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                receiver_id: state.activeChatUserId,
                text: text
            })
        });
        
        const data = await res.json();
        if (data.message) {
            input.value = '';
            fetchChatHistory(state.activeChatUserId);
            // Refresh sidebar list to update last message ordering
            loadMessagesDashboard();
        } else {
            showToast(data.error, "error");
        }
    } catch (err) {
        showToast("Could not send message.", "error");
    }
});

// Periodic polling for new private messages in background
function startMessagePolling() {
    if (state.pollingInterval) clearInterval(state.pollingInterval);
    
    state.pollingInterval = setInterval(() => {
        // If in message view and chat is open, refresh history
        if (state.view === 'messages' && state.activeChatUserId) {
            fetchChatHistory(state.activeChatUserId);
        }
        
        // Also check if any new messages are received to highlight DM badge
        if (state.user) {
            checkForNewDMs();
        }
    }, 4000);
}

function stopMessagePolling() {
    if (state.pollingInterval) {
        clearInterval(state.pollingInterval);
        state.pollingInterval = null;
    }
}

async function checkForNewDMs() {
    try {
        const res = await fetch('/api/messages');
        const data = await res.json();
        
        // Check if there are messages we haven't seen in our current open chat
        // (Just a simple counter badge simulation)
        // If there are recent chats, we can count total messages count
        // For simplicity, let's keep it simple.
    } catch (e) {
        // Quietly fail background checks
    }
}

// --- ADMIN CONTROL PANELS ---

async function loadAdminDashboard() {
    // Populate crop selects
    try {
        const res = await fetch('/api/crops');
        const crops = await res.json();
        
        const disSelect = document.getElementById('disease-crop-select');
        const imgSelect = document.getElementById('upload-crop-select');
        
        disSelect.innerHTML = '';
        imgSelect.innerHTML = '';
        
        crops.forEach(c => {
            const opt1 = document.createElement('option');
            opt1.value = c.id;
            opt1.textContent = `${c.common_name} (${c.scientific_name})`;
            disSelect.appendChild(opt1);
            
            const opt2 = opt1.cloneNode(true);
            imgSelect.appendChild(opt2);
        });
    } catch (err) {
        console.error("Error populating admin options:", err);
    }
    
    // Load registered users list
    fetchAdminUsersList();
}

async function fetchAdminUsersList() {
    try {
        const res = await fetch('/api/users');
        const users = await res.json();
        
        const tbody = document.getElementById('moderation-users-list');
        tbody.innerHTML = '';
        
        if (users.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No regular users registered.</td></tr>`;
            return;
        }
        
        users.forEach(u => {
            const tr = document.createElement('tr');
            const isActive = u.status === 'active';
            const actionBtn = isActive 
                ? `<button class="btn btn-ban btn-sm" onclick="banUser(${u.id})"><i class="fa-solid fa-user-slash"></i> Ban User</button>`
                : `<button class="btn btn-unban btn-sm" onclick="unbanUser(${u.id})"><i class="fa-solid fa-user-check"></i> Restore</button>`;
                
            tr.innerHTML = `
                <td>${u.id}</td>
                <td>${u.email}</td>
                <td>${u.role}</td>
                <td><span class="status-badge ${isActive ? 'active' : 'banned'}">${u.status}</span></td>
                <td>${actionBtn}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Error loading user moderation list:", err);
    }
}

// Global functions for inline click events in moderation table
window.banUser = async function(userId) {
    if (confirm("Are you sure you want to ban this user? Banned users cannot post comments or send direct messages.")) {
        try {
            const res = await fetch(`/api/users/${userId}/ban`, { method: 'POST' });
            const data = await res.json();
            if (data.message) {
                showToast(data.message);
                fetchAdminUsersList();
            } else {
                showToast(data.error, "error");
            }
        } catch (err) {
            showToast("Failed to ban user.", "error");
        }
    }
};

window.unbanUser = async function(userId) {
    try {
        const res = await fetch(`/api/users/${userId}/unban`, { method: 'POST' });
        const data = await res.json();
        if (data.message) {
            showToast(data.message);
            fetchAdminUsersList();
        } else {
            showToast(data.error, "error");
        }
    } catch (err) {
        showToast("Failed to unban user.", "error");
    }
};

// Admin Forms Submit Listeners

// 1. Add Crop
document.getElementById('admin-add-crop-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const scientific_name = document.getElementById('crop-sc-name').value.trim();
    const common_name = document.getElementById('crop-cm-name').value.trim();
    const medicinal_benefit = document.getElementById('crop-med-benefit').value.trim();
    
    try {
        const res = await fetch('/api/crops', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scientific_name, common_name, medicinal_benefit })
        });
        
        const data = await res.json();
        if (data.message) {
            showToast(data.message);
            document.getElementById('admin-add-crop-form').reset();
            loadAdminDashboard(); // reload options
        } else {
            showToast(data.error, "error");
        }
    } catch (err) {
        showToast("Error adding crop profile.", "error");
    }
});

// 2. Add/Edit Disease
document.getElementById('admin-manage-disease-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const crop_id = document.getElementById('disease-crop-select').value;
    const disease_name = document.getElementById('disease-name').value.trim();
    const description = document.getElementById('disease-desc').value.trim();
    const treatment = document.getElementById('disease-treatment').value.trim();
    const is_treatable = document.getElementById('disease-treatable').checked;
    
    try {
        const res = await fetch(`/api/crops/${crop_id}/diseases`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ disease_name, description, treatment, is_treatable })
        });
        
        const data = await res.json();
        if (data.message || data.disease_name) {
            showToast(data.message || "Disease info saved.");
            document.getElementById('admin-manage-disease-form').reset();
        } else {
            showToast(data.error, "error");
        }
    } catch (err) {
        showToast("Error logging disease information.", "error");
    }
});

// 3. Upload Reference Images
document.getElementById('admin-upload-image-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const crop_id = document.getElementById('upload-crop-select').value;
    const type = document.getElementById('upload-type').value;
    const fileInput = document.getElementById('upload-file');
    
    if (fileInput.files.length === 0) return;
    
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('type', type);
    
    try {
        const res = await fetch(`/api/crops/${crop_id}/images`, {
            method: 'POST',
            body: formData
        });
        
        const data = await res.json();
        if (data.message) {
            showToast(data.message);
            document.getElementById('admin-upload-image-form').reset();
        } else {
            showToast(data.error, "error");
        }
    } catch (err) {
        showToast("Upload failed. Only JPG, JPEG, and PNG are accepted.", "error");
    }
});

// Admin Subtabs View Toggler
document.querySelectorAll('.admin-tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.admin-tab-panel').forEach(p => p.classList.add('hidden'));
        
        this.classList.add('active');
        const panelId = this.getAttribute('data-target');
        document.getElementById(panelId).classList.remove('hidden');
    });
});

// --- AUTH MODAL FLOW ---

function toggleAuthModal(show) {
    const modal = document.getElementById('auth-modal');
    if (show) modal.classList.remove('hidden');
    else modal.classList.add('hidden');
}

document.getElementById('btn-close-auth').addEventListener('click', () => toggleAuthModal(false));

// Close modal clicking outside content
document.getElementById('auth-modal').addEventListener('click', (e) => {
    if (e.target.id === 'auth-modal') toggleAuthModal(false);
});

// Auth form switching tabs
const authTabs = {
    loginBtn: document.getElementById('auth-tab-login-btn'),
    registerBtn: document.getElementById('auth-tab-register-btn'),
    loginForm: document.getElementById('login-form'),
    registerForm: document.getElementById('register-form')
};

authTabs.loginBtn.addEventListener('click', () => {
    authTabs.loginBtn.classList.add('active');
    authTabs.registerBtn.classList.remove('active');
    authTabs.loginForm.classList.remove('hidden');
    authTabs.registerForm.classList.add('hidden');
});

authTabs.registerBtn.addEventListener('click', () => {
    authTabs.registerBtn.classList.add('active');
    authTabs.loginBtn.classList.remove('active');
    authTabs.registerForm.classList.remove('hidden');
    authTabs.loginForm.classList.add('hidden');
});

// Submit Login
authTabs.loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (data.user) {
            state.user = data.user;
            showToast(data.message);
            toggleAuthModal(false);
            authTabs.loginForm.reset();
            updateAuthHeader();
            enableProtectedNavigation();
            startMessagePolling();
            
            // Refresh comments to allow entry
            if (state.view === 'crop-detail' && state.currentCropId) {
                showCropDetail(state.currentCropId);
            }
        } else {
            showToast(data.error || "Authentication failed.", "error");
        }
    } catch (err) {
        showToast("Error connecting to auth service.", "error");
    }
});

// Submit Registration
authTabs.registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    
    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (data.message) {
            showToast(data.message);
            // Switch to login tab
            authTabs.loginBtn.click();
            document.getElementById('login-email').value = email;
            authTabs.registerForm.reset();
        } else {
            showToast(data.error || "Registration failed.", "error");
        }
    } catch (err) {
        showToast("Error connecting to registration service.", "error");
    }
});

// Handle Logout
async function handleLogout() {
    try {
        const res = await fetch('/api/auth/logout', { method: 'POST' });
        const data = await res.json();
        showToast(data.message);
        state.user = null;
        updateAuthHeader();
        disableProtectedNavigation();
        stopMessagePolling();
        
        // Refresh detail view if currently open
        if (state.view === 'crop-detail' && state.currentCropId) {
            showCropDetail(state.currentCropId);
        }
    } catch (err) {
        showToast("Error logging out.", "error");
    }
}

// Attach redirect login/register links in comment auth prompt
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('auth-link-trigger')) {
        e.preventDefault();
        toggleAuthModal(true);
    }
});

// Navigation Link Listeners
navLinks.catalog.addEventListener('click', () => switchView('catalog'));
navLinks.messages.addEventListener('click', () => switchView('messages'));
navLinks.admin.addEventListener('click', () => switchView('admin'));
navLinks.logo.addEventListener('click', (e) => {
    e.preventDefault();
    switchView('catalog');
});
document.getElementById('btn-back-to-catalog').addEventListener('click', () => switchView('catalog'));

// --- INITIALIZATION ---
window.addEventListener('DOMContentLoaded', () => {
    // Check initial authentication and fetch initial catalog
    checkAuth();
    switchView('catalog');
});
