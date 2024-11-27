#!/usr/bin/python3
#  @filename : thbStartup.py
#  @brief : Begrüßungsprogramm für die THB-Anzeige
#  @version : 2.0.1
#  @author : Borys 26 23 Okt 2019 20 Nov 2018
##
from time import sleep
import datetime,argparse
from math import exp
from bme280lesen import readBME280All

from EPDsetBitmap import setBitmap
from PIL import Image,ImageFont,ImageDraw
from shutil import move
from os import chmod,remove
from sys import exc_info
from vorhersage import vorhersage
from getconfig import getConfig
import socket
import logging

DEBUG=0
COLORED = 1
UNCOLORED = 0
DATEI = '/tmp/raumklima.dat'
DATEIR = '/tmp/raumklima.tmp'
SHARE = '/usr/share/thb/'
CONFIG = SHARE+'thb.config' 


def main(epd,DEBUG):
	
	logging.debug("Start main")
	epd.init()
	epd.Clear()
	
	sleep(1)
	logging.debug("init OK")
	# epd.set_rotate(2) das erfordert eine Neuberechnung der Koordinaten und neue Bitmaps
	# clear the frame buffer
	pixel = int(epd.width * epd.height / 8)
	frame_black = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
	frame_red = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
	drawblack = ImageDraw.Draw(frame_black)
	drawred = ImageDraw.Draw(frame_red)
	pt = 28
	pt1 = 14
	pt1 = 14
	pt0 = 12
	font = ImageFont.truetype('/usr/share/fonts/truetype/piboto/Piboto-Bold.ttf', pt)
	font1 = ImageFont.truetype('/usr/share/fonts/truetype/piboto/Piboto-Bold.ttf', pt1)
	font0 = ImageFont.truetype('/usr/share/fonts/truetype/piboto/PibotoCondensed-Regular.ttf', pt0)
	HOEHE, TEMP, KORR, VERSION = getConfig(CONFIG)
		
	# For simplicity, the arguments are explicit numerical coordinates
	#drawblack.rectangle((0, 10, 200, 34), fill = 0)
 #   drawblack.text((8, 12), 'hello world',font=font = font, fill = 255)
 #   drawblack.text((8, 36), u'微雪电子',font=font = font18, fill = 0)
 #   drawblack.line((16, 60, 56, 60), fill = 0)
 #   drawblack.line((56, 60, 56, 110), fill = 0)
 #   drawblack.line((16, 110, 56, 110), fill = 0)
 #   drawred.line((16, 110, 16, 60), fill = 0)
 #   drawred.line((16, 60, 56, 110), fill = 0)
 #   drawred.line((56, 60, 16, 110), fill = 0)
 #   drawred.arc((90, 60, 150, 120), 0, 360, fill = 0)
 #   drawred.rectangle((16, 130, 56, 180), fill = 0)
 #   drawred.chord((90, 130, 150, 190), 0, 360, fill = 0)
 #   epd.display(epd.getbuffer(blackimage),epd.getbuffer(redimage))
    
		
	## write strings to the buffer
		
	x = 1
	y = -5
	x2 = 147
	x1 = 105
#   drawblack.text((8, 12), 'hello world',font=font = font, fill = 255)
	drawred.text(( x, y), "THB-Display",font=font, fill = 0)
	y=y+pt
	drawblack.text(( x, y), "Thermometer",font=font1, fill = 0)
	#drawblack.text(( x1, y, "mit BME280",font=font0, fill = 255)
	y=y+pt1
	drawblack.text(( x, y), "Hygrometer",font=font1, fill = 0)
	drawred.text(( x1, y), "Vers. "+VERSION,font=font1, fill = 0)
	y=y+pt1
	drawblack.text(( x, y), "Barometer",font=font1, fill = 0)
	drawred.text(( x1, y), "B.Borys 2019",font=font1, fill = 0)
	#setBitmap(epd.width,epd.height,x2 + 10,y + 10,frame_black,SHARE+"sonne.bmp")
	
	y=y+pt1+10
	#drawblack.text(( x, y, "Barometer",font=font1, fill = 0)
	drawred.text(( x, y), "Parameter:",font=font, fill = 0)
	
	y=y+pt
	drawblack.text(( x, y), "Sensorhöhe: {:>4.0f} m über N.N.".format(HOEHE),font=font1, fill = 0)
	y=y+pt1
	drawblack.text(( x, y), "mittlere Lufttemperatur: {:>2.0f} °C".format(TEMP),font=font1, fill = 0)
	y=y+pt1
	drawblack.text(( x, y), "Korrektur Ist ./. Sensor: {:>2.1f} K".format(KORR),font=font1, fill = 0)
	y=y+pt1
	drawblack.text(( x, y), "Hostname: "+socket.getfqdn(),font=font1, fill = 0)
	y=y+pt1
	#drawblack.text(( x, y, "IP: "+socket.get,font=font1, fill = 255)
	#y=y+pt1
	drawblack.text(( x, y), "Zeit: {:%H:%M}".format(datetime.datetime.now()),font=font1, fill = 0)
	logging.debug("erste Anzeige...")
	
	epd.display(epd.getbuffer(frame_black),epd.getbuffer(frame_red)) 
	 #   epd.display_frame(frame_black, frame_red)

	
