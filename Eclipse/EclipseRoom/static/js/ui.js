// --- State for Message Pagination ---
let nextMessagesUrl = null;
const topMarker = document.getElementById('topMarker');

// --- UI Update Functions ---

function updateCallButtons(isConnected) {
    btnConnect.style.display = isConnected ? 'none' : 'inline-block';
    btnDisconnect.style.display = isConnected ? 'inline-block' : 'none';
    btnMic.style.display = isConnected ? 'inline-block' : 'none';
    btnCam.style.display = isConnected ? 'inline-block' : 'none';
    btnDemo.style.display = isConnected ? 'inline-block' : 'none';
    btnConnect.disabled = isConnected;
}

function updateMicButton(isMuted) {
    btnMic.innerHTML = isMuted ? '<i class="fas fa-microphone-slash"></i>' : '<i class="fas fa-microphone"></i>';
}

function updateCamButton(isOff) {
    btnCam.innerHTML = isOff ? '<i class="fas fa-video-slash"></i>' : '<i class="fas fa-video"></i>';
}

function updateDemoButton(isOff) {
    btnDemo.innerHTML = isOff ? '<i class="fas fa-desktop"></i>' : '<i class="fas fa-stop"></i>';
}

function clearMessageInput() {
    inMessage.value = '';
}

