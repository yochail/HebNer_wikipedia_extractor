import wikimapper as wikimapper
import io
import re
import MapperExtention
from pathlib import Path

#wikimapper.download_wikidumps('hewiki-latest','./Data',overwrite=False)
#wikimapper.create_index('hewiki-latest','./Data','./Output/Mapping')


mapper = wikimapper.WikiMapper("Output/Mapping")
mapperExt = MapperExtention
docStartLine = re.compile(r'<doc id=\"\d+\" '
+'url=\"https?://he\.wikipedia\.org/wiki\?curid=\d+\" '+
                     'title=\"(.+)\" categories=\"\[(.+)\]\">')
docEndLine = re.compile(r'</doc>')
labeledLine = re.compile(r'<(.+)>(.+)')

pathlist = Path("./Output").glob('**\wiki_*')


def handelLabeledLine(line,text, label, doc_title, doc_categories):
	wiki_id = mapper.title_to_id(label)
	print(label)
	line = f"\u202a{text};\u202a{label};{str(wiki_id)}\n"
	return line



def categorise():
	'''read all files one by one, and edit the labeled line by
	the chosen strategy'''
	statistcs = {"words":0,"labeled":0,"pages":0,"I-ORG":0,"I-PER":0,"I-LOC":0,"I-MISC":0}
	for path in pathlist:
		print(path)
		with io.open(path,'r', encoding='utf-8') as f:
			newData = []
			for line in f.readlines():
				docStart = docStartLine.match(line)
				if(docStart):
					page_title = docStart.group(1)
					page_categories = docStart.group(1)
				elif docEndLine.match(line):
					#ignor line
					pass
				else:
					label = labeledLine.match(line)
					if(label):
						line = handelLabeledLine(line,label.group(2),label.group(1),page_title,page_categories)

				newData.append(line)
			io.Eopen(path, 'w', encoding='utf-8').writelines(newData)
			break


		#wikidata_id = mapper.title_to_id("מתמטיקה"



allLabels= mapperExt.WikiMapperExtention("Output/Mapping").get_all_entities()
categorise()