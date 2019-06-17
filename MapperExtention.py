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
				"""SELECT DISTINCT wikidata_id FROM mapping
				 WHERE wikidata_id NOT IN (
				 SELECT DISTINCT wikidata_id from wiki_data WHERE entity_type != ""
				 )
				"""
			)
			results = c.fetchall()

			return [e[0] for e in results]


	def create_data_tabel(self):
		with sqlite3.connect(self._path_to_db) as conn:
			conn.execute(
				"""CREATE TABLE wiki_data (
				    wikidata_id     TEXT PRIMARY KEY,
				    wikipedia_title TEXT,
				    synonyms_title        TEXT,
				    synonyms_data        TEXT,
				    entity_type     TEXT,
				    categories      TEXT,
				    page_text       TEXT
				)"""
			)

			conn.execute("""
			INSERT INTO wiki_data (
                        wikidata_id,
                        wikipedia_title,
                        entity_type,
                        synonyms_title,
                        synonyms_data,
                        categories,
                        page_text
                    )
                    SELECT wikidata_id,
                    wikipedia_title,
                    "",
                    group_concat(REPLACE(wikipedia_title,'_',' '),';') as synonyms_title,
                    "",
                    "",
                    ""
                    FROM mapping 
					GROUP BY 
                    wikidata_id 
                      """)

		return conn.cursor()


	def extand_entities_with_wiki_data(self, wiki_data):
		quaryData = []
		for item in wiki_data:
			wikidata_id = item['item']['value'].replace("http://www.wikidata.org/entity/","")
			quaryData.append((item['itemSynos']['value'],item['types']['value'],wikidata_id))
		with sqlite3.connect(self._path_to_db) as conn:
			c = conn.cursor()
			quary = f"""
			UPDATE wiki_data
			SET synonyms_data = ?,
			 entity_type = ?
			WHERE wikidata_id = ?
			"""
			print(quary)
			res = c.executemany(quary,quaryData)
			print(str(res.rowcount) + "rows updated")
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

	def get_entities_data_by_titles(self,titles):
		result = []
		SQL_MAX_QUAERY = 999
		for i in range(0,len(titles),SQL_MAX_QUAERY):
			group = titles[i:i+SQL_MAX_QUAERY]
			query = ','.join(['?'] * len(group))
			with sqlite3.connect(self._path_to_db) as conn:
				c = conn.cursor()
				conn.set_trace_callback(print)
				c.execute(f"""
				SELECT wikidata_id,title,categories,entity_type,synonyms_data,synonyms_title
				 FROM wiki_data 
				 INNER JOIN
					(SELECT wikipedia_title AS title,wikidata_id AS wiki_id
				    FROM mapping 
				    WHERE wikipedia_title in ({query})) AS RES
				ON wiki_data.wikidata_id = RES.wiki_id
				""", group)
				groupResult = c.fetchall()
			if groupResult and groupResult[0] is not None:
				result.extend(groupResult)
		return result

	def stor_items_data(self, itemsData):
		with sqlite3.connect(self._path_to_db) as conn:
			c = conn.cursor()
			c.executemany("""
			UPDATE wiki_data
			SET categories = ?,
			page_text = ?
			WHERE wikidata_id = ?
			""",itemsData)