function removeElementById(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

function reloadPage() {
    window.location.reload();
}

// --- DOM Creation Functions ---

function createRemoteAudio(stream, peerId) {
    const remoteAudio = document.createElement('audio');
    remoteAudio.id = `remote-audio-${peerId}`;
    remoteAudio.srcObject = stream;
    remoteAudio.autoplay = true;
    document.getElementById('remote-media-container').appendChild(remoteAudio);
}

function createRemoteVideo(stream, peerId, status) {
    const remoteVideo = document.createElement('video');
    remoteVideo.id = `remote-video-${peerId}`;
    remoteVideo.srcObject = stream;
    remoteVideo.autoplay = true;
    if (!status) {
        remoteVideo.style.display = 'none';
    }
    const userCard = document.getElementById(`user-${peerId}`);
    if (userCard) {
        userCard.appendChild(remoteVideo);
    }
}

function showLocalVideo(status) {
    const localVideoContainer = document.getElementById('local-video-container');
    localVideoContainer.innerHTML = ''; // Clear the container
    if (status) {
        const localVideo = document.createElement('video');
        localVideo.srcObject = localStream;
        localVideo.autoplay = true;
        localVideo.muted = true;
        localVideo.playsInline = true;
        localVideo.id = 'local-video';
        localVideo.style.width = '200px';
        localVideo.style.border = '2px solid green';
        localVideoContainer.appendChild(localVideo);
    }
}

function toggleRemoteVideo(userId, show) {
    const remoteVideo = document.getElementById(`remote-video-${userId}`);
    if (remoteVideo) {
        remoteVideo.style.display = show ? "block" : "none";
    }
}


// --- User and Message Rendering ---



async function renderUser(e) {
    if (userContainer && !document.getElementById(`user-${e.id}`)) {
        const userDiv = document.createElement('div');
        userDiv.id = `user-${e.id}`;
        userDiv.className = 'participant-card';

        const userAvatar = document.createElement('img');
        userAvatar.src = e.avatar;
        userAvatar.className = 'participant-avatar';
        userDiv.appendChild(userAvatar);

        const userElement = document.createElement('h1');
        userElement.textContent = e.displayname;
        userDiv.appendChild(userElement);

        if ((userdata.role === "moderator" || userdata.role === "creator") && userdata.id !== e.id) {
            const actionWindow = document.createElement('div');
            actionWindow.className = 'action-window';
            const buttons = [
                { text: 'Kick from voice', onClick: () => sendActionSocket("voice_kick", { "id": e.id }) }
            ];
            buttons.forEach(button => {
                const btn = document.createElement('button');
                btn.className = 'small-btn';
                btn.innerText = button.text;
                btn.onclick = button.onClick;
                actionWindow.appendChild(btn);
            });
            userDiv.appendChild(actionWindow);
        }
        userContainer.appendChild(userDiv);
    }
}

async function renderMembers() {
    try {
        const roomUsers = await fetchdata(`${localhost}api/rooms/${roomId}/users/`);
        if (!roomUsers) return;

        membersContainer.innerHTML = ''; // Clear existing members
        for (const element of roomUsers) {
            const memberdiv = document.createElement("div");
            memberdiv.id = `profile-${element.id}`;
            memberdiv.className = "member-card";

            const avatar = document.createElement('img');
            avatar.src = element.avatar;
            avatar.className = 'member-avatar';
            memberdiv.appendChild(avatar);

            const memberInfo = document.createElement('div');
            memberInfo.className = 'member-info';
            
            let membernameHTML = `<h1>${element.displayname}`;
            if (element.user === userdata.user) {
                membernameHTML += ` (You)`;
            }
            membernameHTML += `</h1>`;
            memberInfo.innerHTML = membernameHTML;
            
            let is_online = element.is_online ? "online" : "offline";
            const statusElement = document.createElement('h5');
            statusElement.id = `status-${element.id}`;
            statusElement.className = is_online;
            statusElement.innerText = is_online;
            memberInfo.appendChild(statusElement)

            memberdiv.appendChild(memberInfo)

            if (element.user !== userdata.user) {
                const actionWindow = document.createElement('div');
                actionWindow.className = 'action-window';
                actionWindow.style.display = 'none';

                const buttons = [];
                switch (userdata.role) {
                    case "creator":
                        buttons.push({ text: 'Kick from room', onClick: () => kickUser(element.id) });
                        if (element.role !== 'creator') {
                           let role = element.role === "moderator" ? "user" : "moderator"
                           let action = element.role === "moderator" ? "demote" : "promote"
                           buttons.push({ text: `${action} to ${role}`, onClick: () => changeRole(element.id, role) });
                        }
                        break;
                    case "moderator":
                        if (element.role !== "creator" && element.role !== "moderator") {
                            buttons.push({ text: 'Kick from room', onClick: () => kickUser(element.id) });
                        }
                        break;
                }

                if (buttons.length > 0) {
                    buttons.forEach(button => {
                        const btn = document.createElement('button');
                        btn.className = 'small-btn';
                        btn.innerText = button.text;
                        btn.onclick = button.onClick;
                        actionWindow.appendChild(btn);
                    });
                    
                    const manageBtn = document.createElement('button');
                    manageBtn.className = 'manage-btn';
                    manageBtn.innerText = 'Manage';
                    manageBtn.onclick = () => {
                        actionWindow.style.display = actionWindow.style.display === 'none' ? 'flex' : 'none';
                    };

                    memberdiv.appendChild(manageBtn);
                    memberdiv.appendChild(actionWindow);
                }
            }
            membersContainer.appendChild(memberdiv);
        }
    } catch (error) {
        console.log("Error loading users", error);
    }
}

async function updateUser(element, status) {
    const existingUser = document.getElementById(`profile-${element.id}`);
    if (existingUser) {
        let is_online = status ? "online" : "offline";
        const statusElement = document.getElementById(`status-${element.id}`);
        statusElement.innerText = is_online;
        statusElement.className = is_online;
    } else {
        const memberdiv = document.createElement("div");
        memberdiv.id = `profile-${element.id}`;
        memberdiv.className = "member-card";

        const avatar = document.createElement('img');
        avatar.src = element.avatar;
        avatar.className = 'member-avatar';
        memberdiv.appendChild(avatar);

        const memberInfo = document.createElement('div');
        memberInfo.className = 'member-info';

        let membernameHTML = `<h1>${element.displayname}`;
        if (element.user === userdata.user) {
            membernameHTML += ` (You)`;
        }
        membernameHTML += `</h1>`;
        memberInfo.innerHTML = membernameHTML;
        
        let is_online = element.is_online ? "online" : "offline";
        const statusElement = document.createElement('h5');
        statusElement.id = `status-${element.id}`;
        statusElement.className = is_online;
        statusElement.innerText = is_online;
        memberInfo.appendChild(statusElement);

        memberdiv.appendChild(memberInfo);

        if (element.user !== userdata.user) {
            const actionWindow = document.createElement('div');
            actionWindow.className = 'action-window';
            actionWindow.style.display = 'none';

            const buttons = [];
            switch (userdata.role) {
                case "creator":
                    buttons.push({ text: 'Kick from room', onClick: () => kickUser(element.id) });
                    if (element.role !== 'creator') {
                        let role = element.role === "moderator" ? "user" : "moderator";
                        let action = element.role === "moderator" ? "demote" : "promote";
                        buttons.push({ text: `${action} to ${role}`, onClick: () => changeRole(element.id, role) });
                    }
                    break;
                case "moderator":
                    if (element.role !== "creator" && element.role !== "moderator") {
                        buttons.push({ text: 'Kick from room', onClick: () => kickUser(element.id) });
                    }
                    break;
            }

            if (buttons.length > 0) {
                buttons.forEach(button => {
                    const btn = document.createElement('button');
                    btn.className = 'small-btn';
                    btn.innerText = button.text;
                    btn.onclick = button.onClick;
                    actionWindow.appendChild(btn);
                });

                const manageBtn = document.createElement('button');
                manageBtn.className = 'manage-btn';
                manageBtn.innerText = 'Manage';
                manageBtn.onclick = () => {
                    actionWindow.style.display = actionWindow.style.display === 'none' ? 'flex' : 'none';
                };

                memberdiv.appendChild(manageBtn);
                memberdiv.appendChild(actionWindow);
            }
        }
        membersContainer.appendChild(memberdiv);
    }
}


async function renderMessages() {
    messageContainer.innerHTML = '';
    messageContainer.appendChild(topMarker);

    try {
        const data = await fetchdata(`${localhost}api/rooms/${roomId}/messages/`);
        if (data) {
            nextMessagesUrl = data.next;
            const messages = data.results;
            messages.reverse().forEach(message => prependMessage(message)); // Prepend to keep order correct
            
            messageContainer.scrollTop = messageContainer.scrollHeight;

            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    handleMessageScroll();
                }
            });
            observer.observe(topMarker);
        }
    } catch (error) {
        console.log("Error rendering messages", error);
    }
    sendActionSocket("status","online")
}

