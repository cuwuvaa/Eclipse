async function init() {
    try {
        console.log("Waiting for handshake...");
        await handshakePromise;
        console.log("Handshake complete, proceeding with initialization.");
        
        await renderMembers();
        await renderMessages();

        console.log("Initialization complete.");

    } catch (error) {
        console.error("Initialization failed:", error);
    }
}

init();