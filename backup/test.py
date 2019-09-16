trackDict =	{
	"24 Hours of Le Mans Circuit": "1740968730",
	"Autodromo Internazionale Enzo E Dino Ferrari Imola": "920145926",
	"Autodromo Nazionale Monza GP": "4241994684",
	"Autodromo Nazionale Monza GP Historic": "1184596327",
	"Autodromo Nazionale Monza Historic Oval + GP Mix": "1327182267",
	"Autodromo Nazionale Monza Oval Historic": "4131920659",
	"Autodromo Nazionale Monza Short": "368740158",
	"Autódromo Internacional do Algarve": "3878349996",
	"Azure Circuit": "832629329",
	"Azure Coast": "560711985"}



for key, value in trackDict.items():
    if key == "Azure Coast":
        track = key
        trackid =  value


print(track)
print(trackid)