# audio-recorder

## Install packets
```Bash	
sudo apt-get update
```
```Bash	
sudo apt-get install python3-pip git portaudio19-dev ffmpeg python3-pyaudio python3-flask python3-paramiko python3-pydub
```
## Installation
```Bash	
git clone https://github.com/pysashapy/audio-recorder.git
```
```Bash
cd audio-recorder
```
```Bash	
cp coreaudio.service /etc/systemd/system/coreaudio.service
```
```Bash	
systemctl start coreaudio
```
