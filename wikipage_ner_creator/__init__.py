import wikimapper as wikimapper
import io
import re
from pathlib import Path

from wikipage_ner_creator import SPARQL, MapperExtention
from wikipage_ner_creator.hebner import HebNer

options = {}
options["BIOES"] = True
options["data"] = "../Data"

def create_hewiki_textfile():
	'''read all files one by one, and concat them without the labels
	for word embedding task'''
	pathlist = Path(options["data"]+"/Output").glob('**\wiki_*')
	with io.open("../Data/wiki-text", 'a', encoding='utf-8') as out:
		for path in pathlist:
			print(path)
			with io.open(path, 'r', encoding='utf-8') as f:
				fileText = f.read()
				fileText = re.sub("<.*>","",fileText)
				fileText = fileText.replace("\n"," ")
				out.write(fileText)

def categorise():
	'''read all files one by one, and edit the labeled line by
	the chosen strategy'''
	hn = HebNer(mapperExt, options)
	pathlist = Path(options["output"]+"/Output").glob('**\wiki_*')
	#statistcs = {"words": 0, "labeled": 0, "pages": 0, "I-ORG": 0, "I-PER": 0, "I-LOC": 0, "I-MISC": 0}
	for path in pathlist:
		print(path)
		with io.open(path, 'r', encoding='utf-8') as f:
			fileData = hn.label_wiki_file(f)
		mapperExt.stor_items_data(fileData)

def create_wikidata_mapper():
	wikimapper.download_wikidumps('hewiki-latest',options["output"]+"Mapping",overwrite=False)
	wikimapper.create_index('hewiki-latest',options["output"]+"Mapping",options["output"])
	mapperExt.create_data_tabel()
	allLabels = mapperExt.get_all_entities()
	labels = [l for l in allLabels if l is not None]
	for wiki_data in SPARQL.SPARQL().get_wikidata_labels(labels):
		mapperExt.extand_entities_with_wiki_data(wiki_data)

if __name__ == '__main__':
	#mapperExt = MapperExtention.WikiMapperExtention(options["output"]+"Mapping")
	#create_wikidata_mapper()
	#categorise()
	create_hewiki_textfile()

