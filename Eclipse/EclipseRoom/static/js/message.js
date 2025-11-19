btnSendMessage.addEventListener("click", async function(){
    let content = inMessage.value;
    if (content.trim() === '') return; // Do not send empty messages
    
    console.log("sending message: ", content);
    sendActionSocket("user_message", content);
    inMessage.value = '';
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
    headers: 
        {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    }).then(response => {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.text();
    })
    sendActionSocket("delete_message",{"id":messageId});
}

//перенести в другой файл

function kickUser(userId){
    fetch(`${localhost}api/rooms/${roomId}/users/${userId}/delete/`,{
    method: 'DELETE',
    headers: 
        {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    }).then(response => {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.text();
    })
    sendActionSocket("kick_user",{"id":userId});
}

function changeRole(userId,role)
{
    console.log(role);
    fetch(`${localhost}api/rooms/${roomId}/users/${userId}/role/`,{
    method: 'PATCH',
    headers: 
        {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    body: JSON.stringify({  
            "role": role
        })
    }).then(response => {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.text();
    })
}

const redirurl = "https://shpilivili.org/uploads/posts/2021-11/1638014058_1-shpilivili-cc-p-porno-golii-starii-negr-1.jpg"