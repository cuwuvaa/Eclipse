class Waveform {
    constructor(stream, canvas) {
        this.stream = stream;
        this.canvas = canvas;
        this.canvasCtx = this.canvas.getContext('2d');
        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.audioCtx.createAnalyser();
        this.analyser.fftSize = 256; // Smaller size for less detail, but faster
        this.bufferLength = this.analyser.frequencyBinCount;
        this.dataArray = new Uint8Array(this.bufferLength);

        this.source = this.audioCtx.createMediaStreamSource(this.stream);
        this.source.connect(this.analyser);

        this.draw();
    }

    draw() {
        requestAnimationFrame(() => this.draw());

        this.analyser.getByteFrequencyData(this.dataArray);

        this.canvasCtx.fillStyle = 'rgb(54, 57, 63)';
        this.canvasCtx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        let total = 0;
        for (let i = 0; i < this.bufferLength; i++) {
            total += this.dataArray[i];
        }
        const average = total / this.bufferLength;

        const barHeight = average;
        this.canvasCtx.fillStyle = 'rgb(67, 181, 129)'
        this.canvasCtx.fillRect(0, this.canvas.height - barHeight / 2, this.canvas.width, barHeight / 2);
    }
}