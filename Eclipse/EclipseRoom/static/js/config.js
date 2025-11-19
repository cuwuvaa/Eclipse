const servers = {
    iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun2.l.google.com:19302" },
        {
            urls: "turn:openrelay.metered.ca:80",
            username: "openrelayproject",
            credential: "openrelayproject"
        }
    ]
};

const VIDEO_CONSTRAINTS = {
    width: { ideal: 1280},
    height: { ideal: 720},
    frameRate: { ideal: 15, min: 10, max: 60 },
};

const DEMO_CONSTRAINTS = {
    width: { ideal: 1280},
    height: { ideal: 720},
    frameRate: { ideal: 25, max: 30 },
    cursor: "always",
};

const localhost = window.location.origin + '/';

let debug = true;

let userdata; 