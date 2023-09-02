#!/usr/bin/python3

## @package : ThermoHygroBaroAnzeige
# Anzeige der Messwerte auf ePaper-Display.
#
# Messwerte werden vom Sensor gelesen,
# Werte werden gespeichert,
# Minima/Maxima über 24 Stunden eingelesen
# Luftdrucktrend berechnet,
# grobe Wettervorhersage aus Luftdrucktrend und Jahreszeit bestimmt.
#
# @param -v, Debug-Ausgabe
# @param "--debug", Debug-Ausgabe
#  @author Borys 13 Jul 2019
# @note benötigt die ePaper-Bibliothek epd1in54b
#
import time,argparse
import datetime 
from math import exp
from bme280lesen import readBME280All
import epd1in54b
from EPDsetBitmap import setBitmap
from PIL import Image,ImageFont,ImageDraw
from shutil import move
from os import chmod,remove
from sys import exc_info
from vorhersage import vorhersage
from getconfig import getConfig

#import imagedata
Dbg=False
COLORED = 1
UNCOLORED = 0
PMIN = 1000
PMAX = 1023
RFMIN = 40
RFMAX = 60
TEMPMIN = 20
TEMPMAX = 23
##absoluter Nullpunkt
ABS0=273.25	#abs. Nullpunkt
##Temperaturgradient. Abnahme der Temperatur mit Höhe in K/m
TEMPGRAD=0.0065 #Temperaturgradient K/m
## Datei mit abgespeicherten Messwerten
DATEI = '/tmp/raumklima.dat'
## Datei zum Umspeichern der Messerte.
# ältere als 24 Stunden werden dabei weggelassen
DATEIR = '/tmp/raumklima.tmp'
##Pfad zu Icons und Konfigurationsdatei
SHARE = '/usr/share/thb/'
##Konfigurationsdatei
CONFIG = SHARE+'thb.config'
XFAKT = 0.6
## Luftdruck-Trend-Berechnungen. Druck steigt
#
# 5 Stunden und 0.3 war zu wenig
# über 7 Stunden: +/- 0,1 ist Änderung, -0,5 ist Gewitter
TRENDGUT = 0.1
## Luftdruck-Trend-Berechnungen. Druck sinkt
TRENDSCHLECHT = -0.1
## Luftdruck-Trend-Berechnungen. Druck sinkt so stark, das Gewitter droht
TRENDSTURM = -0.5
## Zeitabstand für Min/Max-Bestimmung: 24 Stunden.
H24 = 24.0 * 3600.0
## Zeitabstand für Luftdrucktrend.
# war 3 Stunden, aber 7 Stunden sind besser
H3 = 7.0 * 3600.0

## Einlesen der vergangenen Werte.
# Bestimmung der Temperatur- und Feuchteextrema,
# Bestimmung des Luftdrucktrends
#
# @note benötigt die globalen Strings DATEI, DATEIR
# @param jetzt aktuelle Zeit. Unix-Format 
# @param pH3 Zeitabstand für Luftdrucktrend, war mal 3 Stunden
# @param pH24 Zeitabstand für Max/Min: 24 Stunden
# @param Dbg Ausgaben, wenn True
# @returns hmax, hmin Feuchteextrema
# @returns pmax, pmin Druckextrema
# @returns tmax, tmin Temperaturextrema
# @returns pvor Druck am Zeitpunkt für Trendberechnung
# @returns zeitvor Zeitpunkt des Drucks für Drucktrendberechnung
# 
def Extrema(jetzt,pH3,pH24,Dbg=False):
	# verschieben nach *.tmp
	if Dbg:print("Extrema...")
	move(DATEI,DATEIR)	
	#chmod(DATEIR,0O0666)
	# *.tmp lesen
	with  open(DATEIR, 'r', 256) as dateir:
		zeilen = dateir.readlines()
	# *.tmp löschen
	remove(DATEIR)
	tmin = 99
	tmax = -99
	pmin = 9999
	pmax = 0
	pvor = 1013
	hmin = 111
	hmax = 0
	zeitvor = 0

	# neue Datei raumklima.dat schreiben
	with open(DATEI, 'w', 256) as datei:
		for zeile in zeilen:
			szeit,sep,rest = zeile.partition(';')
			zeit = float(szeit)
			stemp,sep,rest = rest.partition(';')
			spres,sep,shum = rest.partition(';')
			if (jetzt - zeit) < pH24:
				# Min/Max der letzten 24 Stunden
				datei.write(zeile)
				temp = float(stemp)
				pres = float(spres)
				hum = float(shum)
				if temp < tmin: tmin = temp
				if temp > tmax: tmax = temp
				if hum < hmin: hmin = hum
				if hum > hmax: hmax = hum
				if pres < pmin: pmin = pres
				if pres > pmax: pmax = pres
				if (jetzt - zeit) > pH3: 
					# Druck vor 3 Stunden mit Zeit dazu
					pvor = pres
					zeitvor = zeit
	if Dbg:print("...Extrema")
	return hmax, hmin, pmax, pmin, tmax, tmin,pvor,zeitvor

