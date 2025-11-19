btnConnect.addEventListener('click', async function(){
    btnConnect.disabled = true;
    isConnected = true;
    await initWebRTC(); 
    sendActionSocket("connect",{});
    btnConnect.style.display = 'none';
    document.getElementById('toggle_mic').style.display = 'inline-block';
    document.getElementById('toggle_cam').style.display = 'inline-block';
    document.getElementById('disconnect_call').style.display = 'inline-block';
    btnDemo.style.display = 'inline-block';
});

btnDisconnect.addEventListener('click', leaveVoice);


// БЛЯ ВЕСЬ КОД РЕАЛЬНО НАДО РЕФАКТОРИТЬ, А ТО ЭТО ПИЗДЕЦ ПОЛНЫЙ (ЛЮДИ ПРОСТИТЕ РЕАЛЬНО)
var isMicMuted = true;
var isCameraOff = false;
var isDemoOff = false;
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

let newVideoTrack;

btnCam.addEventListener('click', async function() {
    if (videoTrack) {
        videoTrack.enabled = !isCameraOff;
        isCameraOff = !isCameraOff;
        if (isCameraOff) {
            btnCam.innerText = "Camera off";
            sendActionSocket("user_camera", {"enabled": true});
            newVideoTrack = (await navigator.mediaDevices.getUserMedia({ video: true })).getVideoTracks()[0];
            localStream.removeTrack(videoTrack);
            localStream.addTrack(newVideoTrack);
            showLocalVideo(true);
            Object.values(peerConnections).forEach(pc => {
                const sender = pc.getSenders().find(s => s.track?.kind === 'video');
                if (sender) sender.replaceTrack(newVideoTrack);
        });
        } else {
            btnCam.innerText = "Camera on";
            newVideoTrack.stop();
            localStream.removeTrack(newVideoTrack);
            sendActionSocket("user_camera", {"enabled": false});
            showLocalVideo(false);
        }
    }
});

btnDemo.addEventListener("click", async function () {
    try {
        if (!isDemoOff)
        {
            isDemoOff = !isDemoOff
            const screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: DEMO_CONSTRAINTS,
                audio: false
            });

            const newScreenTrack = screenStream.getVideoTracks()[0];
            if (!newScreenTrack) throw new Error("No video track from screen share");

            localStream.getVideoTracks().forEach(track => {
                localStream.removeTrack(track);
                track.stop();
            });

            localStream.addTrack(newScreenTrack);

            for (const pc of Object.values(peerConnections)) {
                const sender = pc.getSenders().find(s => s.track?.kind === 'video');
                if (sender) {
                    await sender.replaceTrack(newScreenTrack);
                }
            }

            videoTrack = newScreenTrack;

            showLocalVideo(true);
            btnDemo.innerText = "Stop Screen Share";
            sendActionSocket("user_camera", {"enabled": true});

            newScreenTrack.onended = () => {
                console.log("Screen share ended by user");
                stopDemo();
            };
        }
        else
        {   
            stopDemo();
        }
    } catch (err) {
        console.error("Screen share failed:", err);
        alert("Не удалось начать демонстрацию экрана");
    }
    
})

function stopDemo()
{
    btnDemo.innerText = "Screen on";
    sendActionSocket("user_camera", {"enabled": false});
    localStream.getVideoTracks().forEach(track => {
    localStream.removeTrack(track);
        track.stop();
    });
    showLocalVideo(false);
    isDemoOff = !isDemoOff
}

let localStream = null;
let peerConnections = {}; // { user_id: RTCPeerConnection }

async function initWebRTC() {
    btnCam.innerText = "Camera on";
    await setupMedia();
}

async function setupMedia() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: VIDEO_CONSTRAINTS,
        });
        console.log("Microphone & video access granted");
        audioTrack = localStream.getAudioTracks()[0];
        videoTrack = localStream.getVideoTracks()[0];
        videoTrack.stop();
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

async function createPeerConnection(remoteUserId, camera) {

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
        }if (event.track.kind === 'video') {
            handleVideoTrack(event.streams[0], remoteUserId, camera);
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

async function handleOffer(remoteUserId, offer, camera) {
    console.log(`Received offer from ${remoteUserId}`);
    
    await createPeerConnection(remoteUserId, camera);
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
    if (!status)
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

async function leaveVoice(){

    sendActionSocket("user_disconnect",{});
    await cleanup();
    btnConnect.style.display = 'inline-block';
    document.getElementById('toggle_mic').style.display = 'none';
    document.getElementById('toggle_cam').style.display = 'none';
    document.getElementById('disconnect_call').style.display = 'none';
    btnConnect.disabled = false;
    isCameraOff = false;
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
    
    const remoteMediaContainer = document.getElementById('remote-media-container');
    if (remoteMediaContainer) {
        remoteMediaContainer.innerHTML = '';
    }

    document.getElementById(`user-${userdata.id}`).remove();
    showLocalVideo(false);
    isConnected = false;
    console.log('Cleanup complete.');
}