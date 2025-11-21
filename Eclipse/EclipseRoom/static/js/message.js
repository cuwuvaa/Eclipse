btnSendMessage.addEventListener("click", async function(){
    let content = inMessage.value;
    if (content.trim() === '') return; // Do not send empty messages
    
    sendActionSocket("user_message", content);
    clearMessageInput();
});

function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function deleteMessage(messageId){
    fetch(`${localhost}api/rooms/${roomId}/messages/${messageId}/delete/`,{
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        sendActionSocket("delete_message", {"id": messageId});
    })
    .catch(error => console.error('Failed to delete message:', error));
}

function kickUser(userId){
    fetch(`${localhost}api/rooms/${roomId}/users/${userId}/delete/`,{
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        sendActionSocket("kick_user", {"id": userId});
    })
    .catch(error => console.error('Failed to kick user:', error));
}

function changeRole(userId, role) {
    fetch(`${localhost}api/rooms/${roomId}/users/${userId}/role/`,{
        method: 'PATCH',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "role": role })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // The server should broadcast this change, and ws.js will handle the UI update.
    })
    .catch(error => console.error('Failed to change role:', error));
}
