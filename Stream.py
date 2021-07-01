from flask import Flask, Response, render_template
import pyaudio

app = Flask(__name__, template_folder='.')


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5


audio1 = pyaudio.PyAudio()



def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')
    o += (datasize + 36).to_bytes(4,'little')
    o += bytes("WAVE",'ascii')
    o += bytes("fmt ",'ascii')
    o += (16).to_bytes(4,'little')
    o += (1).to_bytes(2,'little')
    o += (channels).to_bytes(2,'little')
    o += (sampleRate).to_bytes(4,'little')
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')
    o += (bitsPerSample).to_bytes(2,'little')
    o += bytes("data",'ascii')
    o += (datasize).to_bytes(4,'little')
    return o


@app.route('/audio')
def audio():
    # start Recording
    def sound():

        CHUNK = 1024
        sampleRate = 44100
        bitsPerSample = 16
        channels = 2
        wav_header = genHeader(sampleRate, bitsPerSample, channels)

        stream = audio1.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, input_device_index=1,
                        frames_per_buffer=CHUNK)

        first_run = True
        while True:
           if first_run:
               data = wav_header + stream.read(CHUNK)
               first_run = False
           else:
               data = stream.read(CHUNK)
           yield(data)

    return Response(sound())


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True, port=80)