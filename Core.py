import os
import wave
from datetime import datetime
from threading import Thread
from flask import Flask, Response, render_template
import paramiko
import pyaudio
import pydub

__NAME_FTP_PATH__ = "TEST"
__PATH__ = "Data/"
__WAITING_TIME__ = 60*10

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("188.116.36.112", username="root", password="N6c4d3MY14Soe5MzRi")
sftp = client.open_sftp()


def mkdir_p(remote_directory):
    if remote_directory == '/':
        sftp.chdir('/')
        return
    if remote_directory == '':
        return
    try:
        sftp.chdir(remote_directory)
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(dirname)
        sftp.mkdir(basename)
        sftp.chdir(basename)
        return True


class Microphone:
    CHUNK = 1024
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = __WAITING_TIME__
    FORMAT = pyaudio.paInt16

    data = None
    path = None
    ftpPath = None
    name = None

    def __init__(self):
        self.getPyAudio()

    def getPyAudio(self):
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        print("[INFO] YES GetPyAudio")

    def getAudio(self):
        Thread(target=self.server, args=()).start()
        while True:
            frames = []
            time_ = datetime.now()
            for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                self.data = self.stream.read(self.CHUNK)
                frames.append(self.data)
            Thread(target=self.save, args=(frames, time_, )).start()

    def server(self):
        app = Flask(__name__, template_folder='.')

        def genHeader(sampleRate, bitsPerSample, channels):
            datasize = 2000 * 10 ** 6
            o = bytes("RIFF", 'ascii')
            o += (datasize + 36).to_bytes(4, 'little')
            o += bytes("WAVE", 'ascii')
            o += bytes("fmt ", 'ascii')
            o += (16).to_bytes(4, 'little')
            o += (1).to_bytes(2, 'little')
            o += (channels).to_bytes(2, 'little')
            o += (sampleRate).to_bytes(4, 'little')
            o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4, 'little')
            o += (channels * bitsPerSample // 8).to_bytes(2, 'little')
            o += (bitsPerSample).to_bytes(2, 'little')
            o += bytes("data", 'ascii')
            o += (datasize).to_bytes(4, 'little')
            return o

        @app.route('/audio')
        def audio():
            # start Recording
            def sound():
                sampleRate = 44100
                bitsPerSample = 16
                channels = 2
                wav_header = genHeader(sampleRate, bitsPerSample, channels)

                lastData = None
                first_run = True
                while True:
                    if lastData != self.data:
                        if first_run:
                            data = wav_header + self.data
                            first_run = False
                        else:
                            data = self.data
                        lastData = self.data
                        yield (data)

            return Response(sound())

        @app.route('/')
        def index():
            """Video streaming home page."""
            return render_template('index.html')

        app.run(host='0.0.0.0', threaded=True, port=80)

    def save(self, frames, time):
        print("[INFO] YES getAudio")
        name = time.strftime("%H_%M.wav")
        namemp3 =  time.strftime("%H_%M.mp3")
        path = time.strftime("%Y/%m/%d/")
        mkdir_p(f"/home/ftp/{__NAME_FTP_PATH__}/uploads/" + path)
        try:
            os.makedirs(__PATH__ + path)
        except BaseException:
            pass
        print(1)
        wf = wave.open(__PATH__ + path + name, 'wb')
        print("-----save-----")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print("-----uploads-----")
        sound = pydub.AudioSegment.from_wav(__PATH__ + path + name)
        sound.export(__PATH__ + path + namemp3, format="mp3")
        os.remove(__PATH__ + path + name)
        Thread(target=sftp.put, args=(__PATH__ + path + namemp3, "/home/ftp/uploads/" + path + namemp3)).start()


if __name__ == '__main__':
    mic = Microphone()
    Thread(target=mic.getAudio, args=()).start()

