# import modulen
from pathlib import Path
import json
import pprint
from database_wrapper import Database


# initialisatie

# parameters voor connectie met de database
db = Database(host="localhost", gebruiker="user", wachtwoord="password", database="attractiepark")


# main

# Haal de eigenschappen op van een personeelslid
# altijd verbinding openen om query's uit te voeren
db.connect()

# pas deze query aan om het juiste personeelslid te selecteren
select_query = "SELECT * FROM personeelslid WHERE id = 4"
personeelslid = db.execute_query(select_query)

# altijd verbinding sluiten met de database als je klaar bent
db.close()

pprint.pp(personeelslid) # print de resultaten van de query op een overzichtelijke manier
print(personeelslid[0]['naam']) # voorbeeld van hoe je bij een eigenschap komt



# Haal alle onderhoudstaken op
# altijd verbinding openen om query's uit te voeren
db.connect()

# pas deze query aan en voeg queries toe om de juiste onderhoudstaken op te halen
select_query = "SELECT * FROM onderhoudstaak"
onderhoudstaken = db.execute_query(select_query)

# altijd verbinding sluiten met de database als je klaar bent
db.close()

#pprint.pp(onderhoudstaken) # print de resultaten van de query op een overzichtelijke manier




# verzamel alle benodigde gegevens in een dictionary

# Bereken maximale fysieke belasting op basis van leeftijd
leeftijd = personeelslid[0]['leeftijd']
if leeftijd <= 24:
    max_belasting_leeftijd = 25
elif leeftijd <= 50:
    max_belasting_leeftijd = 40
else:
    max_belasting_leeftijd = 20

# Gebruik Arboarts waarde als die is ingesteld, anders leeftijdsnorm
if personeelslid[0]['verlaagde_fysieke_belasting'] > 0:
    max_fysieke_belasting = personeelslid[0]['verlaagde_fysieke_belasting']
else:
    max_fysieke_belasting = max_belasting_leeftijd

# Specialist in attracties omzetten naar array
specialist_attracties = [attractie.strip() for attractie in personeelslid[0]['specialist_in_attracties'].split(',')] if personeelslid[0]['specialist_in_attracties'] else []

dagtakenlijst = {
    "personeelsgegevens": {
        "naam": personeelslid[0]['naam'],
        "werktijd": personeelslid[0]['werktijd'],
        "beroepstype": personeelslid[0]['beroepstype'],
        "bevoegdheid": personeelslid[0]['bevoegdheid'],
        "specialist_in_attracties": specialist_attracties,
        "pauze_opsplitsen": bool(personeelslid[0]['pauze_opsplitsen']),
        "max_fysieke_belasting": max_fysieke_belasting
    },
    "weergegevens": {
        "temperatuur": 20,
        "kans_op_regen": 50
    },
    "dagtaken": [],
    "totale_duur": 0
}

# STAP 2: Vul de dagtaken lijst
huidige_duur = 0
aantal_taken = 0

# Voeg geschikte onderhoudstaken toe
for taak in onderhoudstaken:
    if (huidige_duur + taak['duur'] <= personeelslid[0]['werktijd'] and 
        (taak['fysieke_belasting'] <= max_fysieke_belasting or taak['fysieke_belasting'] == 0)):
        
        dagtakenlijst["dagtaken"].append({
            "omschrijving": taak['omschrijving'],
            "duur": taak['duur'],
            "prioriteit": taak['prioriteit'],
            "beroepstype": taak['beroepstype'],
            "bevoegdheid": taak['bevoegdheid'],
            "fysieke_belasting": taak['fysieke_belasting'] if taak['fysieke_belasting'] > 0 else None,
            "attractie": taak['attractie'],
            "is_buitenwerk": bool(taak['is_buitenwerk'])
        })
        huidige_duur += taak['duur']
        aantal_taken += 1

# STAP 3: Zet de totale duur
dagtakenlijst["totale_duur"] = huidige_duur

# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand, die kan worden ingelezen door de acceptatieomgeving
with open('Personeelsgegevens_personeelslid_x.json', 'w') as json_bestand_uitvoer:
    json.dump(dagtakenlijst, json_bestand_uitvoer, indent=4)