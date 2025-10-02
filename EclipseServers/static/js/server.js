const serverSocket = new WebSocket(protocol + window.location.host + `/ws/server/${serverId}/`)

function sendServerSocket(action,message)
{
    serverSocket.send(JSON.stringify({
        "action":action,
        "message":message
    }))
}

serverSocket.addEventListener('open', ()=>{
    sendServerSocket()
})