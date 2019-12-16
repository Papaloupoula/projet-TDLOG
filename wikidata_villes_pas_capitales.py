
# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """
SELECT DISTINCT ?cityLabel ?population ?countryLabel ?capitalLabel
WHERE
{
  ?city wdt:P31/wdt:P279* wd:Q1549591 .
  ?city wdt:P1082 ?population .
  ?city wdt:P17 ?country .
  ?country wdt:P36 ?capital
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "fr" .
  }
}
ORDER BY DESC(?population) LIMIT 300"""


def get_results(endpoint_url, query):
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


results = get_results(endpoint_url, query)

results = results['results']['bindings']

dictionnaire_villes = {}

for i in range(len(results)):
    dictionnaire_villes[results[i]['countryLabel']['value']] =[]

for i in range(len(results)):
    if results[i]['cityLabel']['value'] != results[i]['capitalLabel']['value'] and len(dictionnaire_villes[results[i]['countryLabel']['value']]) < 5:
        dictionnaire_villes[results[i]['countryLabel']['value']].append(results[i]['cityLabel']['value'])
