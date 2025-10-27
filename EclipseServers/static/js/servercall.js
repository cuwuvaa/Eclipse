const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const ws = new WebSocket(protocol + window.location.host + `/ws/server/${serverId}/`);


let debug = true;

let peers = new Map();
let connected_users = [];

audioContainer = document.getElementById("connected_audio");
btnConnect = document.getElementById("connect_audio");
btnDisconnect = document.getElementById("disconnect_audio");
btnDisconnect.disabled = true;

let btnSendMessage = document.getElementById("message-send-button")

let mychannel;
let localStream;
let isInitialized = false;
let initializationPromise = null;

const servers = {
    iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun2.l.google.com:19302" },
        {
            urls: "turn:openrelay.metered.ca:80",
            username: "openrelayproject",
            credential: "openrelayproject"
        }
    ]
};

let pendingIceCandidates = new Map(); // userId -> [candidates]

async function handleIceCandidate(data) {
    const peer = peers.get(data.userid);
    
    if (!peer) {
        console.warn(`No peer for ICE candidate: ${data.userid}`);
        return;
    }
    
    // Если remoteDescription еще не установлен, буферизуем
    if (!peer.remoteDescription) {
        if (!pendingIceCandidates.has(data.userid)) {
            pendingIceCandidates.set(data.userid, []);
        }
        pendingIceCandidates.get(data.userid).push(data.ice);
        console.log(`Buffered ICE candidate for ${data.userid}`);
        return;
    }
    
    // Если remoteDescription установлен, сразу добавляем
    try {
        await peer.addIceCandidate(data.ice);
    } catch (error) {
        console.error('Error adding ICE candidate:', error);
    }
}


function sendActionSocket(action, message) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            'action': action,
            'message': message
        }));
    } else {
        console.warn('WebSocket not open, message not sent:', action);
    }
}

ws.onmessage = async function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    
    try {
        if (data.type === 'connection_established') {
            mychannel = data.channel_name;
            console.log("rendering")
            sendActionSocket("render", {});
        }
        
        if (data.action == "new_offer") {
            await handleNewOffer(data);
        }

        if (data.action == "new_answer") {
            await handleNewAnswer(data);
        }
        
        if (data.action == "ice") {
            await handleIceCandidate(data);
        }
        
        if (data.action == "listusers") {
            await handleUserList(data);
        }

        if (data.action == "user_disconnect") {
            await handleUserDisconnect(data);
        }

        if (data.action == "background") {
            await handleBackgroundTask(data);
        }
        if (data.action == "new_message")
        {
            displayMessage(data.usermsg);
        }
    } catch (error) {
        console.error('Error handling message:', error);
    }
};

const constraints = {
    'video': debug,
    'audio': true
};

let init = async () => {
localStream = await navigator.mediaDevices.getUserMedia(constraints);
}

async function handleNewOffer(data) {
    if (!connected_users.includes(data.userid)) {
        connected_users.push(data.userid);
    }
    
    addAudioPeer(data.userid);
    console.log("New offer from:", data.userid);
    
    await createAnswer(data.userid, data.sdp);
}

async function handleNewAnswer(data) {
    const peer = peers.get(data.userid);
    if (peer) {
        await peer.setRemoteDescription(data.sdp);
    } else {
        console.warn(`No peer found for user ${data.userid} when setting answer`);
    }
}

async function handleIceCandidate(data) {
    const peer = peers.get(data.userid);
    if (peer && data.ice) {
        await peer.addIceCandidate(data.ice);
    }
}

async function handleUserList(data) {
    connected_users = Object.keys(data.users);

    for (const userId of connected_users) {
        addAudioPeer(userId);
    }
}

async function handleUserDisconnect(data) {
    await user_disconnect(data.userid);
    console.log(`user ${data.userid} has been disconnected`)
    removeAudioElement(data.userid);
    const index = connected_users.indexOf(data.userid);
    if (index > -1) {
        connected_users.splice(index, 1);
    }
}

async function handleBackgroundTask(data) {
    if (data.task == "connection") {
        addAudioPeer(data.userid);
        if (!connected_users.includes(data.userid)) {
            connected_users.push(data.userid);
        }
    }
    if (data.task == "disconnection") {
        removeAudioElement(data.userid);
        const index = connected_users.indexOf(data.userid);
        if (index > -1) {
            connected_users.splice(index, 1);
        }
    }
}

let addAudioPeer = (userId, userAvatar) => {
    if (!document.getElementById(`user_card_${userId}`)) {
        const userCard = document.createElement("div");
        userCard.id = `user_card_${userId}`;
        userCard.className = "user-card";

        const avatar = document.createElement("img");
        avatar.className = "user-avatar";
        axios.get(`${window.location.protocol}//${window.location.host}/api/user/${userId}`)
            .then(response => {
                console.log('Data received:', response.data);
               avatar.src = response.data.avatar
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                avatar.src = '/static/EclipseUser/default_images/default_avatar.png';
            });

        const username = document.createElement("div");
        username.className = "user-name";
        username.innerText = `User ${userId}`;

        const canvas = document.createElement("canvas");
        canvas.id = `waveform_${userId}`;
        canvas.width = 150;
        canvas.height = 50;

        userCard.appendChild(avatar);
        userCard.appendChild(username);
        userCard.appendChild(canvas);

        document.getElementById("user_list").appendChild(userCard);
    }

    // Audio/video element
    if (document.getElementById(`div_user${userId}`)) {
        return;
    }
    
    const userWrapper = document.createElement("div");
    userWrapper.id = `div_user${userId}`;
    const userAudio = debug ? document.createElement("video"): document.createElement("audio");
    userAudio.id = `audio_user${userId}`;
    userAudio.playsInline = true;
    userAudio.autoplay = true;
    userAudio.muted = false;
    userWrapper.appendChild(userAudio);
    audioContainer.appendChild(userWrapper);
}

