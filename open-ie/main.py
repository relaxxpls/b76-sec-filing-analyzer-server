import scispacy
import spacy
from spacy.language import Language
from flair.data import Sentence
from flair.models import SequenceTagger
from transformers import pipeline
import os
import pickle
import pandas

nlp_web_sm = spacy.load("en_core_web_sm")
tagger_ner = SequenceTagger.load("flair/ner-english-ontonotes-fast")
tagger_np = SequenceTagger.load("flair/chunk-english")
qna = pipeline("question-answering")

def getAllNER(sent):
  sentence = Sentence(sent)
  tagger_ner.predict(sentence)
  allowedLabels=['MONEY','QUANTITY','DATE']
  spans=[]
  for entity in sentence.get_spans('ner'):
    if entity.tag in allowedLabels:
      spans.append(entity)
  return spans


def simple_phrases(sent):  
  op = nlp_web_sm(sent)
  phrase_list=[]
  allents=getAllNER(sent)
  for word in op:
    phrase=''
    if word.tag_ in ['NN','NNS','WP','PRP','NNP','NNPS'] and word.dep_ in ['nsubj','sbj','dsubj','nobj','dobj','obj']:
      token_children=[]
      for word1 in op:
        if word1.head.i==word.i:
          token_children.append(word1)
      for subtoken in token_children:
        if subtoken.tag_ in ['AFX','JJ','JJR','JJS','PDT','PRP$','WDT','WP$',] or subtoken.dep_ in ['compound']:
          phrase+=subtoken.text+' '
      if len(phrase)>0:
        phrase+=word.text+' '
    if len(phrase)>0:
      phrase_list.append(phrase)
  return phrase_list

def getLNP(sent,mark):
  op = nlp_web_sm(sent)
  final_phrase=[]
  for word in op:
    phrase=[]
    if word.i<mark and word.tag_ in ['NN','NNS','WP','PRP','NNP','NNPS'] and word.dep_ not in ['compound']:
      token_children=[]
      for word1 in op:
        if word1.head.i==word.i:
          token_children.append(word1)
      for subtoken in token_children:
        if subtoken.tag_ in ['AFX','JJ','JJR','JJS','PDT','PRP$','WDT','WP$',] or subtoken.dep_ in ['compound']:
          phrase.append(subtoken.i)
      phrase.append(word.i)
    if len(phrase)>0:
      final_phrase=phrase
  return final_phrase

      
def getRNP(sent,mark):
  op = nlp_web_sm(sent)
  final_phrase=[]
  for word in op:
    phrase=[]
    if word.i>mark and word.tag_ in ['NN','NNS','WP','PRP','NNP','NNPS'] and word.dep_ not in ['compound']:
      token_children=[]
      for word1 in op:
        if word1.head.i==word.i:
          token_children.append(word1)
      for subtoken in token_children:
        if subtoken.tag_ in ['AFX','JJ','JJR','JJS','PDT','PRP$','WDT','WP$',] or subtoken.dep_ in ['compound']:
          phrase.append(subtoken.i)
      phrase.append(word.i)
      
    if len(phrase)>0:
      final_phrase=phrase
      break
  return final_phrase

def ind2text(phrase,wordarr):
  textphrase=''
  for ind in phrase:
    textphrase+=wordarr[ind]+' '
  return textphrase

def complex_phrases_correct(sent):
  op = nlp_web_sm(sent)
  phrase_list=[]
  wordarr=[]
  allents=getAllNER(sent)
  for word in op:
    wordarr.append(word.text)
    if word.tag_ in ['IN','ADP']:
      phrase=[]
      lnp=getLNP(sent,word.i)
      lnp.sort()
      rnp=getRNP(sent,word.i)
      rnp.sort()
      if len(lnp)>0 and len(rnp)>0 and (word.i-lnp[-1]<3 and rnp[0]-word.i<3):
        phrase.extend(lnp)
        phrase.append(word.i)
        phrase.extend(rnp)
        phrase_list.append(phrase)
  text_phrase_list=[]
  for ph in phrase_list:
    text_phrase_list.append(ind2text(ph,wordarr))
  return text_phrase_list