## das Hauptprogramm.
# alles passiert hier
# @note benötigt die ePaper-Bibliothek
def main():
	parser = argparse.ArgumentParser(description='Thermo/Hygro/Baro-Anzeige')
	#parser.add_argument("-d", "--daten", dest="pTabelle", help="Datenbank-Tabelle", default=pDbTbl)
	#parser.add_argument("-a", "--alle", dest="alle",default=False,help="alle Bilder anzeigen",action="store_true")
	#parser.add_argument("-m", "--menschen", dest="menschen",default=False,help="Bilder mit Menschen",action="store_true")
	parser.add_argument("-v", "--debug", dest="pDbg",help="Debug-Ausgabe",action='store_true')
	arguments = parser.parse_args()
	Dbg=arguments.pDbg
		
	if Dbg:print("EPD init...")
	epd = epd1in54b.EPD()
	epd.init()
	if Dbg:print("...init OK")
	# epd.set_rotate(2) das erfordert eine Neuberechnung der Koordinaten und neue Bitmaps
	# clear the frame buffer
	pixel = int(epd.width * epd.height / 8)
	frame_black = [0xFF] * (pixel)
	frame_red = [0xFF] * (pixel)
	pt = 40
	pt1 = 20
	pt0 = 12
	font = ImageFont.truetype('/usr/share/fonts/truetype/piboto/Piboto-Bold.ttf', pt)
	font1 = ImageFont.truetype('/usr/share/fonts/truetype/piboto/Piboto-Bold.ttf', pt1)
	font0 = ImageFont.truetype('/usr/share/fonts/truetype/piboto/PibotoCondensed-Regular.ttf', pt0)
	try:
		if Dbg:print("getConfig...")
		HOEHE, TEMP, KORR,VERSION = getConfig(CONFIG,0)
		if Dbg:print("Höhe %d m"%HOEHE)
		if Dbg:print("Standardtemperatur %d °C in dieser Höhe"%TEMP)
		if Dbg:print("Korrektur Raumtemperatur %d °C"%KORR)
	except :
		if Dbg:print("...Fehler getConfig")
		epd.display_string_at(frame_red, 1, 1, "Fehler\n\n\nKonfiguration?", font, COLORED)
		print(exc_info()[0],exc_info()[1])
		
	temperature,pressure,humidity = readBME280All()
	if Dbg:print("Daten: %f °C, %f hPa QFE, %f %%r.F."%(temperature,pressure,humidity))
	jetzt = time.time()

	TEMP = ABS0 + TEMP #Umrechnung in Kelvin
	## Barometer, Umrechnung auf Meereshöhe
	#
	#alte Formel:
	#redukt = exp((0.02896 * 9.807 * HOEHE) / (8.314 * TEMP))
	#pressure = pressure * redukt
	#Der Temperaturgradient gibt an, wie schnell die Temperatur mit der Höhe fällt. 
	#Eine gute Schätzung bei normalem Wetter ist 0,0065 °C/Meter.
	#Temperaturschätzung: Temperatur auf Meereshöhe = Temperatur + Temperaturgradient * Höhe
	#Barometrische Höhenformel:
	#Luftdruck auf Meereshöhe = 
	#Barometeranzeige / (1-Temperaturgradient*Höhe/Temperatur auf Meereshöhe in Kelvin)^(0,03416/Temperaturgradient)
	quot=(1.0-TEMPGRAD*HOEHE/(ABS0+15.0))**(0.03416/TEMPGRAD)
	pressure = pressure /quot
	if Dbg:print("%f hPa QNH"%pressure)
	temperature=temperature+KORR
	try:
		with open(DATEI, 'a', 64) as datei:
			datei.write("{};{:>+6.2f};{:>7.2f};{:>5.2f}\n".format(jetzt,temperature,pressure,humidity))
	except PermissionError:
		epd.display_string_at(frame_red, 1, 1, "Fehler", font, COLORED)
		epd.display_string_at(frame_red, 1, 50, "Schreiben von", font1, COLORED)
		epd.display_string_at(frame_red, 1, 70, DATEI, font1, COLORED)
	except:
		epd.display_string_at(frame_red, 1, 1, "Fehler?", font, COLORED)
		print(exc_info()[0],exc_info()[1])
		raise
	else:
		try:
			hmax, hmin, pmax, pmin, tmax, tmin, pvor,zeitvor = Extrema(jetzt,H3,H24,Dbg)
		except PermissionError:
			epd.display_string_at(frame_red, 1, 1, "Fehler", font, COLORED)
			epd.display_string_at(frame_red, 1, 50, "Zwischenspeicher\nBerechtigungen\nüberprüfen!", font1,COLORED)
		except:
			epd.display_string_at(frame_red, 1, 1, "Fehler?", font, COLORED)
			print(exc_info()[0],exc_info()[1])
			raise
		else:
			pgrad = 3600.0 * (pressure - pvor) / (jetzt - zeitvor)
			if Dbg:print("Druckgradient %f hPa/h"%pgrad)
			text=vorhersage(pressure,pgrad,jetzt)
			#print(pressure, pvor, jetzt-zeitvor,pgrad)
		
			
			try:
				f_trend = frame_black
				trend = Image.open(SHARE+'O.bmp')				#Druck unverändert
				if pgrad > TRENDGUT:
					trend = Image.open(SHARE+'NO.bmp')			#Druck steigt
					if pgrad > 2*TRENDGUT:f_trend = frame_red
				if pgrad < TRENDSCHLECHT:
					trend = Image.open(SHARE+'SO.bmp')			#Druck fällt
					if pgrad < 2*TRENDSCHLECHT:f_trend = frame_red
				if pgrad < TRENDSTURM:
					trend = Image.open(SHARE+'S.bmp')			#Sturm, Gewitter
					f_trend = frame_red
			except :
				epd.display_string_at(frame_red, 1, 1, "\nFehler\nIcons?", font, COLORED)
				print(exc_info()[0],exc_info()[1])
		
			# For simplicity, the arguments are explicit numerical coordinates
			#epd.draw_rectangle(frame_black, 10, 60, 50, 110, COLORED);
			#epd.draw_line(frame_black, 10, 60, 50, 110, COLORED);
			#epd.draw_line(frame_red, 50, 60, 10, 110, COLORED);
			#epd.draw_circle(frame_black, 120, 80, 30, COLORED);
			#epd.draw_filled_rectangle(frame_red, 10, 130, 50, 180, COLORED);
			#epd.draw_filled_rectangle(frame_red, 0, 6, 200, 26, COLORED);
			#epd.draw_filled_circle(frame_red, 120, 150, 30, COLORED);
		
			## write strings to the buffer
		
			x = 1
			y = 1
			x2 = 142
			x1 = 105
			f = frame_black
			if pressure < PMIN:		f = frame_red
			if pressure > PMAX:		f = frame_red
			epd.display_string_at(f, x, y, "{:>4.0f}".format(pressure), font, COLORED)
			epd.display_string_at(frame_black, x1, y + pt - pt1, "hPa", font1, COLORED)
		
			setBitmap(epd.width,epd.height,x2 + 10,y + 10,f_trend,trend)
			#Jahreszeit anzeigen (nicht fertig)
			#setBitmap(epd.width,epd.height,x1, y + pt - pt1,f_trend,Image.open(SHARE+'sommer.bmp'))
		
		
			y = y + pt
			f = frame_black
			if temperature < TEMPMIN: 		f = frame_red
			if temperature > TEMPMAX:		f = frame_red
			epd.display_string_at(f, x, y, "{:> 6.1f}".format(temperature), font, COLORED)
			epd.display_string_at(frame_black, x1, y + pt - pt1, "°C", font1, COLORED)
			epd.display_string_at(frame_black, x2, y + pt - pt1, "{:> 6.1f}°".format(tmin), font1, COLORED)
			epd.display_string_at(frame_black, x2, y + pt - 2 * pt1, "{:> 6.1f}°".format(tmax), font1, COLORED)
		
			y = y + pt
			f = frame_black
			if humidity < RFMIN:		f = frame_red
			if humidity > RFMAX:		f = frame_red
			epd.display_string_at(f, x, y, "{:>4.0f}".format(humidity), font, COLORED)
			epd.display_string_at(frame_black, x1, y + pt - pt1, "%r.F.", font1, COLORED)
			epd.display_string_at(frame_black, x2, y + pt - pt1, "{:>4.0f}%".format(hmin), font1, COLORED)
			epd.display_string_at(frame_black, x2, y + pt - 2 * pt1, "{:>4.0f}%".format(hmax), font1, COLORED)
		
		
			y = y + 1.1*pt
			f = frame_black

			# Wetter Text oder Icon
			#print(text[0:2])
			#print(text[2:])
			if text[0:2] == "B=":
				try:
					bild = Image.open('/usr/share/thb/' + text[2:] + '.bmp')	
					setBitmap(epd.width,epd.height,x,y,f,bild)
				except :
					epd.display_string_at(frame_red, x, y, "Bitmap FEHLT:\n"+text[2:], font1, COLORED)
			else:
				epd.display_string_at(f, x, y, text, font1, COLORED)
		
		
	
	
			y = epd.height - 1.1 * pt0
			x = 1
			epd.display_string_at(frame_black, x, y, VERSION+" {:%H:%M}".format(datetime.datetime.now()), font0, COLORED)
	finally:
		## display the frame
		if Dbg:print("Display Frame black, red ...")
		epd.display_frame(frame_black, frame_red)
		if Dbg:print("...sleep...")
		epd.sleep()
		if Dbg:print("...fertig")
		
	# You can get frame buffer from an image or import the buffer directly:
	#epd.display_frame(imagedata.IMAGE_BLACK, imagedata.IMAGE_RED)
if __name__ == '__main__':
	main()
