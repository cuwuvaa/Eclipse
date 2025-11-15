var isConnected = false;

btnConnect.addEventListener('click', async function(){
    btnConnect.disabled = true;
    isConnected = true;
    await initWebRTC(); 
    sendActionSocket("connect",{});
});

btnDisconnect.addEventListener('click', async function() {
    sendActionSocket("disconnect",{});
    await cleanup()
})

async function renderUser(e) {
    const userContainer = document.getElementById('voice_participants');
    if (userContainer) {
        const userElement = document.createElement('h1');
        userElement.textContent = e.username || e.displayname;
        userElement.id = `user-${e.id}`;
        userContainer.appendChild(userElement);
    }
}

let localStream = null;
let peerConnections = {}; // { user_id: RTCPeerConnection }


async function initWebRTC() {
    await setupMedia();
}

async function setupMedia() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: true,
        });
        console.log("Microphone & video access granted");
        const localVideo = document.createElement('video');
        localVideo.srcObject = localStream;
        localVideo.autoplay = true;
        localVideo.muted = true;
        localVideo.id = 'local-video';
        document.getElementById('local-video-container').appendChild(localVideo);
    } catch (error) {
        console.error("Error accessing media devices:", error);
    }
}

async function handleUserJoined(remoteUserId) {
    console.log(`New user joined: ${remoteUserId}`);
    await createPeerConnection(remoteUserId);
    
    const offer = await peerConnections[remoteUserId].createOffer();
    await peerConnections[remoteUserId].setLocalDescription(offer);
    
    sendActionSocket('offer', {"sdp":offer, "to":remoteUserId});
}

async function createPeerConnection(remoteUserId) {
    const pc = new RTCPeerConnection(servers);

    if (localStream) {
        localStream.getTracks().forEach(track => {
            pc.addTrack(track, localStream);
        });
    }

    pc.ontrack = (event) => {
        console.log(`Received remote stream from ${remoteUserId}`);
        handleRemoteStream(remoteUserId, event.streams[0]);
    };

    pc.onicecandidate = (event) => {
        if (event.candidate) {
            sendActionSocket('ice_candidate',{"sdp":event.candidate, "to":remoteUserId});
        }
    };

    pc.onconnectionstatechange = () => {
        console.log(`Connection with ${remoteUserId}: ${pc.connectionState}`);
    };

    peerConnections[remoteUserId] = pc;
    return pc;
}

async function handleOffer(remoteUserId, offer) {
    console.log(`Received offer from ${remoteUserId}`);
    
    await createPeerConnection(remoteUserId);
    await peerConnections[remoteUserId].setRemoteDescription(new RTCSessionDescription(offer));
    
    const answer = await peerConnections[remoteUserId].createAnswer();
    await peerConnections[remoteUserId].setLocalDescription(answer);
    
    sendActionSocket('answer', {"sdp":answer, "to":remoteUserId});
}

async function handleAnswer(remoteUserId, answer) {
    console.log(`Received answer from ${remoteUserId}`);
    const pc = peerConnections[remoteUserId];
    if (pc) {
        await pc.setRemoteDescription(new RTCSessionDescription(answer));
    }
}

async function handleICECandidate(remoteUserId, candidate) {
    const pc = peerConnections[remoteUserId];
    if (pc) {
        try {
            await pc.addIceCandidate(new RTCIceCandidate(candidate));
        } catch (e) {
            console.error('Error adding received ice candidate', e);
        }
    }
}

function handleRemoteStream(userId, stream) {
    if (document.getElementById(`remote-video-${userId}`)) {
        return;
    }
    const remoteVideo = document.createElement('video');
    remoteVideo.srcObject = stream;
    remoteVideo.autoplay = true;
    remoteVideo.id = `remote-video-${userId}`;
    document.getElementById('remote-media-container').appendChild(remoteVideo);
}

function handleUserLeft(userId)
{
    peerConnections[userId].close()
    delete peerConnections[userId]
    document.getElementById(`remote-video-${userId}`).remove();
}

async function cleanup(){
    // Close all peer connections                                                      
    for (const userId in peerConnections) {                                            
        peerConnections[userId].close();                                               
    }                                                                                  
    peerConnections = {};                                                              
                                                                                       
    // Stop local media stream                                                         
    if (localStream) {                                                                 
        localStream.getTracks().forEach(track => track.stop());                        
        localStream = null;                                                            
    }                                                                                  
                                                                                       
    // Remove local video                                                              
    const localVideo = document.getElementById('local-video');                         
    if (localVideo) {                                                                  
        localVideo.remove();                                                           
    }                                                                                  
                                                                                       
    // Reset UI                                                                        
    btnConnect.disabled = false;                                                       
    isConnected = false;                                                                       
}                                                                                      