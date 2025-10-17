const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const ws = new WebSocket(protocol + window.location.host + `/ws/server/${serverId}/`);


let debug = false;

let peers = new Map();
let connected_users = [];
let connectionStates = new Map(); // Трекинг состояний подключений

audioContainer = document.getElementById("connected_audio");
btnConnect = document.getElementById("connect_audio");
btnDisconnect = document.getElementById("disconnect_audio");
btnDisconnect.disabled = true;

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

// Утилиты для работы с асинхронностью
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const waitForCondition = async (condition, timeout = 5000, interval = 100) => {
    const start = Date.now();
    while (Date.now() - start < timeout) {
        if (condition()) return true;
        await delay(interval);
    }
    throw new Error('Timeout waiting for condition');
};

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
    } catch (error) {
        console.error('Error handling message:', error);
    }
};

const constraints = {
    'video': debug,
    'audio': true
};

// Инициализация с гарантией однократного выполнения
let init = async () => {
    if (initializationPromise) {
        return initializationPromise;
    }
    
    initializationPromise = (async () => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error("getUserMedia is not supported in this browser or context.");
        }

        try {
            localStream = await navigator.mediaDevices.getUserMedia(constraints);
            isInitialized = true;
            console.log("Media initialized successfully");
            return localStream;
        } catch (error) {
            console.error("Error getting user media:", error);
            initializationPromise = null;
            throw error;
        }
    })();
    
    return initializationPromise;
};

// Обработчики сообщений с правильной асинхронностью
async function handleNewOffer(data) {
    if (!connected_users.includes(data.userid)) {
        connected_users.push(data.userid);
    }
    
    addAudioPeer(data.userid);
    console.log("New offer from:", data.userid);
    
    // Ждем инициализации перед созданием ответа
    await ensureInitialized();
    await createAnswer(data.userid, data.sdp);
}

async function handleNewAnswer(data) {
    const peer = peers.get(data.userid);
    if (peer) {
        await peer.setRemoteDescription(data.sdp);
        connectionStates.set(data.userid, 'connected');
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
    await ensureInitialized();

    for (const userId of connected_users) {
        addAudioPeer(userId);
    }
}

async function handleUserDisconnect(data) {
    await user_disconnect(data.userid);
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

// инициализация завершена
async function ensureInitialized() {
    if (!isInitialized) {
        await init();
    }
}

let addAudioPeer = (userId, userAvatar) => {
    // User card
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
        username.innerText = `User ${userId}`; // Display user ID

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
    await ensureInitialized();
    
    const peerConnection = new RTCPeerConnection(servers);
    connectionStates.set(userId, 'creating');
    
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
        connectionStates.set(userId, 'track_added');

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
    
    peerConnection.onconnectionstatechange = () => {
        console.log(`Peer connection state for ${userId}:`, peerConnection.connectionState);
        connectionStates.set(userId, peerConnection.connectionState);
    };
    
    peers.set(userId, peerConnection);
    return peerConnection;
}

let createOffer = async (userId) => {
    try {
        console.log("Creating offer for:", userId);
        
        const peerConnection = await createPeerConnection(userId);
        
        await waitForCondition(() => 
            peerConnection.signalingState === 'stable', 3000);
        
        const offer = await peerConnection.createOffer();
        console.log("Offer created:", offer);
        
        await peerConnection.setLocalDescription(offer);
        console.log("Local description set");
        
        // Ждем установления локального описания
        await waitForCondition(() => 
            peerConnection.localDescription !== null, 3000);
        
        console.log("Sending offer to:", userId);
        sendActionSocket("offer", {
            "sdp": offer,
            "to": userId
        });
        
    } catch (error) {
        console.error("Error creating offer for", userId, ":", error);
        // Очищаем failed connection
        if (peers.has(userId)) {
            peers.get(userId).close();
            peers.delete(userId);
            connectionStates.delete(userId);
        }
    }
}

let createAnswer = async (userId, offer) => {
    try {
        console.log("Creating answer for:", userId);
        
        const peerConnection = await createPeerConnection(userId);
        
        await peerConnection.setRemoteDescription(offer);
        console.log("Remote description set for answer");
        
        const answer = await peerConnection.createAnswer();
        console.log("Answer created:", answer);
        
        await peerConnection.setLocalDescription(answer);
        console.log("Local description set for answer");
        
        // Ждем установления локального описания
        await waitForCondition(() => 
            peerConnection.localDescription !== null, 3000);
        
        console.log("Sending answer to:", userId);
        sendActionSocket("answer", {
            "sdp": answer, 
            "to": userId
        });
        
    } catch (error) {
        console.error("Error creating answer for", userId, ":", error);
        if (peers.has(userId)) {
            peers.get(userId).close();
            peers.delete(userId);
            connectionStates.delete(userId);
        }
    }
}

let user_disconnect = async (userId) => {
    console.log("User disconnected:", userId);
    if (peers.has(userId)) {
        peers.get(userId).close();
        peers.delete(userId);
        connectionStates.delete(userId);
        console.log("Closed peer connection with user:", userId);
    }
}

// Основные обработчики с правильной асинхронностью
btnConnect.addEventListener('click', async function(){
    btnConnect.disabled = true;
    btnDisconnect.disabled = false;
    
    try {
        await ensureInitialized();
        addAudioPeer(myuserId, myAvatar);
        
        if (connected_users.length === 0) {
            sendActionSocket("start_voice", {});
        } else {
            // Последовательно создаем оферы для избежания гонки
            for (const userId of connected_users) {
                addAudioPeer(userId);
                await createOffer(userId);
                // Небольшая задержка между подключениями
                await delay(100);
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
    
    // Закрываем все подключения
    const disconnectPromises = [];
    for (let [userId, peer] of peers) {
        if (userId != myuserId) {
            console.log("Disconnecting from", userId);
            disconnectPromises.push(user_disconnect(userId));
        }
    }
    
    await Promise.allSettled(disconnectPromises);
    peers.clear();
    connectionStates.clear();
});

// Инициализация при загрузке
init().catch(error => {
    console.error("Initialization failed:", error);
});

window.addEventListener('beforeunload', function() {
    if (connected_users.includes(String(myuserId)) || connected_users.includes(myuserId))
    {
        sendActionSocket("disconnect_voice", {});
        for (let [userId, peer] of peers) {
            if (userId != myuserId) {
                peer.close();
            }
        }
        peers.clear();
        connectionStates.clear();

    }


});