#!/usr/bin/python3
#
#  @filename : main.cpp
#  @brief : Server für THB-Anzeige
#  @author : Borys 19 Nov 2018
##
from sys import exc_info
import socket
# Hilfe:
# McMillan, Gordon (2018): Socket Programming HOWTO.  Python 3.7.1rc2
# documentation.
# Online verfügbar unter
# https://docs.python.org/3/howto/sockets.html#socket-howto,
# zuletzt geprüft am 14.10.2018.
from bme280lesen import readBME280All
from math import exp
from getconfig import getConfig	    
import logging

Dbg = False

def fTHBServerMain():
	ABS0=273.25	#abs. Nullpunkt
	TEMPGRAD=0.0065 #Temperaturgradient K/m
	ABSTAND = 10
	Fehler = ''
	SHARE = '/usr/share/thb/'
	CONFIG = SHARE + 'thb.config'
	TCP_IP = '' #das funktioniert, jede Adresse des Hosts wird genommen
	TCP_PORT = 5005
	BUFFER_SIZE = 20  # Normally 1024, but we want fast response
	try:
		HOEHE, TEMP,KORR,VER = getConfig(CONFIG,Dbg)
	except :
		logging.warn(exc_info()[0],exc_info()[1])
		Fehler = "Höhe unbekannt"
		HOEHE = 0
		KORR = 0
		TEMP = 15
	logging.debug("ALT %d, T %d, korr %d"%(HOEHE,TEMP,KORR))
	logging.debug(VER)
	TEMP = 273.25 + TEMP
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
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((TCP_IP, TCP_PORT))
		logging.debug(s)
		s.listen(1)
	except:
		logging.fatal("THB-Server Fehler bind/listen")
	else:
		while True:
			try:
				conn, addr = s.accept()
			except:
				logging.fatal("THB-Server Fehler accept")
			else:
				logging.debug('Connection address:', addr)
				try:
					T,B,H = readBME280All()
				except:
					M = "Fehler: Sensor lesen?".encode()
					logging.warn(M)
				else:
					T = T + KORR
					B = B /quot
					M = ('{:>6.1f};{:>5.1f};{:>6.1f};'.format(T,H,B)).encode()
				finally:
					conn.send(M)
					logging.debug(M)
					if Dbg:break
			finally:
				conn.close()
	finally:
		s.close()
	logging.info("THB-Server beendet")
	
if __name__ == '__main__':
	if Dbg:
		logging.basicConfig	(level=logging.DEBUG)
	else:
		logging.basicConfig	(level=logging.INFO)	
	logging.info("thbserver Start")
	fTHBServerMain()
