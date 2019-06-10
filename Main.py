import wikimapper as wikimapper
import io
import re
import MapperExtention
import SPARQL
from pathlib import Path

# wikimapper.download_wikidumps('hewiki-latest','./Data',overwrite=False)
# wikimapper.create_index('hewiki-latest','./Data','./Output/Mapping')


mapperExt = MapperExtention.WikiMapperExtention("Output/Mapping")
docStartLine = re.compile(r'<doc id=\"\d+\" '
                          + 'url=\"https?://he\.wikipedia\.org/wiki\?curid=\d+\" ' +
                          'title=\"(.+)\" categories=\"\[(.*)\]\">')
docEndLine = re.compile(r'</doc>')
labeledLine = re.compile(r'(.+)<(.+)>')

pathlist = Path("./Output").glob('**\wiki_*')

options = {}
options["BIOES"] = True

BEGIN_PRE = "B-"
INSIDE_PRE = "I-"
SINGLE_PRE = "S-" if options["BIOES"] else BEGIN_PRE
END_PRE = "E-" if options["BIOES"] else INSIDE_PRE
EMPTY_LABEL = "O"

def getNERLabel(labels, is_first, is_end):
	prefix = ""
	label = ""
	if(is_first, is_end):
		prefix = SINGLE_PRE
	elif(is_first):
		prefix = BEGIN_PRE
	elif (is_end):
		prefix = END_PRE
	else:
		prefix = INSIDE_PRE
	if(len(labels) == 1):
		label = labels[0]
	elif("GPE" in labels):
		label = "GPE"
	elif ("FAC" in labels):
		label = "FAC"
	elif ("ORG" in labels):
		label = "ORG"
	else:
		print("cant resolve from:" + str(labels))
		label = labels[0]
	return prefix+label



def handel_labeled_line(line, text, label, doc_title, doc_categories,is_first,is_end):
	wiki_id = mapperExt.title_to_id(label)
	if(wiki_id):
		entityData = mapperExt.get_entity_data(wiki_id)
		labels = [l for l in entityData[4].split(';') if l not in ['']]
		if(len(labels) > 0):
			#print(label)
			NERlabel = getNERLabel(labels,is_first,is_end)
			line = f"{text};{label};{str(wiki_id)};{NERlabel}\n"
			return line
		else:
			return handel_unlabeled_line(line)
	else:
		return handel_unlabeled_line(line)

def handel_unlabeled_line(line):
	line = f"{line[:-1]};;;{EMPTY_LABEL}\n"
	return line

def categorise():
	'''read all files one by one, and edit the labeled line by
	the chosen strategy'''
	statistcs = {"words": 0, "labeled": 0, "pages": 0, "I-ORG": 0, "I-PER": 0, "I-LOC": 0, "I-MISC": 0}
	for path in pathlist:
		print(path)
		with io.open(path, 'r', encoding='utf-8') as f:
			newData = []
			is_first = True
			is_last = True
			lines = f.readlines()

			page_title = ""
			page_categories = ""
			page_wiki_id = ""
			for i in range(len(lines)):
				line = lines[i]
				if(i<len(lines)-1):
					next_line = lines[i+1]
				else:
					next_line = None

				docStart = docStartLine.match(line)
				if (docStart):
					statistcs["pages"] += 1
					page_title = docStart.group(1)
					page_categories = docStart.group(2)
					page_wiki_id  = mapperExt.title_to_id(page_title)
				elif docEndLine.match(line):
					mapperExt.stor_item_data(page_wiki_id,page_categories,newData)
					newData = []
				else:
					statistcs["words"] += 1
					label = labeledLine.match(line)
					if (label):
						statistcs["labeled"] += 1
						label_next = labeledLine.match(next_line)

						if (label_next):
							if (label.group(2) == label_next.group(2)):
								is_last = False
							else:
								is_last = True

						line = handel_labeled_line(line,
						                           label.group(1),
						                           label.group(2),
						                           page_title,
						                           page_categories,
						                           is_first,is_last)

						is_first = False

					else:
						line = handel_unlabeled_line(line)
						is_first = True
						is_last = True

				newData.append(line)
			#io.open(path, 'w', encoding='utf-8').writelines(newData)
			break

	# wikidata_id = mapper.title_to_id("מתמטיקה"


def create_wikidata_mapper():
	allLabels = mapperExt.get_all_entities()
	wiki_data = SPARQL.SPARQL().get_wikidata_labels([l for l in allLabels if l is not None])
	#mapperExt.create_data_tabel()
	return mapperExt.extand_entities_with_wiki_data(wiki_data)

#create_wikidata_mapper()
categorise()

