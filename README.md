# Digitalskills.se - Data

## Så är digitalskills.se framtaget
1. Extrahering av annonser från rådata
Historiska jobbannonser hämtas kvartalsvis från Jobtech Development. Från datasetet extraheras annonser som är kategoriserade som Data/IT enligt Jobtech Development’s taxonomi. Du kan hitta datasetet här. Detta görs i `extract_ad_info.py`

2. Berikning av annonsdata
Jobtech Developments algoritm JobAd Enrichments anropas via API och tillämpas på aktuella annonser för att plocka fram kompetenser, yrken, information om jobbets geografiska läge samt mjuka kompetenser kopplade till annonsen. Extraheringen av kompetenser tar ej i beaktning avgränsningen till Data/IT och följaktligen behöver resultatet filtreras genom en framtagen ”black list” på kompetensord. Processen har ett tröskelvärde för den statistiska säkerhet som JobAd Enrichments anser sig ha i sin träffsäkerhet för extraheringen av de olika datapunkterna. Detta görs i `enrich_ads.py`

3. Framskrivning av data
Annonserna passerar sedan en funktion som med hjälp av öppna bibliotek i Python applicerar algoritmer för prognostisering av tidsserier. Metoden som tillämpas är exponentiell utjämning där tidsseriens säsongsvariation först utreds för att sedan tas i beaktning i framskrivningen. Framskrivningar för 6, 12 och 18 månader tas fram och sparas ned som tidsserier i resultatobjektet. I samma steg sparas även värden för historiska trender på samma intervall. Detta görs i `prediction_builder.py`

4. Rensning av data
Efter att framskrivningar har gjorts så rensas framtagna data på en viss uppsättning variabler. Rensning beror på att variabler som använts i framskrivningen och tidigare funktioner inte längre fyller någon funktion i databasen


5. Uppladdning av data
Framtagen data laddas sen upp i en databas genom ett uppladdningsskript. Här laddas varje enskild kompetens och yrke upp genom ett API. Detta görs i `upload_data.py`

6. Sammankoppling av ID:n
Efter att alla kompetenser och yrken är uppladdade så tilldelas alla ett automatiskt id. För att kunna möjliggöra länkningen mellan kompetenser och yrken så går varje kompetens och yrke genom en process där deras ID adderas under relaterade kompetenser och yrken. Detta görs i `database_id_populator.py`

## Testning
I nuläget är det brist på kodtester. Ifall du vill hjälpa till och skapa tester kan du göra detta genom att skapa tester i tests mappen. Testerna är i nuläget skriva med paketet [unittest](https://docs.python.org/3/library/unittest.html). För mer dokumentation gällande [unittest](https://docs.python.org/3/library/unittest.html) se deras [dokumentation](https://docs.python.org/3/library/unittest.html)
