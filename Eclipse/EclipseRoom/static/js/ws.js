console.log("connecting to room: ", roomId);

const ws = new WebSocket(protocol + window.location.host + `/ws/${roomId}/`);;

ws.onerror = function(error) {
    console.error('WebSocket Error: ', error);
    btnConnect.disabled = true;
};

//слушаем вс
ws.onmessage = async function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    if (data.action == "handshake")
        {
            userdata = data.profile;
            console.log(userdata);
            if (data.connected.length != 0)
            {
            let connected_users = await fetchdata(`${localhost}api/rooms/${roomId}/users/bulk/?user_ids=${data.connected}`)
            for (user of connected_users)
            {
                renderUser(user);
            }
        }
        }
    if (data.action == "new_message")
        {
            appendMessage(data.message);
        }
    
    if (data.action == "delete_message")
    {
        document.getElementById(`message-${data.message.id}`).remove()
    }
    if (data.action == "kick_user" && data.message.id == userdata.id)
    {
        window.location.reload();
    }
    if (data.action == 'new_connect'){
        renderUser(data.user)
        if (isConnected && data.user.id != userdata.id)
        {
            await handleUserJoined(data.user.id);
        }
    }
    if (!isConnected && data.action == 'user_disconnect'){
        console.log(data.user.id);
        document.getElementById(`user-${data.user.id}`).remove();
    }
    if (isConnected){
        if (data.action == 'offer'){
            await handleOffer(data.from_user_id, data.pkg, data.camera);
        }
        if (data.action == 'answer'){
            await handleAnswer(data.from_user_id, data.pkg), data.camera;
        }
        if (data.action == 'ice_candidate'){
            await handleICECandidate(data.from_user_id, data.pkg);
        }
        if (data.action == 'user_disconnect'){
            console.log(data.user.id)
            handleUserLeft(data.user.id);
        }
        if (data.action == 'voice_kick')
        {
            console.log(data.id);
            if (data.id != userdata.id)
            {
                console.log("another user was kicked")
                handleUserLeft(data.id);
            }
            else
            {
                console.log("I AM KICKED")
                leaveVoice();
            }
        }
        if (data.action == 'user_camera')
        {
            if (data.user.id === userdata.id) {
                return;
            }

            const remoteVideo = document.getElementById(`remote-video-${data.user.id}`);
            
            if (data.status) {
                if (remoteVideo) {
                    console.log(`Showing video for ${data.user.id}`);
                    remoteVideo.style.display = "block";
                }
            } else { 
                if (remoteVideo) {
                    console.log(`Hiding video for ${data.user.id}`);
                    remoteVideo.style.display = "none";
                }
            }
        }
    }
};
