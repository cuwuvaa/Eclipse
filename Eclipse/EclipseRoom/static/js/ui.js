// --- State for Message Pagination ---
let nextMessagesUrl = null;

// --- Functions from call.js ---

/**
 * Renders a user's name in the voice participants list.
 * @param {object} e - User data object with username/displayname and id.
 */
async function renderUser(e) {
    const userContainer = document.getElementById('voice_participants');
    if (userContainer && !document.getElementById(`user-${e.id}`)) {
        const userDiv = document.createElement('div')
        const userElement = document.createElement('h1');
        if (userdata.role == "moderator" || userdata.role == "creator" && userdata.id != e.id)
        {
            const kickBtn = document.createElement("button")
            kickBtn.innerText = `kick ${e.displayname}`
            kickBtn.addEventListener('click', ()=> {
                sendActionSocket("voice_kick", {"id":e.id})
            })
            userDiv.appendChild(kickBtn);
        }
        userElement.textContent = e.username || e.displayname;
        userDiv.id = `user-${e.id}`;
        userDiv.appendChild(userElement);
        userContainer.appendChild(userDiv);
    }
}
/**
 * Shows or hides the local video element.
 * @param {boolean} status - If true, shows the video; otherwise, removes it.
 */
async function showLocalVideo(status) {
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

/**
 * Creates an audio element for a remote user's stream.
 * @param {MediaStream} stream - The remote user's media stream.
 * @param {string} peerId - The ID of the remote user.
 */
function handleAudioTrack(stream, peerId) {
    if (document.getElementById(`remote-audio-${peerId}`)) return;
    const remoteAudio = document.createElement('audio');
    remoteAudio.id = `remote-audio-${peerId}`;
    remoteAudio.srcObject = stream;
    remoteAudio.autoplay = true;
    document.getElementById('remote-media-container').appendChild(remoteAudio);
    
    console.log(`Аудио обработано для пира: ${peerId}`);
}

/**
 * Creates or updates a video element for a remote user's stream.
 * @param {MediaStream} stream - The remote user's media stream.
 * @param {string} peerId - The ID of the remote user.
 * @param {boolean} status - The initial enabled status of the video track.
 */
function handleVideoTrack(stream, peerId, status) {
    let remoteVideo = document.getElementById(`remote-video-${peerId}`);
    if (!remoteVideo) {
        remoteVideo = document.createElement('video');
        remoteVideo.id = `remote-video-${peerId}`;
        remoteVideo.autoplay = true;
        document.getElementById('remote-media-container').appendChild(remoteVideo);
        console.log(`Видео-элемент создан для пира: ${peerId}`);
    }
    
    remoteVideo.srcObject = stream;

    if (!status) {
        remoteVideo.style.display = 'none';
    } else {
        remoteVideo.style.display = 'block';
    }
}


// --- Functions from message.js ---

/**
 * Fetches data from a given URL.
 * @param {string} url - The URL to fetch data from.
 * @returns {Promise<object|null>} - The fetched data as a JSON object, or null on error.
 */

async function fetchdata(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Error status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.log('Error fetching data');
        return null;
        
    }
}


/**
 * Fetches the first page of messages and sets up the scroll listener.
 */

const topMarker = document.getElementById('topMarker');
async function renderMessages() {
    // Clear container but keep the marker
    messageContainer.innerHTML = '';
    messageContainer.appendChild(topMarker);

    try {
        const data = await fetchdata(`${localhost}api/rooms/${roomId}/messages/`);
        if (data) {
            nextMessagesUrl = data.next; 
            const messages = data.results;
            messages.reverse().forEach(message => {
                appendMessage(message); 
            });
            
            messageContainer.scrollTop = messageContainer.scrollHeight;

            const observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    handleMessageScroll();
                }
            });

            observer.observe(topMarker);
        }
    }
    catch (error)
    {
        console.log("error occured! join server");
    }
}

/**
 * Handles the scroll event on the message container to fetch older messages.
 */
async function handleMessageScroll() {
    if (nextMessagesUrl) {
        console.log('Scrolled to top, fetching older messages...');
        try {
            const data = await fetchdata(nextMessagesUrl);
            if (data) {
                nextMessagesUrl = data.next;
                const olderMessages = data.results;
                olderMessages.forEach(message => {
                    prependMessage(message);
                });
                // Move the marker to the new top (which is the end of the container)
                messageContainer.appendChild(topMarker);
            }
        } catch (error) {
            console.error('Error fetching older messages:', error);
        }
    }
}

/**
 * Creates the HTML string for a single message.
 * @param {object} e - Message data object.
 * @returns {string} - The HTML string for the message.
 */
function createMessageHTML(e) {
    let messageDiv = `<div id="message-${e.id}"" class="message-item" style="width: max-content; border: 1px solid #ccc; margin: 5px; padding: 5px;">`

    messageDiv += `<h3>${e.displayname} | ${e.role}</h3>
                <h4>${new Date(e.timestamp).toLocaleString()}</h4>
                <h2>${e.text}</h2>`
    

    switch (userdata.role)
    {
        case "creator":
            messageDiv += `<button onclick="deleteMessage(${e.id})">delete</button>`
            break;
        case "moderator":
            if (e.role != "creator")
            {
            messageDiv += `<button onclick="deleteMessage(${e.id})">delete</button>`
            }
            break;
        case "user":
            if (e.roomsender_id == userdata.id)
            {
            messageDiv += `<button onclick="deleteMessage(${e.id})">delete</button>`
            }
            break;
    }
    messageDiv += `</div>`
    return messageDiv;
}

/**
 * Appends a new message to the bottom of the container.
 * @param {object} e - Message data object.
 */
function appendMessage(e) {
    const messageHTML = createMessageHTML(e);
    messageContainer.insertAdjacentHTML('afterbegin', messageHTML);
}

/**
 * Prepends an older message to the top of the container.
 * @param {object} e - Message data object.
 */
function prependMessage(e) {
    const messageHTML = createMessageHTML(e);
    // The marker is at the end, so insert before it.
    topMarker.insertAdjacentHTML('beforebegin', messageHTML);
}

async function renderMembers() {
    try{await fetchdata(`${localhost}api/rooms/${roomId}/users/`).then((roomUsers) => {for (element of roomUsers){
        let role;
        let action;
        if (element.role == "moderator")
        {
            role = "user"
            action = "reduce"
        }
        else {
            action = "upper"
            role = "moderator"
        }
        let memberdiv = document.createElement("div")
        memberdiv.id = `profile-${element.id}`
        let membername = document.createElement("h1")
        membername.innerHTML = `ID: ${element.id} | ${element.displayname} `
        memberdiv.appendChild(membername);
        membersContainer.appendChild(memberdiv);
        if (element.user === userdata.user)
        {
            membername.innerHTML += `(You)`;
            memberdiv.innerHTML += `            
                <h2>role: ${element.role}</h1> 
            `
            continue;
        }
        memberdiv.innerHTML += `            
            <h2>role: ${element.role}</h1> 
        `
        switch (userdata.role){
            case "creator":
                memberdiv.innerHTML += `<button onclick="kickUser(${element.id})">kick</button>`;
                memberdiv.innerHTML += `<button onclick="changeRole(${element.id},'${role}')">${action} role</button>`;
                break;
            case "moderator":
                if (element.role != "creator")
                {
                    memberdiv.innerHTML += `<button onclick="kickUser(${element.id})">kick</button>`;
                }
                break;
        }
    };
    })}
    catch (error)
    {
        console.log("error loading users");
        console.log(error)
    }
}