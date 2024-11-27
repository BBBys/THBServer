## @package : vorhersage
# bestimmt Wetteränderung aus Druck, Jahreszeit und Druckänderung.
# dies ist eine noch unvollständige Implementierung des Zambretti Algorithm 
# https://github.com/sassoftware/iot-zambretti-weather-forcasting.git
# https://integritext.net/DrKFS/zambretti.htm
#
# @author Borys 26 Nov 2024 11 Nov 14 Jul 2019 20 Nov 2018
#
# Informationen: 
#$VText=array("Settled Fine","Fine Weather","Fine Becoming Less Settled","Fairly Fine Showery Later",
#"Showery Becoming more unsettled","Unsettled, Rain later","Rain at times, worse later","Rain at times, becoming very unsettled",
#"Very Unsettled, Rain",
#//10
#"Settled Fine","Fine Weather","Fine, Possibly showers","Fairly Fine, Showers likely","Showery Bright Intervals",
#//15
#"Changeable some rain","Unsettled, rain at times","Rain at Frequent Intervals","Very Unsettled, Rain","Stormy, much rain",//20
#"Settled Fine","Fine Weather","Becoming Fine","Fairly Fine, Improving","Fairly Fine, Possibly showers, early",
#//25
#"Showery Early, Improving","Changeable Mending","Rather Unsettled Clearing Later","Unsettled, Probably Improving",
#//29
#"Unsettled, short fine Intervals","Very Unsettled, Finer at times","Stormy, possibly improving","Stormy, much rain");
#$text=$VText[$Z-1];
#echo("<p> Aussichten: $text </p>");
#// Ende der Vorhersage VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
#?>
from datetime import date
## Ausgben, wenn True
Dbg=False
## bestimmt Wetteränderung aus Druck, Jahreszeit und Druckänderung. 
# Gibt Name des Icons zurück, welches die Änderung darstellt, 
# in einigen (Icon fehlt noch) Fällen auch Text, der die Änderung beschreibt.
# @todo Icons für restliche Texte entwerfen
# @param p Druck in hPa
# @param dp Druckänderung in hPa/h
# @param pjetzt nicht verwendet
# @returns String "<Text über bevorstehende Änderung>" oder "B=<Icon-Name>"
def vorhersage(p,dp,pjetzt): 
	if Dbg:print("jetzt ",pjetzt)
	heute=date.today()
	tag=heute.timetuple()[7]
	if Dbg:print(tag,heute)
	if   tag <  60: jz = 4 #Winter
	elif tag < 151: jz = 1 #Frühling
	elif tag < 243: jz = 2 #Sommer
	elif tag < 334: jz = 3 #Herbst
	else:           jz = 4 #Winter
	if Dbg:print("Jahreszeit",jz)
	korr=0
	if jz==2:						#Sommer:
		if dp<(-0.2):	korr=0		#fallend im Sommer
		elif dp>0.2:	korr=(-1)	#steigend im Sommer
	elif jz==4:						#Winter:
		if dp<(-0.2):	korr=(-1)	#fallend im Winter
		elif dp>0.2:	korr=0		#steigend im Winter
	if Dbg:print("Druckänderung, Korrektur: ",dp,korr)
	## keine Winddaten - keine Windkorrektur
	# Berechnungen
	z=max(min(round(147-(50*p)/376+korr),19),10)					#gleichbleibend 10...19
	if dp<(-0.2):	z=max(min(round(130-(10*p)/81+korr),9),1)		#fallend 1...9
	if dp>0.2:		z=max(min(round(179-(20*p)/129+korr),32),20)	#steigend 20...32
	
	# es passen 19 Zeichen in die Zeile
	Texte=(
	#1...5....0....5...9
	"beständig gut",							#1 fallend
	"B=sonne",									#"gutes Wetter",
	"gut,\nwird unbeständig",
	"B=gut-schauer",							#"ziemlich gut,\nspäter Schauer",
	"B=schauer-unbes",							#Schauer,\nwird unbeständiger",				#5
	"unbeständig,\nspäter Regen",
	"zeitweise Regen,\nspäter schlechter",
	"zeitweise Regen,\nviel schlechter",
	"sehr unbeständig,\nRegen",					#9 fallend
												#10 gleichbleibend
	"B=sonne3",									#"beständig\ngutes Wetter",					
	"B=sonne",									#"gutes Wetter",
	"B=gut-schauer-mglich",						#"gutes Wetter,\nSchauer möglich",
	"B=zgut-schauer-wahr",						#"ziemlich gut,\nSchauer wahrscheinlich",
	"B=schauer-sonne-mgl",						#"Schauer,\nSonne möglich",
	"unbeständig,\netwas Regen",				#15
	"unbeständig,\nmanchmal Regen",
	"Regen in\nhäufigen Intervallen",
	"sehr unbeständig,\nRegen",
	"stürmisch,\nviel Regen",					#19 gleichbleibend
												#20 steigend
	"B=sonne3",									#"beständig\ngutes Wetter",					
	"B=sonne",									#"gutes Wetter",
	"B=besser-werdend",							#besser werdend",
	"ziemlich gut,\nverbesserend",
	"B=zgut-schauer-wahr",						#"ziemlich gut,\n Schauer möglich",
												#25
	"B=schauer-besser",							#erst Schauer,\ndann besser",				
	"B=besser-werdend",							#Besserung",
	"ziemlich unbeständig,\nspäter besser",
	"unbeständig,\n wahrscheinlich besser",
	"unbeständig,\nkurzzeitig besser",
	"sehr unbeständig,\nmanchmal besser",		#30
	"stürmisch,\nmöglicherweise besser",
	"stürmisch,\nviel Regen")					#32 steigend
	return Texte[z-1]
	#return Texte[3]
