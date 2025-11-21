

async function init() {
    const response = await fetch(`${localhost}api/rooms/${roomId}/users/`);
    if (response.status === 403) {
        console.log("join server!");
        return
    };

    setTimeout(() => {
    renderMembers();
    renderMessages();
    }, 1000);


}

init();

