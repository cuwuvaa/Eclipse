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
    btnMic.innerText = isMuted ? "Unmute" : "Mute";
}

function updateCamButton(isOff) {
    btnCam.innerText = isOff ? "Camera on" : "Camera off";
}

function updateDemoButton(isOff) {
    btnDemo.innerText = isOff ? "Screen on" : "Stop Screen Share";
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
            const kickBtn = document.createElement("button");
            kickBtn.innerText = `kick`;
            kickBtn.onclick = () => sendActionSocket("voice_kick", { "id": e.id });
            userDiv.appendChild(kickBtn);
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
            let role, action;
            if (element.role === "moderator") {
                role = "user";
                action = "demote";
            } else {
                action = "promote";
                role = "moderator";
            }
            let is_online = element.is_online ? "online" : "offline";
            const memberdiv = document.createElement("div");
            memberdiv.id = `profile-${element.id}`;
            memberdiv.className = "member-card";
            
            let membernameHTML = `<h1>ID: ${element.id} | ${element.displayname}`;
            if (element.user === userdata.user) {
                membernameHTML += ` (You)`;
            }
            membernameHTML += `</h1><h2>role: ${element.role}</h2>`;
            memberdiv.innerHTML = membernameHTML;

            if (element.user !== userdata.user) {
                 switch (userdata.role) {
                    case "creator":
                        memberdiv.innerHTML += `<button onclick="kickUser(${element.id})">kick</button>`;
                        if (element.role !== 'creator') {
                           memberdiv.innerHTML += `<button onclick="changeRole(${element.id},'${role}')">${action} to ${role}</button>`;
                        }
                        break;
                    case "moderator":
                        if (element.role !== "creator" && element.role !== "moderator") {
                            memberdiv.innerHTML += `<button onclick="kickUser(${element.id})">kick</button>`;
                        }
                        break;
                }
            }
            memberdiv.innerHTML += `<h5 id="status-${element.id}" class="${is_online}">${is_online}</h5>`
            membersContainer.appendChild(memberdiv);
        }
    } catch (error) {
        console.log("Error loading users", error);
    }
}

async function updateUser(element, status) {
    try
    {
        document.getElementById(`profile-${element.id}`)
        let is_online = status ? "online" : "offline"
        const statusElement = document.getElementById(`status-${element.id}`);
        statusElement.innerText = is_online;
        statusElement.className = is_online;
    }
    catch(error)
    {
            let role, action;
            if (element.role === "moderator") {
                role = "user";
                action = "demote";
            } else {
                action = "promote";
                role = "moderator";
            }
            let is_online = element.is_online ? "online" : "offline"
            const memberdiv = document.createElement("div");
            memberdiv.id = `profile-${element.id}`;
            memberdiv.className = "member-card";

            let membernameHTML = `<h1>ID: ${element.id} | ${element.displayname}`;
            if (element.user === userdata.user) {
                membernameHTML += ` (You)`;
            }
            membernameHTML += `</h1><h2>role: ${element.role}</h2>`;
            memberdiv.innerHTML = membernameHTML;

            if (element.user !== userdata.user) {
                 switch (userdata.role) {
                    case "creator":
                        memberdiv.innerHTML += `<button onclick="kickUser(${element.id})">kick</button>`;
                        if (element.role !== 'creator') {
                           memberdiv.innerHTML += `<button onclick="changeRole(${element.id},'${role}')">${action} to ${role}</button>`;
                        }
                        break;
                    case "moderator":
                        if (element.role !== "creator" && element.role !== "moderator") {
                            memberdiv.innerHTML += `<button onclick="kickUser(${element.id})">kick</button>`;
                        }
                        break;
                }
            }
            memberdiv.innerHTML += `<h5 id="status-${element.id}" class="${is_online}">${is_online}</h5>`
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
    let messageDiv = `<div id="message-${e.id}" class="message-item">`;
    messageDiv += `<h3>${e.displayname} | ${e.role}</h3>
                   <h4>${new Date(e.timestamp).toLocaleString()}</h4>
                   <h2>${e.text}</h2>`;

    const canDelete = (userdata.role === "creator" && e.role !== "creator") ||
                      (userdata.role === "moderator" && e.role === "user") ||
                      (e.roomsender_id === userdata.id);

    if (canDelete) {
        messageDiv += `<button onclick="deleteMessage(${e.id})">delete</button>`;
    }
    messageDiv += `</div>`;
    return messageDiv;
}

function appendMessage(e) {
    const messageHTML = createMessageHTML(e);
    messageContainer.insertAdjacentHTML('beforeend', messageHTML);
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

function prependMessage(e) {
    const messageHTML = createMessageHTML(e);
    topMarker.insertAdjacentHTML('afterend', messageHTML);
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
