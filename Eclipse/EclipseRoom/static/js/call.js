btnConnect.addEventListener('click', async function() {
    isConnected = true;
    updateCallButtons(true);
    await initWebRTC();
    sendActionSocket("connect", {});
});

btnDisconnect.addEventListener('click', leaveVoice);

var isMicMuted = false;
var isCameraOff = true;
var isDemoOff = true;
var isConnected = false;

let audioTrack = null;
let videoTrack = null;

btnMic.addEventListener('click', function() {
    if (audioTrack) {
        isMicMuted = !isMicMuted;
        audioTrack.enabled = !isMicMuted;
        updateMicButton(isMicMuted);
    }
});

let newVideoTrack;

btnCam.addEventListener('click', async function() {
    isCameraOff = !isCameraOff;
    updateCamButton(isCameraOff);

    if (!isCameraOff) {
        try {
            newVideoTrack = (await navigator.mediaDevices.getUserMedia({ video: true })).getVideoTracks()[0];
            if (videoTrack) {
                localStream.removeTrack(videoTrack);
            }
            localStream.addTrack(newVideoTrack);
            videoTrack = newVideoTrack; // Update the reference
            
            Object.values(peerConnections).forEach(pc => {
                const sender = pc.getSenders().find(s => s.track?.kind === 'video');
                if (sender) sender.replaceTrack(newVideoTrack);
            });

            showLocalVideo(true);
            sendActionSocket("user_camera", { "enabled": true });

        } catch (error) {
            console.error("Failed to get video track", error);
            isCameraOff = true;
            updateCamButton(isCameraOff);
        }
    } else {
        if (newVideoTrack) {
            newVideoTrack.stop();
            localStream.removeTrack(newVideoTrack);
            videoTrack = null;
        }
        showLocalVideo(false);
        sendActionSocket("user_camera", { "enabled": false });
    }
});


btnDemo.addEventListener("click", async function() {
    isDemoOff = !isDemoOff;
    updateDemoButton(isDemoOff);

    if (!isDemoOff) {
        try {
            const screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: DEMO_CONSTRAINTS,
                audio: false
            });
            const newScreenTrack = screenStream.getVideoTracks()[0];

            if (videoTrack) {
                localStream.removeTrack(videoTrack);
                videoTrack.stop();
            }
            localStream.addTrack(newScreenTrack);
            videoTrack = newScreenTrack;

            for (const pc of Object.values(peerConnections)) {
                const sender = pc.getSenders().find(s => s.track?.kind === 'video');
                if (sender) await sender.replaceTrack(newScreenTrack);
            }

            showLocalVideo(true);
            sendActionSocket("user_camera", { "enabled": true });

            newScreenTrack.onended = stopDemo;

        } catch (err) {
            console.error("Screen share failed:", err);
            isDemoOff = true;
            updateDemoButton(isDemoOff);
        }
    } else {
        stopDemo();
    }
});

function stopDemo() {
    if (videoTrack && videoTrack.readyState === 'live') {
        videoTrack.stop();
    }
    localStream.removeTrack(videoTrack);
    videoTrack = null;
    
    showLocalVideo(false);
    sendActionSocket("user_camera", { "enabled": false });
    
    isDemoOff = true;
    updateDemoButton(isDemoOff);
    // Restore camera if it was on before demo
    if (!isCameraOff) {
        btnCam.click(); 
    }
}


let localStream = null;
let peerConnections = {}; // { user_id: RTCPeerConnection }

async function initWebRTC() {
    updateCamButton(isCameraOff);
    await setupMedia();
}

async function setupMedia() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: true,
        });
        audioTrack = localStream.getAudioTracks()[0];
        videoTrack = localStream.getVideoTracks()[0];
        videoTrack.stop();
        updateMicButton(isMicMuted);
    } catch (error) {
        console.error("Error accessing media devices:", error);
    }
}

async function handleUserJoined(remoteUserId) {
    await createPeerConnection(remoteUserId);
    const offer = await peerConnections[remoteUserId].createOffer();
    await peerConnections[remoteUserId].setLocalDescription(offer);
    sendActionSocket('offer', { "sdp": offer, "to": remoteUserId });
}

async function createPeerConnection(remoteUserId, camera) {
    const pc = new RTCPeerConnection(servers);

    if (localStream) {
        localStream.getTracks().forEach(track => {
            pc.addTrack(track, localStream);
        });
    }

    pc.ontrack = (event) => {
        if (event.track.kind === 'audio') {
            createRemoteAudio(event.streams[0], remoteUserId);
        }
        if (event.track.kind === 'video') {
            createRemoteVideo(event.streams[0], remoteUserId, camera);
        }
    };

    pc.onicecandidate = (event) => {
        if (event.candidate) {
            sendActionSocket('ice_candidate', { "sdp": event.candidate, "to": remoteUserId });
        }
    };
    
    peerConnections[remoteUserId] = pc;
    return pc;
}

async function handleOffer(remoteUserId, offer, camera) {
    await createPeerConnection(remoteUserId, camera);
    await peerConnections[remoteUserId].setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await peerConnections[remoteUserId].createAnswer();
    await peerConnections[remoteUserId].setLocalDescription(answer);
    sendActionSocket('answer', { "sdp": answer, "to": remoteUserId });
}

async function handleAnswer(remoteUserId, answer) {
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

function handleUserLeft(userId) {
    if (peerConnections[userId]) {
        peerConnections[userId].close();
        delete peerConnections[userId];
    }
    removeElementById(`remote-video-${userId}`);
    removeElementById(`remote-audio-${userId}`);
    removeElementById(`user-${userId}`);
}

async function leaveVoice() {
    sendActionSocket("user_disconnect", {});
    await cleanup();
    updateCallButtons(false);
    isCameraOff = true;
    updateCamButton(isCameraOff);
}

async function cleanup() {
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
    
    document.getElementById('remote-media-container').innerHTML = '';
    document.getElementById(`user-${userdata.id}`).remove();

    showLocalVideo(false);
    isConnected = false;
}
