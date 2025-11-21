# Поток загрузки страницы комнаты (room.html) - Пошаговый анализ JavaScript
# НА ДАННЫЙ МОМЕНТ НЕ ПРОВЕДЕН РЕФАКТОРИНГ JS
Этот документ описывает порядок выполнения JavaScript-функций при загрузке страницы комнаты, что поможет в рефакторинге и понимании зависимостей.

## 1. Загрузка HTML и определение глобальных переменных DOM

Браузер загружает `room.html`. В процессе загрузки определяются элементы DOM, к которым затем будут обращаться скрипты.

## 2. Загрузка и выполнение JavaScript-файлов (по порядку)

### 2.1. `config.js`
- **Действие:** Определяет глобальные константы и переменные, такие как `servers`, `VIDEO_CONSTRAINTS`, `DEMO_CONSTRAINTS`, `localhost`, `debug`, `userdata`, `currentUrl`, `pathSegments`, `roomId`, `protocol`.
- **Важно:** `userdata` инициализируется без значения и будет заполнена позже через WebSocket. `roomId` и `protocol` также определяются здесь.

### 2.2. `dom.js`
- **Действие:** Получает ссылки на элементы DOM по их `id` и присваивает их глобальным переменным.
- **Примеры:** `btnSendMessage`, `inMessage`, `messageContainer`, `userContainer`, `btnConnect`, `btnDisconnect`, `btnCam`, `btnMic`, `btnDemo`, `membersContainer`.
- **Важно:** Эти переменные становятся доступны для всех последующих скриптов.

### 2.3. `ui.js`
- **Действие:** Определяет глобальные переменные состояния для пагинации сообщений (`nextMessagesUrl`, `isLoadingMessages`). Определяет функции, отвечающие за рендеринг элементов UI и взаимодействие с DOM.
- **Определяемые функции:**
    - `renderUser(e)`: Рендерит пользователя в списке участников голосового чата.
    - `showLocalVideo(status)`: Показывает или скрывает локальное видео.
    - `handleAudioTrack(stream, peerId)`: Создает аудиоэлемент для удаленного пользователя.
    - `handleVideoTrack(stream, peerId, status)`: Создает/обновляет видеоэлемент для удаленного пользователя.
    - `fetchdata(url)`: Асинхронная функция для получения данных по URL.
    - `renderMessages()`: Инициализирует загрузку сообщений и обработчик прокрутки.
    - `handleMessageScroll()`: Обрабатывает событие прокрутки для загрузки старых сообщений.
    - `createMessageHTML(e)`: Генерирует HTML для одного сообщения.
    - `appendMessage(e)`: Добавляет новое сообщение в конец контейнера.
    - `prependMessage(e)`: Добавляет старое сообщение в начало контейнера.
- **Важно:** `topMarker` также определяется здесь, получая ссылку на `<div id="topMarker"></div>` из `room.html`.

### 2.4. `ws.js`
- **Действие:** Инициализирует WebSocket-соединение и определяет обработчики событий WebSocket.
- **Глобальные переменные:** `ws` (объект WebSocket).
- **Определяемые функции:** `sendActionSocket(action, message)` для отправки сообщений через WebSocket.
- **Обработчики событий:**
    - `ws.onerror`: Обрабатывает ошибки WebSocket.
    - `ws.onmessage`: **Основной обработчик входящих сообщений от сервера.**
        - `data.action == "handshake"`: Получает `userdata` (профиль текущего пользователя) и, если есть подключенные пользователи, вызывает `fetchdata` и `renderUser` для их отображения.
        - `data.action == "new_message"`: Вызывает `appendMessage(data.message)` для отображения нового сообщения.
        - `data.action == "delete_message"`: Удаляет сообщение из DOM.
        - `data.action == "kick_user"`: Перенаправляет пользователя, если его кикнули.
        - `data.action == 'new_connect'`: Вызывает `renderUser` и `handleUserJoined` для нового пользователя.
        - `data.action == 'user_disconnect'`: Удаляет пользователя из DOM.
        - `data.action == 'offer'`, `'answer'`, `'ice_candidate'`: Вызывает соответствующие WebRTC-функции (`handleOffer`, `handleAnswer`, `handleICECandidate`).
        - `data.action == 'voice_kick'`: Обрабатывает кик из голосового чата.
        - `data.action == 'user_camera'`: Обновляет видимость видеоэлемента удаленного пользователя.
