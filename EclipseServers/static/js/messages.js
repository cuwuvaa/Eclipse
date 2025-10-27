function displayMessage(message) {
    const chatMessages = document.getElementById("messages-list");

    chatMessages.innerHTML += `
        <div class="message-wrapper">
            <div class="message-avatar-section">
                <div class="message-avatar-container">
                    <img src="${message.sender.user.avatar}" class="message-avatar" alt="Аватар" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiByeD0iMjAiIGZpbGw9IiM3Mjg5ZGEiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDExQzE0LjIwOTEgMTEgMTYgOS4yMDkxIDE2IDdDMTYgNC43OTA4NiAxNC4yMDkxIDMgMTIgM0M5Ljc5MDg2IDMgOCA0Ljc5MDg2IDggN0M4IDkuMjA5MTQgOS43OTA4NiAxMSAxMiAxMVoiIGZpbGw9IiNGRkYiLz4KPHBhdGggZD0iTTEyIDEzQzguMTMgMTMgNSAxNi4xMyA1IDIwQzUgMjAuNTUyMyA1LjQ0NzcyIDIxIDYgMjFIMThDMTguNTUyMyAyMSAxOSAyMC41NTIzIDE5IDIwQzE5IDE2LjEzIDE1Ljg3IDEzIDEyIDEzWiIgZmlsbD0iI0ZGRiIvPgo8L3N2Zz4KPC9zdmc+'">
                </div>
                <div class="message-content-section">
                    <div class="message-header">
                        <span class="message-username">${message.sender.user.username}</span>
                        <span class="message-timestamp">${new Date(message.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="message-text">${message.content}</div>
                    <div class="message-actions"></div>
                </div>
            </div>
        </div>
    `;
    chatMessages.scrollTop = chatMessages.scrollHeight; 
}
