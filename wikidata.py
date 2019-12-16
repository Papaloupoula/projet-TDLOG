from wikidata_villes_pas_capitales import dictionnaire_villes
# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT DISTINCT ?countryLabel ?capitalLabel ?population ?continentLabel ?presidentLabel ?flag
WHERE
{
  ?country wdt:P31 wd:Q3624078;
           wdt:P1082 ?population;
           wdt:P30 ?continent
  #not a former country
  FILTER NOT EXISTS {?country wdt:P31 wd:Q3024240}
  #and no an ancient civilisation (needed to exclude ancient Egypt)
  FILTER NOT EXISTS {?country wdt:P31 wd:Q28171280}
  OPTIONAL { ?country wdt:P36 ?capital } .
  OPTIONAL { ?country wdt:P35 ?president} .
  OPTIONAL { ?country wdt:P41 ?flag} .

  SERVICE wikibase:label { bd:serviceParam wikibase:language "fr" }
}
ORDER BY ASC(?continentLabel)"""


def get_results(endpoint_url, query):
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


results = get_results(endpoint_url, query)

results = results["results"]["bindings"]


dictionnaire_des_pays = [{'Pays' : results[i]['countryLabel']['value'], 'Capitale' : results[i]['capitalLabel']['value'], 'Continent' :results[i]['continentLabel']['value'], 'President' : results[i]['presidentLabel']['value'], 'Population' : results[i]['population']['value'], 'Drapeau' : results[i]['flag']['value']} for i in range(len(results)) if ('capitalLabel' in results[i])]


#Crée un dictionnaire de la forme ['Pays', 'Capitale', 'Continent', 'Population']

for pays in dictionnaire_des_pays:
    if pays['Pays'] in dictionnaire_villes:
        pays['GdesVilles'] = dictionnaire_villes[pays['Pays']]

#Ajoute les grandes villes autres que la capitale ex pour la France on a :
# >>> dictionnaire_des_pays[171]
#{'Pays': 'France', 'Capitale': 'Paris', 'Continent': 'Europe', 'President': 'Emmanuel Macron', 'Population': '66628000', 'Drapeau': 'http://commons.wikimedia.org/wiki/Special:FilePath/Flag%20of%20France.svg', 'GdesVilles': ['Marseille', 'Lyon', 'Toulouse', 'Nice', 'Nantes']}

# /!\ y'a pas de gdes villes pour tous les pays pour l'instant, on verra si on peut améliorer ça plus tard /!\ du coup parfois la clé 'GdesVilles' n'existe pas