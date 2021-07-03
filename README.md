# audio-recorder

## Install packets
```Bash	
sudo apt-get update && apt upgrade -y
sudo apt-get install python3-flask python3-pyaudio python3-paramiko git
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
cp streamaudio.service /etc/systemd/system/streamaudio.service
```