let removeAudioElement = (userId) => {
    const element = document.getElementById(`div_user${userId}`);
    if (element) {
        element.remove();
    }
    const userCard = document.getElementById(`user_card_${userId}`);
    if (userCard) {
        userCard.remove();
    }
}

let createPeerConnection = async (userId) => {
    
    const peerConnection = new RTCPeerConnection(servers);
    
    const remoteStream = new MediaStream();
    
    // Добавляем локальные треки
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });
    
    document.getElementById(`audio_user${userId}`).srcObject = remoteStream;
    
    peerConnection.ontrack = (event) => {
        console.log("Received remote track from:", userId);
        event.streams[0].getTracks().forEach(track => {
            remoteStream.addTrack(track);
        });

        // Create waveform
        const canvas = document.getElementById(`waveform_${userId}`);
        if (canvas) {
            new Waveform(remoteStream, canvas);
        }
    };

    peerConnection.onicecandidate = async (event) => {
        if (event.candidate) {
            console.log("Sending ICE candidate to:", userId);
            sendActionSocket("ice", {"candidate": event.candidate, "to": userId});
        }
    };
    // В createPeerConnection добавить:
    peerConnection.onconnectionstatechange = () => {
        console.log(`Peer connection state for ${userId}:`, peerConnection.connectionState);
        
        // При успешном соединении очищаем буфер
        if (peerConnection.connectionState === 'connected') {
            pendingIceCandidates.delete(userId);
        }
    };

    peers.set(userId, peerConnection);
    return peerConnection;
}

let createOffer = async (userId) => {
    try {
        const peerConnection = await createPeerConnection(userId);        
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        
        // После установки localDescription проверяем буферизованные кандидаты
        if (pendingIceCandidates.has(userId)) {
            const candidates = pendingIceCandidates.get(userId);
            for (const candidate of candidates) {
                await peerConnection.addIceCandidate(candidate).catch(console.error);
            }
            pendingIceCandidates.delete(userId);
        }
        
        sendActionSocket("offer", {"sdp": offer, "to": userId});
        
    } catch (error) {
        console.error("Error creating offer for", userId, ":", error);
    }
}

let createAnswer = async (userId, offer) => {
    try {
        console.log("Creating answer for:", userId);
        
        const peerConnection = await createPeerConnection(userId);
        
        await peerConnection.setRemoteDescription(offer);
        console.log("Remote description set for answer");

        if (pendingIceCandidates.has(userId)) {
            const candidates = pendingIceCandidates.get(userId);
            console.log(`Processing ${candidates.length} buffered ICE candidates for ${userId}`);
            
            for (const candidate of candidates) {
                try {
                    await peerConnection.addIceCandidate(candidate);
                } catch (error) {
                    console.error('Error adding buffered ICE candidate:', error);
                }
            }
            pendingIceCandidates.delete(userId);
        }

        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);

        sendActionSocket("answer", {
            "sdp": answer, 
            "to": userId
        });
        
    } catch (error) {
        console.error("Error creating answer for", userId, ":", error);

    }
}

let user_disconnect = async (userId) => {
    console.log("User disconnected:", userId);
    if (peers.has(userId)) {
        peers.get(userId).close();
        peers.delete(userId);
        console.log("Closed peer connection with user:", userId);
    }
}

btnConnect.addEventListener('click', async function(){
    btnConnect.disabled = true;
    btnDisconnect.disabled = false;
    
    try {
        addAudioPeer(myuserId, myAvatar);
        if (connected_users.length === 0) {
            sendActionSocket("start_voice", {});
        } else {
            for (const userId of connected_users) {
                addAudioPeer(userId);
                await createOffer(userId);
            }
        }
    } catch (error) {
        console.error("Error connecting:", error);
        btnConnect.disabled = false;
        btnDisconnect.disabled = true;
    }
});

btnDisconnect.addEventListener('click', async function(){
    console.log("Disconnecting voice");
    btnConnect.disabled = false;
    btnDisconnect.disabled = true;
    
    removeAudioElement(myuserId);
    sendActionSocket("disconnect_voice", {});
    
    const disconnectPromises = [];
    for (let [userId, peer] of peers) {
        if (userId != myuserId) {
            console.log("Disconnecting from", userId);
            disconnectPromises.push(user_disconnect(userId));
        }
    }
    peers.clear();
});


init().catch(error => {
    console.error("Initialization failed:", error);
});

window.addEventListener('beforeunload', function() {
    if (connected_users.includes(String(myuserId)) || connected_users.includes(myuserId))
    {
    console.log("Disconnecting voice");
    btnConnect.disabled = false;
    btnDisconnect.disabled = true;
    
    removeAudioElement(myuserId);
    sendActionSocket("disconnect_voice", {});
    
    const disconnectPromises = [];
    for (let [userId, peer] of peers) {
        if (userId != myuserId) {
            console.log("Disconnecting from", userId);
            disconnectPromises.push(user_disconnect(userId));
        }
    }
    peers.clear();
    }
});


btnSendMessage.addEventListener("click", async function(){
    const inputField = document.getElementById("message-input-field")
    let content = inputField.value
    console.log("sending message: ", content)
    sendActionSocket("user_message", content)
    inputField.value = '';
})