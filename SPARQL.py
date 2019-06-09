import requests


class SPARQL:
	def __init__(self):
		self.url = 'https://query.wikidata.org/sparql'

	def get_wikidata_labels(self,wikidata_ids):
		data_list = []
		step = 400
		ids_groups = [wikidata_ids[i:i+step] for i in range(0,len(wikidata_ids),step)]
		for group in ids_groups:
			ids = " wd:" + " wd:".join(group)
			query = """
			SELECT ?item ?itemLabel (GROUP_CONCAT(DISTINCT ?itemSyno; SEPARATOR=";") AS ?itemSynos) (GROUP_CONCAT(DISTINCT ?type; SEPARATOR=";") AS ?types) WHERE {
			  VALUES ?item { """ + ids + """  }
			  VALUES(?class ?type){
			    (wd:Q1496967 "GPE")
			    (wd:Q27096213 "LOC")
			    (wd:Q43229 "ORG")
			    (wd:Q795052 "PER")  
			    (wd:Q11471 "TIM") 
			    (wd:Q205892 "DAT") 
			    (wd:Q13226383 "FAC")
			  } 
			  ?item (wdt:P31/(wdt:P279*)) ?class;
			  OPTIONAL{ ?item skos:altLabel ?itemSyno
			  FILTER(LANG(?itemSyno) = "he").}
	
			  SERVICE wikibase:label { bd:serviceParam wikibase:language "he". }
			}
			GROUP BY ?item ?itemLabel
			"""
			r = requests.get(self.url, params={'format': 'json', 'query': query})
			print(r)
			data = r.json()
			data_list.extend(data["results"]["bindings"])
		return data_list






#"""
# {
# 	"head": {
# 		"vars": [
# 			"item",
# 			"itemLabel",
# 			"itemSynos",
# 			"types"
# 		]
# 	},
# 	"results": {
# 		"bindings": [
# 			{
# 				"item": {
# 					"type": "uri",
# 					"value": "http://www.wikidata.org/entity/Q1000"
# 				},
# 				"itemLabel": {
# 					"xml:lang": "he",
# 					"type": "literal",
# 					"value": ""
# 				},
# 				"itemSynos": {
# 					"type": "literal",
# 					"value": ""
# 				},
# 				"types": {
# 					"type": "literal",
# 					"value": "LOC;GPE;ORG"
# 				}
# 			},
# 			{
# 				"item": {
# 					"type": "uri",
# 					"value": "http://www.wikidata.org/entity/Q100"
# 				},
# 				"itemLabel": {
# 					"xml:lang": "he",
# 					"type": "literal",
# 					"value": "sddsssd"
# 				},
# 				"itemSynos": {
# 					"type": "literal",
# 					"value": ""
# 				},
# 				"types": {
# 					"type": "literal",
# 					"value": "GPE;ORG;LOC"
# 				}
# 			}
# 		]
# 	}
# }


