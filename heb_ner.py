import re

def format_punctuation(text:str)->str:
		#text = re.sub("<(.+?)>\[(.+?)\]", r"xx", text, re.DOTALL)
		#print(text)
		text = re.sub("([\,\.\!\:\?\;\\/\\\(\)\[\]\"\'\`\~]+)([\n\s\r]|$)+",r" \1 ",text) #punctuation in new line
		text = re.sub("([\,\.\!\:\?\;\\/\\\(\)\[\]\"\'\`\~])([\,\.\!\:\?\;\\/\\\(\)\[\]\"\'\`\~\-])",r"\1 \2",text) #sepereate close punctuation e.g ". in "bla".
		text = re.sub("([\n\s\r]|$)+([\,\.\!\:\?\;\\/\\\(\)\[\]\"\'\`\~]+)",r" \2 ",text) #punctuation in new line
		text = re.sub("([\n\s\r]|$)+([ולבמהש])(\")([\u0590-\u05fe]{2,})",r" \2 \3 \4",text) #handle citation in the middle of word
		text = re.sub("([\s\n]+)|(^$)", "\n", text) #replace spaces with newlines
		text = re.sub("^\n", "", text) #get rid of double spaces
	#	text = re.sub("\n$", "", text) #replace spaces with newlines


docStartLine = re.compile(r'<doc id=\"\d+\" '
                          + 'url=\"https?://he\.wikipedia\.org/wiki\?curid=\d+\" ' +
                          'title=\"(.+)\" categories=\"\[(.*)\]\">')
docEndLine = re.compile(r'</doc>')
labeledLine = re.compile(r'(.+)<(.+)>')

def labelWikiFile(f,mapperExt):
	newData = []
	is_first = True
	is_last = True
	lines = f.readlines()
	file_data = []
	page_title = ""
	page_categories = ""
	page_wiki_id = ""
	for i in range(len(lines)):
		line = lines[i]
		if (i < len(lines) - 1):
			next_line = lines[i + 1]
		else:
			next_line = None

		docStart = docStartLine.match(line,)
		if (docStart):
			page_title = docStart.group(1)
			page_categories = docStart.group(2)
			page_wiki_id = mapperExt.title_to_id(page_title)
		elif docEndLine.match(line):
			file_data.append(page_wiki_id, page_categories, newData)
			newData = []
		else:
			label = labeledLine.match(line)
			if (label):
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
				                           is_first, is_last)

				is_first = False

			else:
				line = handel_unlabeled_line(line)
				is_first = True
				is_last = True
			newData.append(line)

	# io.open(path, 'w', encoding='utf-8').writelines(newData)
	break
	return file_data

options = []
BEGIN_PRE = "B-"
INSIDE_PRE = "I-"
SINGLE_PRE = "S-" if options["BIOES"] else BEGIN_PRE
END_PRE = "E-" if options["BIOES"] else INSIDE_PRE
EMPTY_LABEL = "O"

def getNERLabel(labels, is_first, is_end):
	prefix = ""
	label = ""
	if (is_first, is_end):
		prefix = SINGLE_PRE
	elif (is_first):
		prefix = BEGIN_PRE
	elif (is_end):
		prefix = END_PRE
	else:
		prefix = INSIDE_PRE
	if (len(labels) == 1):
		label = labels[0]
	elif ("GPE" in labels):
		label = "GPE"
	elif ("FAC" in labels):
		label = "FAC"
	elif ("ORG" in labels):
		label = "ORG"
	else:
		print("cant resolve from:" + str(labels))
		label = labels[0]
	return prefix + label

def handel_labeled_line(line, text, label, doc_title, doc_categories, is_first, is_end):
	wiki_id = mapperExt.title_to_id(label)
	if (wiki_id):
		entityData = mapperExt.get_entity_data(wiki_id)
		labels = [l for l in entityData[4].split(';') if l not in ['']]
		if (len(labels) > 0):
			# print(label)
			NERlabel = getNERLabel(labels, is_first, is_end)
			line = f"{text};{label};{wiki_id};{NERlabel}"
		else:
			line = f"{text};{label};{wiki_id};{EMPTY_LABEL}"
		return line
	else:
		return handel_unlabeled_line(line)

def handel_unlabeled_line(line):
	line = f"{line[:-1]};;;{EMPTY_LABEL}"
	return line


def handlePunc(match):
	return ("\n" + match.group(0) + "\n").replace(" ","")



