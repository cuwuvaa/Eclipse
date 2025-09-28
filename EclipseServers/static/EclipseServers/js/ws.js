const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://'; //кода будет ссл будет использоваться вебсокет секьюрд
const chatSocket = new WebSocket(protocol + window.location.host + '/ws/chat/' + serverId + '/')

const chatSubmit = document.querySelector('#chat-message-submit');
const chatInput = document.querySelector('#message-input');
const chatContainer = document.querySelector('#chat-messages')

const serverSideBar = document.querySelector('#server-sidebar')
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');

const voiceUsers = document.getElementById('voice_users');
const onlineCount = document.getElementById('online-count');
let _onlineCount = 0;

disconnectBtn.style="display:none;"
disconnectBtn.disabled=true;

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);

    const timeOptions = { hour: '2-digit', minute: '2-digit', hour12: false };
    const timeString = date.toLocaleTimeString([], timeOptions);

    if (date.toDateString() === now.toDateString()) {
        return `Today at ${timeString}`;
    } else if (date.toDateString() === yesterday.toDateString()) {
        return `Yesterday at ${timeString}`;
    } else {
        const dateOptions = { day: '2-digit', month: '2-digit', year: 'numeric' };
        const dateString = date.toLocaleDateString([], dateOptions);
        return `${dateString}`;
    }
}

chatSocket.onmessage = function(event){
    var data = JSON.parse(event.data);
    console.log(data)
    if(data.type == "chat_message"){
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
    if (data.type == "voice_connection")
        {
            voiceUsers.innerHTML += ` <div id="user${data.user_id}"}>${data.user}</div>`;
            _onlineCount += 1;
            onlineCount.innerHTML = `Онлайн: ${_onlineCount}`;
        }
    if (data.type == "render") {
        for (let user of data.users_connected_voice) {
            console.log(user.username);
            voiceUsers.innerHTML += `<h3>${user.username}</h3><br>`;
        }
        _onlineCount = data.users_connected_voice.length
        onlineCount.innerHTML = `Онлайн: ${_onlineCount}`;
    }
    if (data.type == "voice_disconnection")
        {
            let user_card = document.getElementById(`user${data.user_id}`)
            user_card.remove()
            _onlineCount -= 1;
            onlineCount.innerHTML = `Онлайн: ${_onlineCount}`;
        }
}

chatSubmit.onclick = function (event) {
    const message = chatInput.value;
        try {
            chatSocket.send(JSON.stringify({
                'action':"send_chatmsg",
                'message': message,
            }));
            chatInput.value = '';
        } catch (e) {
            console.error(e);
        }
};

chatInput.onkeydown = function (e) {
    if (e.keyCode === 13) { // enter, return
        chatSubmit.click();
    }
};