rel_words = ['share','price','earn','amount','expense','income' , 'revenue','operat','financ','tax','market','fund','stock','asset','bond','settlement','amount','rate','valu','price','per','net','carry','expens','interest','lease','purchase','stock','income','tax','balanc','bill','customer','operat','allowance','net','revenue','standard','amortiz','securit','money','market','monit','fiscal','gross','benefit','exchange','debt','term','sheet','receiv','cash','flow','statement','account','polic','capita','anal','invest','eqity','interest','record','gain','sale','issu','note','principal','year','reduc','defer','deficit','acquisition','claim','insurance','cost','liabilit','change','charge','transact','quarter','agreement','grant','repay','loan','credit','trad','period','principal','compensat','proceed','stockholder','deduction','unvest','contribut','total','loss','off','recover','currency','adjust']
def getNER(sent):
  sentence = Sentence(sent)
  tagger_ner.predict(sentence)
  allowedLabels=['MONEY','QUANTITY','DATE']
  quantSpans=[]
  for entity in sentence.get_spans('ner'):
    if entity.tag in allowedLabels:
      quantSpans.append(entity)
  return quantSpans

def getPhrase(sen):
  phrases = []
  sen_np = Sentence(sen)
  tagger_np.predict(sen_np)
  
  phrases = [nc.text if len(nc.text.split(' '))>2 else '' for nc in sen_np.get_spans('np') ]
  while("" in phrases) :
    phrases.remove("")

  return phrases

def getQues(phrases):
  questions = []
  '''
  if tag == 'DATE' :
    for phrase in phrases:
      questions.append("When is "+phrase+" ?")

  if tag == 'MONEY' :
    for phrase in phrases:
      questions.append("How much is "+phrase+" ?")

  if tag == 'QUANTITY' :
    for phrase in phrases:
      questions.append("How much is "+phrase+" ?")
  '''
  for phrase in phrases:
    questions.append("What is "+phrase+"?")
  
  return questions

def generate_preds(sen):
  ques = []
  keys = []
  confidence = []
  values = []
  ners = getNER(sen)
  phrases=simple_phrases(sen)
  phrases.extend(complex_phrases_correct(sen))
  
  ques = getQues(phrases)
  
  for q in (ques) :
    cond = False      
    check = False

    for rel_word in rel_words :
      if rel_word in q.lower():
        check = True
        break
        
    if not check :
      continue


    ans = qna(question = q, context = sen)

    if ans['score'] < .7 :
      continue
    
    else :
      
      keys.append(q)
      values.append(ans['answer'])
      confidence.append(ans['score'])
  key_val = {'keys': keys , 'value': values , 'score' : confidence} 
  return key_val

company_name_list=pandas.read_csv('data/saas_list.csv', usecols=['Company'])['Company'].to_list()
for company_name in company_name_list:
  files_ = []
  for (root,dirs,files) in os.walk(f'/content/drive/MyDrive/Open IE/{company_name}', topdown=True):
    for file_ in files:
      files_.append(os.path.join(root,file_))

  lines_ = []
  for file_ in files_ :
    lines_in_files = []
    f = open(file_, "r",encoding='utf-8')
    for line_ in f:
      if len(line_) > 70:
        lines_in_files.append(line_.replace('\xa0',' '))
    lines_.append(lines_in_files)
    f.close()

  preds = []
  for lines__ in lines_:   #lines_ [lines of all files] line__ [lines in one file]

    preds_ = []
    for x in lines__:
      p = generate_preds(x[:-2])
      if len(p['keys']) == 0 :
        continue
      preds_.append(p)
    preds.append(preds_)
  print(company_name)
  for p in range(len(preds)):
    print(len(preds[p]))
    print(preds)
  with open(f'/content/drive/MyDrive/Open IE Pkl/{company_name}.pkl', 'wb') as f:
    pickle.dump(preds, f)