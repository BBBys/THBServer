# THBServer
alle Dateien für den Rasperry-basierten Thermo/Hygro/Baro-Server
## Datenabfrage TCP Port 5005,
    antwortet mit Temperatur, Luftfeuchtigkeit, Luftdruck
        Format TT.tt;FF.ff;DDDD.dd;
    Skript Restartthbserver auf /etc/cron.hourly
    (kann 60 Minuten dauern, bis der Zugriff möglich ist)
## Höhe des Sensors über Meeresspiegel angeben:
    Datei /usr/share/thb/thb.config,
    Zeile 1: Höhe in Metern über NN
        Zeile 2: unwichtig
        Zeile 3: Temperaturkorrektur (negativ, wenn wirkliche kleiner als gemessene)
### Dateitransfer mit SFTP
User root, Kennwort root
### Verzeichnisse
    Programme auf /usr/local/thb
    Icons und Konfiguration auf /usr/share/thb
    Messwerte zur Trendbestimmung: /tmp/raumklima.dat (bei Reboot gelöscht)
### Displayupdate 
#### durch crontab:
    /var/spool/cron/crontabs/pi oder …/root (wobei root besser ist)
    
    @reboot /usr/local/thb/ThermoHygroBaroAnzeige.py &
    8,28,48 6-23 * * * /usr/local/thb/ThermoHygroBaroAnzeige.py
# Einrichtung
SPI und I2C muss eingeschaltet sein

zu kopieren:
## /etc/init.d
thbstart, Berechtigungen rwx r-x r-x
## /usr/local/thb
thb: gesamtes Verzeichnis, Berechtigungen rwx r-x r-x
## /usr/share/thb
thb: gesamtes Verzeichnis

Stand 29 Aug 2023 2019
