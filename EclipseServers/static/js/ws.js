
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

const chatSocket = new WebSocket(protocol + window.location.host + '/ws/server/' + serverId + '/')
chatSocket.onopen(event=>{
    
})