btnConnect.addEventListener('click', async function(){
    btnConnect.disabled = true;
    isConnected = true;
    await initWebRTC(); 
    sendActionSocket("connect",{});
    document.getElementById('toggle_mic').style.display = 'inline-block';
    document.getElementById('toggle_cam').style.display = 'inline-block';
    document.getElementById('disconnect_call').style.display = 'inline-block';
});

btnDisconnect.addEventListener('click', async function() {
    sendActionSocket("user_disconnect",{});
    await cleanup();
});

var isMicMuted = true;
var isCameraOff = false;
var isConnected = false;

let audioTrack = null;
let videoTrack = null;

btnMic.addEventListener('click', function() {
    if (audioTrack) {
        audioTrack.enabled = !isMicMuted;
        isMicMuted = !isMicMuted;
        if (!isMicMuted) {
            btnMic.innerText = "Unmute";
        } else {
            btnMic.innerText = "Mute";
        }
    }
});

btnCam.addEventListener('click', function() {
    if (videoTrack) {
        videoTrack.enabled = !isCameraOff;
        isCameraOff = !isCameraOff;
        if (isCameraOff) {
            btnCam.innerText = "Camera off";
            sendActionSocket("user_camera", {"enabled": true});
            showLocalVideo(true);
        } else {
            btnCam.innerText = "Camera on";
            sendActionSocket("user_camera", {"enabled": false});
            showLocalVideo(false);
        }
    }
});

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
        audioTrack = localStream.getAudioTracks()[0];
        videoTrack = localStream.getVideoTracks()[0];
        videoTrack.enabled = false;
    } catch (error) {
        console.error("Error accessing media devices:", error);
    }
}

function showLocalVideo(status) {
    const localVideoContainer = document.getElementById('local-video-container');
    localVideoContainer.innerHTML = ''; // Очищаем контейнер
    if (status)
    {
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
        console.log(event.streams[0]);
        if (event.track.kind === 'audio') {
            handleAudioTrack(event.streams[0], remoteUserId);
        } else if (event.track.kind === 'video') {
            handleVideoTrack(event.streams[0], remoteUserId, event.track.enabled);
        }
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

async function renderVideo(userId) {
}

function handleAudioTrack(stream, peerId) {
    const remoteAudio = document.createElement('audio');
    remoteAudio.id = `remote-audio-${peerId}`;
    remoteAudio.srcObject = stream;
    remoteAudio.autoplay = true;
    document.getElementById('remote-media-container').appendChild(remoteAudio);
    
    console.log(`Аудио обработано для пира: ${peerId}`);
}

function handleVideoTrack(stream, peerId, status) {
    const remoteVideo = document.createElement('video');
    remoteVideo.id = `remote-video-${peerId}`;
    remoteVideo.srcObject = stream;
    remoteVideo.autoplay = true;
    if (status)
    {
        remoteVideo.style.display = 'none';
    }
    document.getElementById('remote-media-container').appendChild(remoteVideo);
    
    console.log(`Видео обработано для пира: ${peerId}`);
}

function handleUserLeft(userId) {
    console.log(`Cleaning up connection for user: ${userId}`);
    if (peerConnections[userId]) {
        peerConnections[userId].close();
        delete peerConnections[userId];
    }

    const remoteVideo = document.getElementById(`remote-video-${userId}`);
    if (remoteVideo) {
        remoteVideo.remove();
    }
    const remoteAudio = document.getElementById(`remote-audio-${userId}`);
    if (remoteAudio) {
        remoteAudio.remove();
    }

    const userElement = document.getElementById(`user-${userId}`);
    if (userElement) {
        userElement.remove();
    }
}

async function cleanup() {
    console.log('Running cleanup...');

    // Close all peer connections
    for (const userId in peerConnections) {
        if (peerConnections[userId]) {
            peerConnections[userId].close();
        }
    }
    peerConnections = {};

    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }

    const localVideo = document.getElementById('local-video');
    if (localVideo) {
        localVideo.remove();
    }
    
    const remoteMediaContainer = document.getElementById('remote-media-container');
    if (remoteMediaContainer) {
        remoteMediaContainer.innerHTML = '';
    }

    const voiceParticipantsContainer = document.getElementById('voice_participants');
    if (voiceParticipantsContainer) {
        voiceParticipantsContainer.innerHTML = '';
    }

    btnConnect.disabled = false;
    isConnected = false;
    console.log('Cleanup complete.');
}