- **Важно:** `ws.onclose` также должен быть определен здесь для вызова `cleanup()` при закрытии соединения. (В текущем коде он отсутствует, что является ошибкой).

### 2.5. `message.js`
- **Действие:** Определяет обработчик события для кнопки отправки сообщения и вспомогательные функции для работы с сообщениями.
- **Определяемые функции:**
    - `getCSRFToken()`: Получает CSRF-токен из куки.
    - `deleteMessage(messageId)`: Отправляет DELETE-запрос на API для удаления сообщения и оповещает через WebSocket.
    - `kickUser(userId)`: Отправляет DELETE-запрос на API для кика пользователя и оповещает через WebSocket.
    - `changeRole(userId, role)`: Отправляет PATCH-запрос на API для изменения роли пользователя.
- **Обработчики событий:** `btnSendMessage.addEventListener("click", ...)` для отправки текстовых сообщений.

### 2.6. `call.js`
- **Действие:** Определяет основную логику WebRTC, включая инициализацию медиа, управление PeerConnection, обработку SDP/ICE и управление локальным/удаленным видео/аудио.
- **Глобальные переменные:** `isMicMuted`, `isCameraOn`, `isConnected`, `audioTrack`, `videoTrack`, `localStream`, `peerConnections`.
- **Определяемые функции:**
    - `initWebRTC()`: Инициализирует WebRTC.
    - `setupMedia()`: Получает локальные медиапотоки (только аудио по умолчанию).
    - `handleUserJoined(remoteUserId)`: Обрабатывает присоединение нового пользователя.
    - `createPeerConnection(remoteUserId)`: Создает `RTCPeerConnection`.
    - `handleOffer`, `handleAnswer`, `handleICECandidate`: Обрабатывают WebRTC-сигнализацию.
    - `handleUserLeft(userId)`: Очищает ресурсы при уходе пользователя.
    - `leaveVoice()`: Завершает голосовой чат.
    - `cleanup()`: Выполняет полную очистку всех WebRTC-ресурсов.
- **Обработчики событий:**
    - `btnConnect.addEventListener('click', ...)`: Начинает голосовой чат, вызывает `initWebRTC`, `sendActionSocket("connect")`.
    - `btnDisconnect.addEventListener('click', leaveVoice)`: Вызывает `leaveVoice`.
    - `btnMic.addEventListener('click', ...)`: Переключает состояние микрофона.
    - `btnCam.addEventListener('click', ...)`: Переключает состояние камеры, вызывает `getUserMedia` для видео, добавляет/удаляет видеодорожку, вызывает `showLocalVideo`, `sendActionSocket("user_camera")`.
    - `btnDemo.addEventListener('click', ...)`: Обрабатывает демонстрацию экрана.

### 2.7. `init.js`
- **Действие:** Точка входа для инициализации страницы после загрузки всех скриптов.
- **Определяемые функции:** `init()`.
- **Выполнение:**
    - Вызывает `init()`.
    - `init()`:
        - Выполняет `fetch` запрос к `/api/rooms/${roomId}/users/`.
        - Если запрос успешен, через `setTimeout` вызывает `renderMembers()` и `renderMessages()`.
- **Важно:** `renderMembers()` и `renderMessages()` являются функциями из `ui.js`.

## 3. Пошаговый поток выполнения при загрузке страницы

1.  **Загрузка `config.js`:** Определяются глобальные константы (`servers`, `localhost`, `roomId`, `protocol` и т.д.).
2.  **Загрузка `dom.js`:** Получаются ссылки на элементы DOM (`btnSendMessage`, `messageContainer`, `btnConnect` и т.д.).
3.  **Загрузка `ui.js`:** Определяются глобальные переменные состояния для пагинации (`nextMessagesUrl`), а также все функции рендеринга (`renderUser`, `showLocalVideo`, `handleAudioTrack`, `handleVideoTrack`, `fetchdata`, `renderMessages`, `handleMessageScroll`, `createMessageHTML`, `appendMessage`, `prependMessage`). `topMarker` получает ссылку на элемент DOM.
4.  **Загрузка `ws.js`:** Инициализируется WebSocket-соединение (`ws = new WebSocket(...)`). Определяются `sendActionSocket`, `ws.onerror`, `ws.onmessage`.
5.  **Загрузка `message.js`:** Определяются `getCSRFToken`, `deleteMessage`, `kickUser`, `changeRole`. Устанавливается обработчик `btnSendMessage.addEventListener("click", ...)`.
6.  **Загрузка `call.js`:** Определяются глобальные переменные состояния WebRTC (`isMicMuted`, `isCameraOn`, `isConnected`, `audioTrack`, `videoTrack`, `localStream`, `peerConnections`). Определяются все WebRTC-функции (`initWebRTC`, `setupMedia`, `handleUserJoined`, `createPeerConnection`, `handleOffer`, `handleAnswer`, `handleICECandidate`, `handleUserLeft`, `leaveVoice`, `cleanup`). Устанавливаются обработчики событий для кнопок голосового чата (`btnConnect`, `btnDisconnect`, `btnMic`, `btnCam`, `btnDemo`).
7.  **Загрузка `init.js`:**
    - Вызывается функция `init()`.
    - `init()` выполняет `fetch` запрос к `/api/rooms/${roomId}/users/`.
    - После успешного получения данных (или ошибки 403), через 1 секунду (`setTimeout`):
        - Вызывается `renderMembers()` (из `ui.js`).
        - Вызывается `renderMessages()` (из `ui.js`).

