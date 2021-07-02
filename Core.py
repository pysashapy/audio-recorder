import os
import wave
from datetime import datetime
from threading import Thread

import paramiko
import pyaudio

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
        mkdir_p(sftp, dirname)
        sftp.mkdir(basename)
        sftp.chdir(basename)
        return True


class Microphone:
    CHUNK = 1024
    WIDTH = 2
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = __WAITING_TIME__
    FORMAT = pyaudio.paInt16

    path = None
    ftpPath = None
    name = None

    def __init__(self):
        self.getPyAudio()

    def getPyAudio(self):
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.p.get_format_from_width(self.WIDTH),
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        output=True,
                        frames_per_buffer=self.CHUNK)
        print("[INFO] YES GetPyAudio")
    def getAudio(self):
        while True:
            frames = []
            time_ = datetime.now()

            for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = self.stream.read(self.CHUNK)
                frames.append(data)
            print("[INFO] YES getAudio")

            Thread(target=self.save, args=(frames, time_, )).start()

    def save(self, frames, time):
        print("[INFO] YES getAudio")
        name = time.strftime("%H_%M.wav")
        path = time.strftime("%Y/%m/%d/")
        mkdir_p("/home/ftp/uploads/" + path)
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
        Thread(target=sftp.put, args=(__PATH__ + path + name, "/home/ftp/uploads/" + path + name)).start()


if __name__ == '__main__':
    mic = Microphone()
    Thread(target=mic.getAudio, args=()).start()

