console.log("voicechat.js")
var peers = {}; // хранение всех пиров
var localStream = new MediaStream();

const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://'; //кода будет ссл будет использоваться вебсокет секьюрд
const chatSocket = new WebSocket(protocol + window.location.host + '/ws/server/' + serverId + '/')

const chatSubmit = document.querySelector('#chat-message-submit');
const chatInput = document.querySelector('#message-input');
const chatContainer = document.querySelector('#chat-messages')

const serverSideBar = document.querySelector('#server-sidebar')
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');

const voiceUsers = document.getElementById('voice_users');
const onlineCount = document.getElementById('online-count');

const audiocontainer = document.getElementById("audiocontainer");
const localAudio = document.getElementById("myaudio");
let _onlineCount = 0;

disconnectBtn.style="display:none;"
disconnectBtn.disabled=true;

const constraints = {
    'video': false,
    'audio': true
};

function sendVoiceSocket(action, message){
    chatSocket.send(JSON.stringify({
        "peer": userid,
        "action": action,
        "message": message
    }));
}

var userMedia = navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        localStream = stream;
        localAudio.srcObject = localStream;
        localAudio.muted = true;
    }).catch(error => {
        console.log("error: ", error);
    });


function websocketOnMessage(event){
    var parsedData = JSON.parse(event.data)
    var user = parsedData['peer']
    var action = parsedData['action']

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
        return;
    }
        if(action == "chat_message"){
        const formattedTimestamp = formatTimestamp(data.timestamp);
        chatContainer.innerHTML += `                    <div class="message">
                        <img class="message-avatar" src=${data.avatar_url}>
                        <div class="message-content">
                            <div class="message-header">
                                <span class="message-author">${data.sender}</span>
                                <span class="message-time">${formattedTimestamp}</span>
                            </div>
                            <div class="message-text">
                                ${data.content}
                            </div>
                        </div>
                    </div>`
    }
    if (action == "voice_connection")
        {
            voiceUsers.innerHTML += ` <div id="user${data.user_id}"}>${data.user}</div>`;
            _onlineCount += 1;
            onlineCount.innerHTML = `Онлайн: ${_onlineCount}`;
            return;
        }
    if (action == "render") {
        for (let user of data.users_connected_voice) {
            console.log(user.username);
            voiceUsers.innerHTML += `<h3>${user.username}</h3><br>`;
        }
        _onlineCount = data.users_connected_voice.length
        onlineCount.innerHTML = `Онлайн: ${_onlineCount}`;
        return;
    }
    if (action == "voice_disconnection")
        {
            let user_card = document.getElementById(`user${data.user_id}`)
            user_card.remove()
            _onlineCount -= 1;
            onlineCount.innerHTML = `Онлайн: ${_onlineCount}`;
        }
    return;
}

function createOffer(user, receiver_channel_name) {
    var peer = new RTCPeerConnection({
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' }
        ]
    });
    
    peers[user] = peer; // Сохраняем peer в объект peers
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
connectBtn.addEventListener("click", event =>
{    
    connectBtn.style="display:none;";
    connectBtn.disabled=true;
    disconnectBtn.style=""
    disconnectBtn.disabled=false;

    chatSocket.send(JSON.stringify('new-peer', {}));
    
    chatSocket.addEventListener('message', websocketOnMessage);
    chatSocket.addEventListener('close', event => {
        console.log("connection closed.");
        //удаляем все peerы соединения при закрытии WebSocket
        Object.values(peers).forEach(peer => peer.close());
        peers = {};
    });
})

disconnectBtn.onclick = function (event)
{
    chatSocket.send(JSON.stringify(
            {
                'action':"voice_disconnect",
                'message':"sucessfully"
            }));
    voiceSocket.close()
    disconnectBtn.style="display:none;";
    disconnectBtn.disabled=true;
    connectBtn.style=""
    connectBtn.disabled=false;
}

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



chatSubmit.onclick = async function (event) {
    const message = chatInput.value;
        try {
            await chatSocket.send(JSON.stringify({
                'action':"send_chatmsg",
                'message': message,
            }));
            chatInput.value = '';
        } catch (e) {
            console.error(e);
        }
};