# NBSM

Ein Python3 Script um den 'Landis + Gyr E450' Smartmeter auszulesen. 

## Description

Entwickelt für den Smart Meter von Netz Burgenland, in diesem Repository angepasst für die Wiener Netze. Für das Projekt benutze ich einen optischen Lesekopf von Weidmann Elektronik (https://amzn.to/39XEpme), der mit USB angeschlossen ist. Kabelgebundene Leser (Über RJ12) sollten mit wenig Aufwand ebenso funktionieren.

## Getting Started

### Dependencies

* Libraries installieren:
```
pip3 install pycryptodome
pip3 install pycryptodomex
pip3 install pyserial
```

Wenn im MQTT Modus gestartet werden soll, ist zusätzlich noch das Paket 'paho-mqtt' notwendig:
```
pip3 install paho-mqtt
```
* Konfiguration kann über ein Config-File (.nbsm, /etc/nbsm.conf) oder Kommandozeilen-Parameter gesetzt werden. Details erfährt man mit `./nbsm.py -h`

### Executing program

Der Smartmeter sendet ca. alle 10 Sekunden Daten. Die Daten werden je nach Modus entweder an stdout als json ausgegeben (--mode stdout), als json an einen http endpoint gesendet (--mode json) oder an einen mqtt server weitergereicht (--mode mqtt)
```
# stdout modus:
python3 nbsm.py --mode stdout

# json endpoint modus:
python3 nbsm.py --mode json

# mqtt server
python3 nbsm.py --mode mqtt
```

## Support

Diskussionen werden im Photovoltaikforum geführt:
* [Photovoltaikforum](https://www.photovoltaikforum.com/thread/128724-landis-gyr-e450-%C3%BCber-vz-logger-auslesen/?postID=2355585#post2355585)
