const currentUrl = window.location.href;
console.log(currentUrl);
const pathSegments = currentUrl.split("/");
pathSegments.pop();
const roomId = pathSegments.pop();
console.log("connecting to room: ", roomId);

let uid;

const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const ws = new WebSocket(protocol + window.location.host + `/ws/${roomId}/`);


//функция для отправки сообщения через вс
function sendActionSocket(action, message) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            'action': action,
            'message': message
        }));
    } else {
        console.warn('WebSocket not open, message not sent:', action);
    }
}

ws.onclose = async function(event) {
    console.log('WebSocket connection closed. Cleaning up.', event);
    await cleanup();
};

ws.onerror = function(error) {
    console.error('WebSocket Error: ', error);
};

//слушаем вс
ws.onmessage = async function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    if (data.action == "voice_users")
        {
            uid = data.me
        }
    if (data.action == "new_message")
        {
            await renderMessage(data.message);
        }
    if (data.action == 'new_connect'){
        renderUser(data.user)
        if (isConnected && data.user.id != uid)
        {
            await handleUserJoined(data.user.id);
        }
    }
    if (isConnected){
        if (data.action == 'offer'){
            await handleOffer(data.from_user_id, data.pkg);
        }
        if (data.action == 'answer'){
            await handleAnswer(data.from_user_id, data.pkg);
        }
        if (data.action == 'ice_candidate'){
            await handleICECandidate(data.from_user_id, data.pkg);
        }
        if (data.action == 'user_disconnect'){
            console.log(data.user.id)
            handleUserLeft(data.user.id);
        }
        if (data.action == 'user_camera')
        {
            if (data.user.id === uid) {
                return; // Don't act on our own messages
            }

            const remoteVideo = document.getElementById(`remote-video-${data.user.id}`);
            
            if (data.status) { // Camera is ON
                if (remoteVideo) {
                    console.log(`Showing video for ${data.user.id}`);
                    remoteVideo.style.display = "block";
                }
                // If remoteVideo doesn't exist, ontrack will handle creating it.
                // We no longer log an error here, which fixes the race condition issue.
            } else { // Camera is OFF
                if (remoteVideo) {
                    console.log(`Hiding video for ${data.user.id}`);
                    remoteVideo.style.display = "none";
                }
            }
        }
    }
};
