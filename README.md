# THBServer

alle Dateien für den Rasperry-basierten Thermo/Hygro/Baro-Server

## Ziel

- Anzeige von Wetter- und Raumklimadaten auf einem ePaper-Display
  - Wetterdaten von einem Wetterserver
  - Raumklima aus einem BME280- oder DHT-Sensor
- zusätzlich grobe Vorhersage der Wetterentwicklung
- Software auf einem Raspberry
- zusätzlich zur Anzeige die Möglichkeit, die Daten auch über eine Schnittstelle abzufragen

## Darstellung

[Aussehen](Bilder/b1.jpg)

[Gehäuse](Bilder/b2.jpg)

## Datenabfrage

Abfrage der Daten ist über den TCP-Port 5005 möglich. Der Server antwortet mit Temperatur (T), Luftfeuchtigkeit (F) und Luftdruck (D) im Format
> TT.tt;FF.ff;DDDD.dd;
Das Skript dazu ist `Restartthbserver` auf `/etc/cron.hourly`. Das kann
60 Minuten dauern, bis der Zugriff möglich ist

## Luftdruck

Wird der Luftdruck über dem BME280 ermittent, muss zur Umrechnung die Höhe des
Sensors über Meeresspiegel angegeben verden. Dies erfolgt in  der Datei
`/usr/share/thb/thb.config`:

```text
Zeile 1: Höhe in Metern über NN
Zeile 2: unwichtig
Zeile 3: Temperaturkorrektur (negativ, wenn wirkliche kleiner als gemessene)
```

Die Formel für die Umrechnung sollte lauten

```C
pressure *pow(1 - (0.0065* elevationM) / (tempC + (0.0065 * elevationM) + 273.15),-5.257 ))
```

[!NOTE] prüfen

## Vorhersage

Eine Vorhersage wird versucht mit Hilfe des
[Zambretti Algorithm for Weather Forecasting](https://github.com/sassoftware/iot-zambretti-weather-forcasting.git), die Windrichtung wird noch nicht berücksichtigt.
> [!NOTE]
> implementieren
Auf der Seite von @sassoftware steht mehr dazu. Ebenso [Short-Range Local Forecasting with a Digital Barograph using an Algorithm based on the Zambretti Forecaster](https://integritext.net/DrKFS/zambretti.htm)

### Vorhersage-Icons

Die Namen der Icons entsprechen ungefähr der Aussage der Vorhersage, zum Beispiel `gut-schauer-m\[ö\]glich.bmp`.

## Verzeichnisse

```text
Programme auf /usr/local/thb
Icons und Konfiguration auf /usr/share/thb
Messwerte zur Trendbestimmung: /tmp/raumklima.dat (bei Reboot gelöscht)
```

## Displayupdate

gesteuert durch Eintrag in `crontab` auf `/var/spool/cron/crontabs/pi` oder
`…/root*` (wobei root besser ist) beim Start und tagsüber alle 20 Minuten

```bash
\@reboot /usr/local/thb/ThermoHygroBaroAnzeige.py &
8,28,48 6-23 * * * /usr/local/thb/ThermoHygroBaroAnzeige.py
```

## noch zu erledigen

- mehr Icons
- Windrichtung berücksichtigen
- Luftdruck-Umrechnung prüfen

[!note] Stand 11/2024
