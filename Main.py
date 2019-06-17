import wikimapper as wikimapper
import io
import re
import MapperExtention
import SPARQL
from pathlib import Path

# wikimapper.download_wikidumps('hewiki-latest','./Data',overwrite=False)
# wikimapper.create_index('hewiki-latest','./Data','./Output/Mapping')
import heb_ner

mapperExt = MapperExtention.WikiMapperExtention("Output/Mapping")


pathlist = Path("./Output").glob('**\wiki_*')

options = {}
options["BIOES"] = True



def categorise():
	'''read all files one by one, and edit the labeled line by
	the chosen strategy'''
	hn = heb_ner.heb_ner(mapperExt,options)
	statistcs = {"words": 0, "labeled": 0, "pages": 0, "I-ORG": 0, "I-PER": 0, "I-LOC": 0, "I-MISC": 0}
	for path in pathlist:
		print(path)
		with io.open(path, 'r', encoding='utf-8') as f:
			fileData = hn.label_wiki_file(f)
		mapperExt.stor_items_data(fileData)


def create_wikidata_mapper():
	allLabels = mapperExt.get_all_entities()
	wiki_data = SPARQL.SPARQL().get_wikidata_labels([l for l in allLabels if l is not None])
	#mapperExt.create_data_tabel()
	return mapperExt.extand_entities_with_wiki_data(wiki_data)

#create_wikidata_mapper()
categorise()

