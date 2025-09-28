let voiceSocket

connectBtn.onclick = function (event)
{
    voiceSocket = new WebSocket(protocol + window.location.host + '/ws/voicechat/' + serverId + '/')
    connectBtn.style="display:none;";
    connectBtn.disabled=true;
    disconnectBtn.style=""
    disconnectBtn.disabled=false;

    chatSocket.send(JSON.stringify(
        {
            'action':"voice_connect",
            'message':"sucessfully"
        }));


    voiceSocket.onmessage = function(event)
    {
        var data = JSON.parse(event.data);
        console.log(data)
    }

}

    disconnectBtn.onclick = function (event)
    {
        chatSocket.send(JSON.stringify(
            {
                'action':"voice_disconnect",
                'message':"sucessfully"
            }));
        voiceSocket.close()
    disconnectBtn.style="display:none;";
    disconnectBtn.disabled=true;
    connectBtn.style=""
    connectBtn.disabled=false;
    }

