## @package getconfig
# Konfigurationsparameter lesen.
# die Parameer sind:
# Höhe in Metern über Normal-Null;
# mittlere Lufttemperatur in °C;
# Temperaturkorrektur in K (negativ, wenn wirkliche kleiner als gemessene);
# Version.
#

## Funktion getConfig
#  @param pCONFIG Dateipfad.
#  @param Dbg wenn True: macht Ausgaben.
def getConfig(pCONFIG,Dbg=False):
	if Dbg:print(pCONFIG)
	with open(pCONFIG, 'r', 256) as dateir:
		## TTTTTTTTTTTTTTTTTTT .
		# xxx
		if Dbg:print("open")
		line = dateir.readline()
		HOEHE = float(line.rstrip('\n'))
		line = dateir.readline()
		TEMP = float(line.rstrip('\n'))
		line = dateir.readline()
		KORR = float(line.rstrip('\n'))
		line = dateir.readline()
		VER = line.rstrip('\n')
	if Dbg:print(VER)
	return HOEHE, TEMP, KORR,VER
