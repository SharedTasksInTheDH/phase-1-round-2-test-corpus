import spacy
import sys
import os.path

infilename = sys.argv[1]
outdir = sys.argv[2]
outfilename = os.path.join(outdir,os.path.basename(sys.argv[1]))

fh = open(infilename, "r")
text = fh.read()
fh.close()

nlp = spacy.load("en_core_web_sm")
doc = nlp(text)
assert doc.has_annotation("SENT_START")
fh = open(outfilename, "w")
for sent in doc.sents:
  fh.write(sent.text)
  fh.write("\n")
fh.close()