import os
import sys
import wave
from datetime import datetime
from threading import Thread
from time import sleep

import paramiko
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

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


'''class Ftp(FTP):
    def __init__(self, ip="188.116.36.112"):
        super(Ftp, self).__init__(ip)

    def ftp_upload(self, path):
        """
        Функция для загрузки файлов на FTP-сервер
        @param ftp_obj: Объект протокола передачи файлов
        @param path: Путь к файлу для загрузки
        """
        print(path, 100000)
        self.storbinary('STOR ' + path, open(path, 'rb'), 1024)

    def cdTree(self, currentDir):
        print(currentDir, "TESTTTTT")
        if currentDir != "":
            try:
                self.cwd(currentDir)

            except BaseException:
                print(currentDir)
                self.cdTree("/".join(currentDir.split("/")[:-1]))
                self.mkd(currentDir)
                self.cwd(currentDir)'''


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

    def getAudio(self):
        while True:
            print("start 2")
            frames = []

            for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                data = self.stream.read(self.CHUNK)
                frames.append(data)
            Thread(target=self.save, args=(frames, )).start()

    def setPath(self, path):
        print(path, 0)
        self.ftpPath = path
        self.path = __PATH__+path

    def setName(self, name):
        self.name = name

    def save(self, frames):
        print(f"{self.path}/{self.name}", 11111111)
        sleep(1)
        wf = wave.open(f"{self.path}/{self.name}", 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        Thread(target=sftp.put, args=(f"{self.path}/{self.name}", f"/home/ftp/uploads/{self.ftpPath}/{self.name}")).start()


class GeneratorFoldersAndFails:
    def __init__(self, path="Data"):
        self.path = __PATH__

    def createFolder(self, name: str, newPath=False):
        try:
            mkdir_p("/home/ftp/uploads/"+name)

            os.makedirs(self.path+"/"+name)
        except BaseException as e:
            print(e)

    def createMp3Fail(self, name: str):
        open(self.path+"/"+name, "w")

    def setPath(self, path):
        self.path = "Data/"+path
        self.createFolder("")


class Date(QThread):
    year = pyqtSignal(str)
    month = pyqtSignal(str)
    day = pyqtSignal(str)
    hour = pyqtSignal(str)
    minute = pyqtSignal(str)
    path = pyqtSignal(str)
    nameFail = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def upData(self):
        def year_(self):
            self.year__ = str(self.dateDatetime.strftime("%Y"))

        def month_(self):
            self.month__ = str(self.dateDatetime.strftime("%m"))

        def day_(self):
            self.day__ = str(self.dateDatetime.strftime("%d"))

        def hour_(self):
            self.hour__ = str(self.dateDatetime.strftime("%H"))

        def minute_(self):
            self.minute__ = str(self.dateDatetime.strftime("%M"))

        def upDatetime(self):
            while True:
                sleep(__WAITING_TIME__)
                self.dateDatetime = datetime.now()

                day_(self)
                year_(self)
                month_(self)
                minute_(self)
                hour_(self)
                print(f"{self.year__}/{self.month__}/{self.day__}")
                self.path.emit(f"{self.year__}/{self.month__}/{self.day__}")

                self.nameFail.emit(f"{self.hour__}_{self.minute__}")

        upDatetime(self)

    def run(self):
        print("------------start--------------")

        self.upData()


if __name__ == '__main__':

    #print(a.cdTree("2021/06/10"))

    app = QApplication([])

    mic = Microphone()
    creator = GeneratorFoldersAndFails()
    testCl = Date()

    testCl.path.connect(creator.setPath)
    testCl.path.connect(mic.setPath)

    testCl.nameFail.connect(lambda e: mic.setName(e+".wav"))
    testCl.start()
    Thread(target=mic.getAudio, args=()).start()

    sys.exit(app.exec_())
