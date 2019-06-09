import sqlite3
from typing import List

from wikimapper import WikiMapper


class WikiMapperExtention(WikiMapper):
	""" Uses a precomputed database created by `create_wikipedia_wikidata_mapping_db`. """

	def __init__(self, path_to_db: str):
		self._path_to_db = path_to_db
		WikiMapper.__init__(self,path_to_db)

	def get_all_entities(self) -> List[str]:
		''' Returns:
			List[str]: A list of All Wikidata ID in DB.
		'''

		with sqlite3.connect(self._path_to_db) as conn:
			c = conn.cursor()
			c.execute(
				"SELECT DISTINCT wikidata_id FROM mapping"
			)
			results = c.fetchall()

			return [e[0] for e in results]


	def create_data_tabel(self):
		with sqlite3.connect(self._path_to_db) as conn:
			conn.execute(
				"""CREATE TABLE wiki_data (
				wikidata_id text PRIMARY KEY ,
				wikipedia_title text,
				synonyms text,
				entity_type text,
				categories text
				)"""
			)

			conn.execute("""
			INSERT INTO wiki_data (
                        wikidata_id,
                        wikipedia_title,
                        entity_type,
                        synonyms,
                        categories
                    )
                    SELECT wikidata_id,
                    wikipedia_title,
                    "",
                    "",
                    group_concat(REPLACE(wikipedia_title,'_',' '),';') as synonyms
                    FROM mapping 
					GROUP BY 
                    wikidata_id 
                      """)

		return conn.cursor()


	def extand_entities_with_wiki_data(self, wiki_data):
		self.create_data_tabel()
		quaryData = []
		for item in wiki_data:
			wikidata_id = item['item']['value'].replace("http://www.wikidata.org/entity/","")
			quaryData.append((item['itemSynos']['value'],item['types']['value'],wikidata_id))
		with sqlite3.connect(self._path_to_db) as conn:
			c = conn.cursor()
			quary = f"""
			UPDATE wiki_data
			SET synonyms = synonyms || ; || '?',
			 entity_type = '?'
			WHERE wikidata_id = '?'
			"""
			print(quary)
			res = c.executemany(quary,quaryData)
			print(res.rowcount + "rows updated")
			return c

	def get_entity_data(self, wikidata_id):
		with sqlite3.connect(self._path_to_db) as conn:
			c = conn.cursor()
			c.execute("SELECT * FROM wiki_data WHERE wikidata_id=?", (wikidata_id,))
			result = c.fetchone()

		if result is not None and result[0] is not None:
			return result
		else:
			return None



