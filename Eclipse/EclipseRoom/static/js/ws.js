const ws = new WebSocket(protocol + window.location.host + `/ws/${roomId}/`);

let handshakeResolver;
const handshakePromise = new Promise(resolve => {
    handshakeResolver = resolve;
});


ws.onerror = function(error) {
    console.error('WebSocket Error: ', error);
    // Disable connect button as we can't establish a connection
    btnConnect.disabled = true;
};

ws.onmessage = async function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);

    // The first message should always be the handshake
    if (data.action === "handshake") {
        userdata = data.profile;
        console.log("Handshake successful. Userdata received:", userdata);
        handshakeResolver(data); // Resolve the promise so init() can continue
    }


    switch (data.action) {
        case "handshake":
            // The promise is resolved above, but we can handle other handshake data here
            if (data.connected && data.connected.length > 0) {
                const connectedUsers = await fetchdata(`${localhost}api/rooms/${roomId}/users/bulk/?user_ids=${data.connected}`);
                if (connectedUsers) {
                    for (const user of connectedUsers) {
                        renderUser(user);
                    }
                }
            }
            break;

        case "new_message":
            prependMessage(data.message);
            break;

        case "delete_message":
            removeElementById(`message-${data.message.id}`);
            break;
        
        case "user_update":
            updateUser(data.user, true);
            break;

        case "kick_user":
            if (data.message.id === userdata.id) {
                alert("You have been kicked from the room.");
                reloadPage();
            } else {
                removeElementById(`profile-${data.message.id}`);
            }
            break;

        case 'new_connect':
            renderUser(data.user);
            if (isConnected && data.user.id !== userdata.id) {
                await handleUserJoined(data.user.id);
            }
            break;

        case 'user_disconnect':
            if (isConnected) {
                handleUserLeft(data.user.id);
            } else {
                removeElementById(`user-${data.user.id}`);
            }
            updateUser(data.user,false);
            break;

        case 'offer':
            if (isConnected) await handleOffer(data.from_user_id, data.pkg, data.camera);
            break;

        case 'answer':
            if (isConnected) await handleAnswer(data.from_user_id, data.pkg);
            break;

        case 'ice_candidate':
            if (isConnected) await handleICECandidate(data.from_user_id, data.pkg);
            break;

        case 'voice_kick':
            if (data.id === userdata.id) {
                console.log("I WAS KICKED FROM VOICE");
                leaveVoice();
            } else {
                console.log("Another user was kicked from voice");
                handleUserLeft(data.id);
            }
            break;

        case 'user_camera':
            if (data.user.id !== userdata.id) {
                toggleRemoteVideo(data.user.id, data.status);
            }
            break;
    }
};

ws.onclose = function() {
    console.log('WebSocket connection closed.');
    if (isConnected) {
        cleanup();
    }
    btnConnect.disabled = true;
    btnSendMessage.disabled = true;
};