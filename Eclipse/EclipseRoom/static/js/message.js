btnSendMessage.addEventListener("click", async function(){
    let content = inMessage.value
    console.log("sending message: ", content)
    sendActionSocket("user_message", content)
    inMessage.value = '';
})

async function renderMessages(){
    try {
        const msgdata = await fetchdata(`${localhost}api/messages/${roomId}/`);

        if (msgdata && Array.isArray(msgdata)) {
            msgdata.forEach(message => {
                renderMessage(message);
            });
        }
    } catch (error) {
        console.error('Error rendering messages:', error);
    }
}


async function renderMessage(e){
    messageContainer.innerHTML += `<div id="message" style="width: max-content; display: block; border: 2px solid black">
            <h3>${e.displayname}</h3>
            <h4>${e.timestamp}</h4>
            <h2>${e.text}</h2>
        </div>`
}

async function fetchdata(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Error status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}