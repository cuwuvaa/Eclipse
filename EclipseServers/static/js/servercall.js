const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const ws = new WebSocket(protocol + window.location.host + `/ws/server/${serverId}/`);

let peers = new Map()


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
    ]
}

function sendActionSocket(action,message)
{
    ws.send(JSON.stringify({
        'action':action,
        'message':message
    }))
}

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(data)
    if (data.type === 'connection_established') {
        mychannel = data.channel_name;
        sendActionSocket("render",{})
            }
    if (data.action == "new_offer")
    {
        console.log("new connection");
        console.log("connection data: ", data);
        createAnswer(data.userid,data.sdp)
    }

    if (data.action == "new_answer")
    {
        console.log("answer from user ", data.userid);
        peerConnection.setRemoteDescription(data.sdp);
        peers.set(data.userid, peerConnection);
    }
    if (data.action == "ice")
    {
        console.log("new icecandidate: ", data.ice)
        peerConnection.addIceCandidate(data.ice)
    }
    if (data.action == "listusers")
    {
        let connected_users = Object.keys(data.users)
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
    if (data.action == "background")
    {
        if (data.task == "connection")
        {
            addAudioPeer(data.userid)
        }
        if (data.task == "disconnection")
        {
            document.getElementById(`div_user${data.userid}`).remove();
        }
    }

};

const constraints = {
    'video': false,
    'audio': true
};


let init = async () =>{
    localStream = await navigator.mediaDevices.getUserMedia(constraints);
}

let addAudioPeer = (userId) =>
{
    const userWrapper = document.createElement("div")
    userWrapper.id = `div_user${userId}`;
    const userAudio = document.createElement("audio")
    userAudio.id = `audio_user${userId}`;
    userAudio.playsinline = true;
    userAudio.autoplay = true;
    userAudio.muted = false;
    userWrapper.innerText += `${userId}`; 
    userWrapper.appendChild(userAudio);
    audiodiv = document.getElementById("connected_audio")
    audiodiv.appendChild(userWrapper);
}

let createPeerConnection = async (userId) => {
    peerConnection = new RTCPeerConnection(servers);
    console.log("created peer connection with ", userId)
    remoteStream = new MediaStream();
    peers.set(userId,peerConnection);
    console.log("peers before: ",peers)
    await addAudioPeer(userId);
    document.getElementById(`audio_user${userId}`).srcObject = remoteStream;

    localStream.getTracks().forEach(track => {
        peers.get(userId).addTrack(track, localStream);
    });
    

    peers.get(userId).ontrack = (event) =>{
        event.streams[0].getTracks().forEach(track =>{
            remoteStream.addTrack(track);
        })
    }

    await console.log("ice candidates section:")
    peers.get(userId).onicecandidate = async (event) => {
        if (event.candidate)
            {
                console.log(event.candidate);
                sendActionSocket("ice",event.candidate)
            }
    }
    
}

let createOffer = async (userId) => {
    await createPeerConnection(userId);
    let offer = await peers.get(userId).createOffer()
    await peers.get(userId).setLocalDescription(offer);
    await console.log(offer);
    sendActionSocket("offer",{"sdp":offer})

}

let createAnswer = async (userId, offer) =>{
    await createPeerConnection(userId);
    await peers.get(userId).setRemoteDescription(offer);
    let answer = await peers.get(userId).createAnswer();
    await console.log("CREATING ANSWER" ,answer);
    await peers.get(userId).setLocalDescription(answer);
    sendActionSocket("answer",{"sdp":answer, "to":userId})
}

let user_disconnect = (userId) =>
{
    console.log("somebody leaves! it's ",userId);
    console.log("all pears: ",peers);
    peers.get(userId).close()
    peers.delete(userId);
    console.log("closed peer connection with user ", userId);
}



btnConnect.addEventListener('click', function(){
    createOffer(myuserId);
    btnConnect.disabled = true;
    btnDisconnect.disabled = false;
})

btnDisconnect.addEventListener('click', function(){
    console.log("you pushed disconnect")
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