import re

def text2BIOES_format(text:str)->str:
		#text = re.sub("<(.+?)>\[(.+?)\]", r"xx", text, re.DOTALL)
		#print(text)
		text = re.sub("([\,\.\!\:\?\;\\\/])[\n\s]",r" \1 ",text) #punctuation in new line
		text = re.sub("\s+", "\n", text) #replace spaces with newlines



		return text

def handlePunc(match):
	return ("\n" + match.group(0) + "\n").replace(" ","")



