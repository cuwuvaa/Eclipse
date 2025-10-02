const connectBtn = document.getElementById("connectBtn")
const disconnectBtn = document.getElementById("disconnectBtn")
const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const audiocontainer = document.getElementById("audiocontainer");
var voiceSocket; // Вынесем WebSocket в глобальную переменную
var peers = {}; // Объект для хранения всех пиров

// Функция для отправки сообщений через WebSocket
function sendVoiceSocket(action, message){
       console.log('sent:', action, " with message:", message);
    voiceSocket.send(JSON.stringify({
        "peer": userid,
        "action": action,
        "message": message
    }));
}

function renderVoiceUsers(users) {
    const voiceUsersDiv = document.getElementById('voice_users');
    voiceUsersDiv.innerHTML = '';
    for (const user of users) {
        const userDiv = document.createElement('div');
        userDiv.classList.add('voice-user');
        userDiv.innerHTML = `
            <img src="${user.avatar_url}" alt="${user.username}'s avatar">
            <span>${user.username}</span>
        `;
        voiceUsersDiv.appendChild(userDiv);
    }
}

function websocketOnMessage(event){
    var parsedData = JSON.parse(event.data)
    var user = parsedData['peer']
    var action = parsedData['action']

    if (action === 'voice_users') {
        renderVoiceUsers(parsedData.users);
        return;
    }

    if (userid == user){
        return; // Игнорируем собственные сообщения
    }
    var receiver_channel_name = parsedData['message']['receiver_channel_name']

    if (action == "new-peer") {
        createOffer(user, receiver_channel_name);
        return;
    }
    
    if (action == "new-offer") {
        var offer = parsedData['message']['sdp'];
        createAnswer(user, offer, receiver_channel_name);
        return;
    }

    if (action == "new-answer") {
        var answer = parsedData['message']['sdp'];
        var peer = peers[user];
        if (peer) {
            peer.setRemoteDescription(answer)
                .then(() => {
                    console.log("Remote description set successfully");
                })
                .catch(error => {
                    console.error("Error setting remote description:", error);
                });
        }
        return;
    }

    if (action == "ice-candidate") {
        var candidate = parsedData['message']['candidate'];
        var peer = peers[user];
        if (peer) {
            peer.addIceCandidate(new RTCIceCandidate(candidate))
                .then(() => {
                    console.log("ICE candidate added successfully");
                })
                .catch(error => {
                    console.error("Error adding ICE candidate:", error);
                });
        }
        console.log(peers)
        return;
    }
}

function createOffer(user, receiver_channel_name) {
    var peer = new RTCPeerConnection({
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' }
        ]
    });
    
    peers[user] = peer; // Сохраняем peer в объект peers
    console.log("PEER SAVED: ", peers[user])
    addLocalTracks(peer);
    setupPeerConnection(peer, user); // Настраиваем обработчики событий
    
    var remoteAudio = createAudio(user, peer);

    // Создаем offer
    peer.createOffer()
        .then(offer => {
            return peer.setLocalDescription(offer);
        })
        .then(() => {
            // Отправляем offer через WebSocket
            sendVoiceSocket("new-offer", {
                "sdp": peer.localDescription,
                "receiver_channel_name": receiver_channel_name
            });
        })
        .catch(error => {
            console.error("Error creating offer:", error);
        });
}

function createAnswer(user, offer, receiver_channel_name) {
    var peer = new RTCPeerConnection({
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' }
        ]
    });
    
    peers[user] = peer; // Сохраняем peer в объект peers
    console.log("PEER SAVED: ", peers[user])
    addLocalTracks(peer);
    setupPeerConnection(peer, user); // Настраиваем обработчики событий
    
    var remoteAudio = createAudio(user, peer);

    // Устанавливаем удаленное описание (offer) и создаем answer
    peer.setRemoteDescription(offer)
        .then(() => {
            return peer.createAnswer();
        })
        .then(answer => {
            return peer.setLocalDescription(answer);
        })
        .then(() => {
            // Отправляем answer через WebSocket
            sendVoiceSocket("new-answer", {
                "sdp": peer.localDescription,
                "receiver_channel_name": receiver_channel_name
            });
        })
        .catch(error => {
            console.error("Error creating answer:", error);
        });
}

// Функция для настройки обработчиков событий peer connection
function setupPeerConnection(peer, user) {
    // Обработчик ICE кандидатов
    peer.onicecandidate = (event) => {
        if (event.candidate) {
            sendVoiceSocket("ice-candidate", {
                "candidate": event.candidate,
                "receiver_channel_name": user
            });
        }
    };

    // Обработчик изменения состояния соединения
    peer.onconnectionstatechange = () => {
        console.log(`Connection state with ${user}: ${peer.connectionState}`);
    };

    // Обработчик изменения ICE состояния
    peer.oniceconnectionstatechange = () => {
        console.log(`ICE connection state with ${user}: ${peer.iceConnectionState}`);
    };
}

function addLocalTracks(connection){
    localStream.getTracks().forEach(track => {
        connection.addTrack(track, localStream);
    });
}

connectBtn.addEventListener("click", event => {
    console.log(userid);
    
    voiceSocket = new WebSocket(protocol + window.location.host + `/ws/voicechat/${serverId}/`);
    
    voiceSocket.addEventListener('open', () => {
        sendVoiceSocket('new-peer', {});
    });
    
    voiceSocket.addEventListener('message', websocketOnMessage);
    voiceSocket.addEventListener('close', event => {
        console.log("connection closed.");
        // Очищаем все peer соединения при закрытии WebSocket
        Object.values(peers).forEach(peer => peer.close());
        peers = {};
    });

    connectBtn.style.display = 'none';
    disconnectBtn.style.display = 'block';
});

disconnectBtn.addEventListener("click", event => {
    voiceSocket.close();
    connectBtn.style.display = 'block';
    disconnectBtn.style.display = 'none';
});

var localStream = new MediaStream();

const constraints = {
    'video': false,
    'audio': true
};

const localAudio = document.getElementById("myaudio");

var userMedia = navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        localStream = stream;
        localAudio.srcObject = localStream;
        localAudio.muted = true;
    }).catch(error => {
        console.log("error: ", error);
    });

function createAudio(user, peer){
    var newAudio = document.createElement('audio');
    newAudio.id = user + "-audio";
    newAudio.autoplay = true;
    newAudio.playsInline = true;

    var remoteStream = new MediaStream();
    newAudio.srcObject = remoteStream;

    peer.addEventListener("track", async(event) => {
        remoteStream.addTrack(event.track, remoteStream);
    });
    
    audiocontainer.appendChild(newAudio);
    return newAudio;
}