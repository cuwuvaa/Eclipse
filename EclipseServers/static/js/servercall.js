const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const ws = new WebSocket(protocol + window.location.host + `/ws/server/${serverId}/`);

let peers = new Map()
let connected_users = [];

audioContainer = document.getElementById("connected_audio")
btnConnect = document.getElementById("connect_audio")
btnDisconnect = document.getElementById("disconnect_audio")
btnDisconnect.disabled = true;

let mychannel;
let localStream;
let remoteStream;

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
}

function sendActionSocket(action,message)
{
    ws.send(JSON.stringify({
        'action':action,
        'message':message
    }))
}

ws.onmessage = async function(event) {
    const data = JSON.parse(event.data);
    console.log(data)
    if (data.type === 'connection_established') {
        mychannel = data.channel_name;
        sendActionSocket("render",{})
    }
    if (data.action == "new_offer")
    {
        if (!connected_users.includes(data.userid)) {
            connected_users.push(data.userid);
        }
        addAudioPeer(data.userid)
        console.log("new connection");
        console.log("connection data: ", data);
        createAnswer(data.userid,data.sdp)
    }

    if (data.action == "new_answer")
    {
        peers.get(data.userid).setRemoteDescription(data.sdp)

    }
     if (data.action == "ice") {
        peers.get(data.userid).addIceCandidate(data.ice)
    }
    if (data.action == "listusers")
    {
        connected_users = Object.keys(data.users)
        connected_users.forEach(element => {
            addAudioPeer(element);
        });
    }

    if (data.action == "user_disconnect")
    {
        user_disconnect(data.userid)
        document.getElementById(`div_user${data.userid}`).remove();
        console.log(peers);
    }

    if (data.action == "user_connect")
    {
        connected_users.push(data.userid)
    }

    if (data.action == "background")
    {
        if (data.task == "connection")
        {
            addAudioPeer(data.userid)
            if (!connected_users.includes(data.userid)) {
                connected_users.push(data.userid);
            }
        }
        if (data.task == "disconnection")
        {
            removeAudioElement(data.userid);
            const index = connected_users.indexOf(data.userid);
            if (index > -1) {
                connected_users.splice(index, 1);
            }
        }
    }

};

const constraints = {
    'video': true,
    'audio': true
};


let init = async () =>{
    localStream = await navigator.mediaDevices.getUserMedia(constraints);
}


let addAudioPeer = (userId) => {
    if (document.getElementById(`div_user${userId}`)) {
        return; // Уже существует
    }
    
    const userWrapper = document.createElement("div");
    userWrapper.id = `div_user${userId}`;
    const userAudio = document.createElement("video");
    userAudio.id = `audio_user${userId}`;
    userAudio.playsInline = true;
    userAudio.autoplay = true;
    userAudio.muted = false;
    userWrapper.innerText += `User ${userId}`; 
    userWrapper.appendChild(userAudio);
    audioContainer.appendChild(userWrapper);
}

let removeAudioElement = (userId) => {
    const element = document.getElementById(`div_user${userId}`);
    if (element) {
        element.remove();
    }
}

let createPeerConnection = async (userId) => {
    const peerConnection = new RTCPeerConnection(servers);
    console.log(`Created peerConnection with ID: ${peerConnection._id} for user: ${userId}`);
    
    // Создаем отдельный remoteStream для каждого пользователя
    const remoteStream = new MediaStream();
    
    // Добавляем локальные треки
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });
    document.getElementById(`audio_user${userId}`).srcObject = remoteStream;
    // Обрабатываем удаленные треки
    peerConnection.ontrack = (event) => {
        console.log("Received remote track from:", userId);
        event.streams[0].getTracks().forEach(track => {
            remoteStream.addTrack(track);
        });

    };
    
    // Обрабатываем ICE кандидаты
    peerConnection.onicecandidate = async (event) => {
        if (event.candidate) {
            console.log("Sending ICE candidate to:", userId);
            sendActionSocket("ice", event.candidate);
        }
    };
    peers.set(userId, peerConnection);
}

let createOffer = async (userId) => {
    try {
        console.log("Creating offer for:", userId);
        await createPeerConnection(userId);
        const peerConnection = await peers.get(userId)
        console.log("Peer connection object in createOffer:", peerConnection);
        
        const offer = await peerConnection.createOffer();
        console.log("Offer created:", offer); // Added log
        try {
            await peerConnection.setLocalDescription(offer);
        } catch (e) {
            console.error("Error setting local description for offer:", e);
        }
        
        console.log("Sending offer to:", userId);
        sendActionSocket("offer", {
            "sdp": offer,
            "to": userId  // Важно указать кому отправляем
        });
        
    } catch (error) {
        console.error("Error creating offer:", error);
    }
}

let createAnswer = async (userId, offer) => {
    try {
        console.log("Creating answer for:", userId);
        createPeerConnection(userId);
        const peerConnection = peers.get(userId);

        console.log("Received offer for answer:", offer); // Added log
        try {
            await peerConnection.setRemoteDescription(offer);
            console.log("Remote description set for answer.");
        } catch (e) {
            console.error("Error setting remote description for answer:", e);
        }
        const answer = await peerConnection.createAnswer();
        console.log("Answer created:", answer); // Added log
        try {
            await peerConnection.setLocalDescription(answer);
        } catch (e) {
            console.error("Error setting local description for answer:", e);
        }
        
        console.log("Sending answer to:", userId);
        sendActionSocket("answer", {
            "sdp": answer, 
            "to": userId  // Важно указать кому отправляем
        });
        
    } catch (error) {
        console.error("Error creating answer:", error);
    }
}

let user_disconnect = (userId) => {
    console.log("User disconnected:", userId);
    if (peers.has(userId)) {
        peers.get(userId).close();
        peers.delete(userId);
        console.log("Closed peer connection with user:", userId);
    }
}


btnConnect.addEventListener('click', function(){
    if (connected_users.length == 0)
    {
        sendActionSocket("start_voice", {})
    }
    else
    {
    connected_users.forEach(userId => {
                addAudioPeer(userId);
                createOffer(userId); // Создаем офер для всех существующих пользователей
        })
    }
    addAudioPeer(myuserId);
    btnConnect.disabled = true;
    btnDisconnect.disabled = false;
})

btnDisconnect.addEventListener('click', function(){
    console.log("you pushed disconnect")
    removeAudioElement(myuserId)
    sendActionSocket("disconnect_voice",{});
    for (let user of peers.keys()) {
        if (user != myuserId)
        {
            console.log("disconnecting with ", user)
            peers.get(user).close()
        }   //проблема в нескольких дисконнектах в коде этом
    }
    peers = new Map();
    btnConnect.disabled = false;
    btnDisconnect.disabled = true;
})

init();