# audio-recorder

## Install packets
```Bash	
sudo apt-get install python3-pip git portaudio19-dev 
python3 -m pip install pyaudio flask paramiko pydub
```
## InstallationCancel changes
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