### 3.1. Детали выполнения `renderMembers()` (из `ui.js`)
- Вызывает `fetchdata(`${localhost}api/rooms/${roomId}/users/`)`.
- После получения данных, итерируется по `roomUsers`.
- Для каждого `element` (пользователя в комнате):
    - Создает `div` (`memberdiv`) и `h1` (`membername`).
    - Добавляет `membername` в `memberdiv`.
    - Добавляет `memberdiv` в `membersContainer`.
    - Если `element.user === userdata.user`, добавляет `(You)` к имени.
    - Добавляет `<h2>role: ${element.role}</h1>`.
    - В зависимости от `userdata.role` (текущего пользователя):
        - Если `creator`: добавляет кнопки "kick" и "change role".
        - Если `moderator`: добавляет кнопку "kick" (если цель не "creator").

### 3.2. Детали выполнения `renderMessages()` (из `ui.js`)
- Очищает `messageContainer.innerHTML` и добавляет `topMarker`.
- Вызывает `fetchdata(`${localhost}api/rooms/${roomId}/messages/`)`.
- После получения данных:
    - Сохраняет `data.next` в `nextMessagesUrl`.
    - Итерируется по `data.results` (сообщениям, в обратном порядке).
    - Для каждого `message` вызывает `appendMessage(message)`.
    - Устанавливает `messageContainer.scrollTop = messageContainer.scrollHeight` (прокручивает вниз).
    - Создает `IntersectionObserver` для `topMarker`.
    - Начинает наблюдение за `topMarker`.

### 3.3. Детали выполнения `appendMessage(message)` (из `ui.js`)
- Вызывает `createMessageHTML(message)`.
- Вставляет полученный HTML в `messageContainer` с помощью `insertAdjacentHTML('afterbegin', ...)`.

### 3.4. Детали выполнения `createMessageHTML(e)` (из `ui.js`)
- Генерирует HTML для сообщения, включая кнопки "delete" в зависимости от роли текущего пользователя (`userdata.role`) и отправителя сообщения.

## 4. Дальнейшие действия (после загрузки)

- **WebSocket `ws.onmessage`:** Продолжает слушать сообщения от сервера и реагировать на них (новые сообщения, изменения статуса камеры, WebRTC-сигнализация и т.д.).
- **Прокрутка сообщений:** Когда `topMarker` становится видимым (пользователь прокручивает вверх), `IntersectionObserver` вызывает `handleMessageScroll()`.
    - `handleMessageScroll()`:
        - Вызывает `fetchdata(nextMessagesUrl)`.
        - После получения данных, итерируется по `data.results` (старым сообщениям).
        - Для каждого `message` вызывает `prependMessage(message)`.
        - Перемещает `topMarker` в конец `messageContainer` (`messageContainer.appendChild(topMarker)`).
- **Кнопки голосового чата:**
    - `btnConnect`: Вызывает `initWebRTC()`, `setupMedia()` (получает только аудио), `sendActionSocket("connect")`.
    - `btnCam`: Вызывает `getUserMedia({video: true})` для получения видео, добавляет/удаляет видеодорожку, вызывает `showLocalVideo`, `sendActionSocket("user_camera")`.
    - `btnDemo`: Вызывает `navigator.mediaDevices.getDisplayMedia` для демонстрации экрана.

---
Надеюсь, этот подробный анализ поможет вам в рефакторинге!