def main2(epd,DEBUG):
	logging.debug("Start main2")
	epd.init()
	logging.debug("init OK")
	pixel = int(epd.width * epd.height / 8)
	frame_black = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
	frame_red = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
	drawblack = ImageDraw.Draw(frame_black)
	drawred = ImageDraw.Draw(frame_red)
	# epd.set_rotate(2) das erfordert eine Neuberechnung der Koordinaten und neue Bitmaps
	# clear the frame buffer
	pt = 40
	pt1 = 20
	pt0 = 12
	ptc=int(pt/2)
	ptd=int(pt/3.3)
	#font = ImageFont.truetype('/usr/share/fonts/truetype/piboto/Piboto-Bold.ttf', pt)
	fontc = ImageFont.truetype('/usr/share/fonts/truetype/piboto/Piboto-Bold.ttf', ptc)
	fontd = ImageFont.truetype('/usr/share/fonts/truetype/piboto/Piboto-Bold.ttf',ptd )
	#font1 = ImageFont.truetype('/usr/share/fonts/truetype/piboto/Piboto-Bold.ttf', pt1)
	#font0 = ImageFont.truetype('/usr/share/fonts/truetype/piboto/PibotoCondensed-Regular.ttf', pt0)
	x = 1
	y = 1
	x2 = 147
	x1 = 105
	f = frame_black
	drawblack.text(( x, y), "Luftdruck",font=fontc, fill = 0)
	drawblack.text(( x, y+ptc), "auf Meereshöhe",font=fontc, fill = 0)
	drawblack.text(( x2+10, y), "3-Std.-\nTrend",font=fontd, fill = 0)

	y=y+pt+5
	drawblack.text(( x, y), "Raum-",font=fontc, fill = 0)
	drawblack.text(( x, y+ptc), "temperatur",font=fontc, fill = 0)
	drawblack.text(( x2+10, y + pt - pt1), "Min",font=fontd, fill = 0)
	drawblack.text(( x2+10, y + pt - 2*pt1), "Max",font=fontd, fill = 0)

	y=y+pt+5
	drawblack.text(( x, y), "Luft-",font=fontc, fill = 0)
	drawblack.text(( x, y+ptc), "Feuchte",font=fontc, fill = 0)
	drawblack.text(( x2+10, y + pt - pt1), "Min",font=fontd, fill = 0)
	drawblack.text(( x2+10, y + pt - 2 * pt1), "Max",font=fontd, fill = 0)
		
	y=y+1.1*pt+5

	drawblack.text(( x, y), "Wetterentwicklung",font=fontc, fill = 0)
	drawred.text(( x, y+pt-5), "Update alle 20 Min.",font=fontc, fill = 0)
	
	epd.display(epd.getbuffer(frame_black),epd.getbuffer(frame_red)) 
	
	
	# You can get frame buffer from an image or import the buffer directly:
	#epd.display_frame(imagedata.IMAGE_BLACK, imagedata.IMAGE_RED)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Start-Anzeige für Thermo/Hygro/Baro-Anzeige')
	#parser.add_argument("-d", "--daten", dest="pTabelle", help="Datenbank-Tabelle", default=pDbTbl)
	#parser.add_argument("-a", "--alle", dest="alle",default=False,help="alle Bilder anzeigen",action="store_true")
	#parser.add_argument("-m", "--menschen", dest="menschen",default=False,help="Bilder mit Menschen",action="store_true")
	parser.add_argument("-v", "--debug", dest="pDbg",help="Debug-Ausgabe",action='store_true')
	arguments = parser.parse_args()
	DEBUG=arguments.pDbg
	if DEBUG:
		logging.basicConfig	(level=logging.DEBUG)
	else:
		logging.basicConfig	(level=logging.INFO)	
	logging.info("thbStartup Start")
	logging.debug("import...")
	import epd1in54b
	logging.debug("...import OK")
	epd = epd1in54b.EPD()
	
	main(epd,DEBUG)
	if DEBUG:
		sleep(0.1)
	else:
		sleep(10)
	main2(epd,DEBUG)
	epd.sleep()
	logging.debug("thbStartup Display sleep, Ende")
	