async function handleMessageScroll() {
    if (nextMessagesUrl) {
        try {
            const data = await fetchdata(nextMessagesUrl);
            if (data) {
                nextMessagesUrl = data.next;
                const olderMessages = data.results;
                olderMessages.reverse().forEach(message => {
                    prependMessage(message, false); // Prepend older messages without scrolling
                });
            }
        } catch (error) {
            console.error('Error fetching older messages:', error);
        }
    }
}

function createMessageHTML(e) {
    const messageDiv = document.createElement('div');
    messageDiv.id = `message-${e.id}`;
    messageDiv.className = 'message-item';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = `<h3>${e.displayname} | ${e.role}</h3>
                                <h4>${new Date(e.timestamp).toLocaleString()}</h4>
                                <h2>${e.text}</h2>`;
    messageDiv.appendChild(messageContent);

    const canDelete = (userdata.role === "creator" && e.role !== "creator") ||
                      (userdata.role === "moderator" && e.role === "user") ||
                      (e.roomsender_id === userdata.id);

    if (canDelete) {
        const actionWindow = document.createElement('div');
        actionWindow.className = 'action-window';
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.onclick = () => deleteMessage(e.id);
        actionWindow.appendChild(deleteBtn);
        messageDiv.appendChild(actionWindow);
    }
    return messageDiv;
}

function appendMessage(e) {
    const messageHTML = createMessageHTML(e);
    messageContainer.appendChild(messageHTML);
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

function prependMessage(e) {
    const messageHTML = createMessageHTML(e);
    topMarker.after(messageHTML);
}


// --- Data Fetching ---

async function fetchdata(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Error status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.log('Error fetching data:', error);
        return null;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- Room Settings Modal ---
function initializeUI() {
    const roomSettingsModal = document.getElementById('room-settings-modal');
    const roomSettingsBtn = document.getElementById('room-settings-btn');
    const roomSettingsCloseBtn = roomSettingsModal.querySelector('.close-btn');
    const roomSettingsForm = document.getElementById('room-settings-form');

    const deleteRoomModal = document.getElementById('delete-room-modal');
    const deleteRoomBtn = document.getElementById('delete-room-btn');
    const deleteRoomCloseBtn = deleteRoomModal.querySelector('.close-btn');
    const deleteRoomForm = document.getElementById('delete-room-form');

    if (roomSettingsBtn && (userdata.role === 'creator' || userdata.role === 'moderator')) {
        roomSettingsBtn.style.display = 'block';
        roomSettingsBtn.onclick = function() {
            roomSettingsModal.style.display = 'block';
        }
    }

    if (userdata.role === 'creator') {
        deleteRoomBtn.style.display = 'block';
        deleteRoomBtn.onclick = function() {
            roomSettingsModal.style.display = 'none';
            deleteRoomModal.style.display = 'block';
        }
    }

    if (roomSettingsCloseBtn) {
        roomSettingsCloseBtn.onclick = function() {
            roomSettingsModal.style.display = 'none';
        }
    }
    
    if (deleteRoomCloseBtn) {
        deleteRoomCloseBtn.onclick = function() {
            deleteRoomModal.style.display = 'none';
        }
    }

    window.onclick = function(event) {
        if (event.target == roomSettingsModal) {
            roomSettingsModal.style.display = 'none';
        }
        if (event.target == deleteRoomModal) {
            deleteRoomModal.style.display = 'none';
        }
    }

    if (roomSettingsForm) {
        roomSettingsForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const formData = new FormData();
            const description = document.getElementById('room-description').value;
            const avatar = document.getElementById('room-avatar').files[0];

            if (description) {
                formData.append('description', description);
            }
            if (avatar) {
                formData.append('avatar', avatar);
            }

            const response = await fetch(`/api/rooms/${roomId}/update/`, {
                method: 'PATCH',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: formData,
            });

            if (response.ok) {
                window.location.reload();
            } else {
                console.error('Failed to update room settings');
            }
        });
    }

    if (deleteRoomForm) {
        deleteRoomForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const passphrase = document.getElementById('passphrase-input').value;
            const response = await fetch(`/api/rooms/${roomId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ passphrase }),
            });

            if (response.ok) {
                window.location.href = '/';
            } else {
                console.error('Failed to delete room');
            }
        });
    }
}


