import re
from argparse import ArgumentError
from logging import exception
import html

options = {
"BIOES" : True
}
docStartLine = re.compile(r'<doc id=\"\d+\" '
                               + 'url=\"https?://he\.wikipedia\.org/wiki\?curid=\d+\" ' +
                               'title=\"(.+)\" categories=\"\[(.*)\]\">')
docEndLine = re.compile(r'</doc>')
labeledLine = re.compile(r'(.+)<(.+)>')

class HebNer:
	def __init__(self,mapperExt = None,options = {}):
		self.BEGIN_PRE = "B-"
		self.INSIDE_PRE = "I-"
		self.SINGLE_PRE = "S-" if options.get("BIOES") else self.BEGIN_PRE
		self.END_PRE = "E-" if options.get("BIOES") else self.INSIDE_PRE
		self.EMPTY_LABEL = "O"
		self.mapperExt = mapperExt
		self.labels = ["ORG","PER","LOC","TIM"]
		if options.get("GPE"):
			self.labels.append("GPE")
		if options.get("FAC"):
			self.labels.append("FAC")

	def get_labels_enc(self):
		PRE_TYPES = [self.BEGIN_PRE,self.INSIDE_PRE]
		if options.get("BIOES"):
			PRE_TYPES.append(self.SINGLE_PRE)
			PRE_TYPES.append(self.END_PRE)
		labels_enc = {}
		counter = 0
		labels_enc[self.EMPTY_LABEL] = counter
		for pre in PRE_TYPES:
			for label in self.labels:
				counter = counter+1
				labels_enc[pre + label] = counter
		return labels_enc


	def tokenize_punctuation(self,text:str)->str:
			#text = re.sub("<(.+?)>\[(.+?)\]", r"xx", text, re.DOTALL)
			#print(text)
			text = re.sub("([\,\.\!\:\?\;\\\/\\\(\)\[\]\"\'\`\~]+)([\n\s\r]|$)+",r" \1 ",text) #punctuation in new line
			text = re.sub("([\,\.\!\:\?\;\\/\\\(\)\[\]\"\'\`\~])([\,\.\!\:\?\;\\/\\\(\)\[\]\"\'\`\~])",r"\1 \2",text) #sepereate close punctuation e.g "'.' in "bla".
			text = re.sub("([\n\s\r]|$|^)+([\,\.\!\:\?\;\\\/\\\(\)\[\]\"'\`\~]+)",r" \2 ",text) #punctuation in new line
			text = re.sub("([\n\s\r]|$)+([ולבמהש])(\")([\u0590-\u05fe]{2,})",r" \2 \3 \4",text) #handle citation in the middle of word
			text = re.sub("([\s\n]+)|(^$)", "\n", text) #replace spaces with newlines
			text = re.sub("^\n", "", text) #get rid of double spaces
		#	text = re.sub("\n$", "", text) #replace spaces with newlines
			return text

	def replace_hypen(self,text):
		return text.replace("-", " - ")
	#def handlePunc(match):
	#	return ("\n" + match.group(0) + "\n").replace(" ","")


	def label_wiki_file(self,f):
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
				page_title = html.unescape(docStart.group(1))
				page_categories = html.unescape(docStart.group(2))
			elif docEndLine.match(line):
				labeledLines,page_wiki_id = self.handleLines(newData,page_title)
				file_data.append((page_categories, '\n'.join(labeledLines),page_wiki_id))
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

					line = ("labeled",(line,
					                           label.group(1),
					                           label.group(2),
					                           page_title,
					                           page_categories,
					                           is_first, is_last))

					is_first = False

				else:
					line = ("unlabeled",(line,))
					is_first = True
					is_last = True
				newData.append(line)

		return file_data

	def getNERLabel(self,labels, is_first, is_end):
		prefix = ""
		label = ""
		if (is_first and is_end):
			prefix = self.SINGLE_PRE
		elif (is_first):
			prefix = self.BEGIN_PRE
		elif (is_end):
			prefix = self.END_PRE
		else:
			prefix = self.INSIDE_PRE
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

	def handleLines(self, lines,title):
		title = title.replace(' ','_')
		titles = [l[1][2] for l in lines if l[0] == "labeled"]
		titles.append(title)
		wiki_data = self.mapperExt.get_entities_data_by_titles(titles)
		page_wiki_id = [l for l in wiki_data if l[1] == title]
		if not page_wiki_id:
			page_wiki_id = title #filler for pages without id
		else:
			page_wiki_id = page_wiki_id[0][0]
		labeledLines = []
		for line in lines:
			if(line[0] == "unlabeled"):
				new_line = self.handel_unlabeled_line(line[1][0].strip('\n'))
			else:
				new_line = self.handel_labeled_line(line[1],wiki_data)
			labeledLines.append(new_line)
		return labeledLines,page_wiki_id

	def handel_labeled_line(self,line_data,wiki_data):
		(line, text, label,
		 doc_title, doc_categories,
		 is_first, is_end) = line_data
		wiki_data_line = [l for l in wiki_data if l[1] ==label]
		wiki_id = None
		if not wiki_data_line:
			print('missing page:' + label)
		else:
			wiki_data_line = wiki_data_line[0]
			wiki_id = wiki_data_line[0]
			entity_labels = wiki_data_line[3]
		if (wiki_id):
			labels = [l for l in entity_labels.split(';') if l not in ['']]
			if (labels):
				# print(label)
				NERlabel = self.getNERLabel(labels, is_first, is_end)
				line = f"{text};{label};{wiki_id};{NERlabel}"
			else:
				line = f"{text};{label};{wiki_id};{self.EMPTY_LABEL}"
			return line
		else:
			return self.handel_unlabeled_line(text)

	def handel_unlabeled_line(self,line):
		line = f"{line};;;{self.EMPTY_LABEL}"
		return line





