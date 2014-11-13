
# coding: utf-8

## Multi United Nations Corpus Sever Functions

# This is a list of all the service functions used to access and process the Multi UN corpus.

# In[177]:

import nltk
import re
import os
import chardet
from unidecode import unidecode
from progressbar import AnimatedMarker, Bar, BouncingBar,                            Counter, ETA, Percentage, ProgressBar, SimpleProgress, FileTransferSpeed

# PATH_TO_FILES = "C:\\Users\\Hassan\\Documents\\iSchool\\NLP\\United Nations\\multiUN.en\\un\\txt\\en"
# PATH_TO_XML_FILES="C:\\Users\\Hassan\\Documents\\iSchool\\NLP\\United Nations\\multiUN.en\\un\\xml\\en"

PATH_TO_FILES = "..\\data\\multiUN.en\\un\\txt\\en"
PATH_TO_XML_FILES="..\\data\\multiUN.en\\un\\xml\\en"


### Load Files

# In[178]:

def load_files(year = None, raw=True):
    years = []
    if year is None:
        years = [ year for year in os.listdir(PATH_TO_FILES) if not '.txt' in year or '_OLD_' in year]
    else:
        years = [str(year)]
    data = {}
    pbar = ProgressBar(widgets=[SimpleProgress(), Percentage(), Bar(), ETA()], maxval=len(years)).start()
    for i in range(len(years)):
        y = years[i]
        data[y] = load_files_by_year(y, raw)
        pbar.update(i+1)
    pbar.finish()
    return data


def load_files_by_year(year, raw=True):
    texts = []
    file_type = 'raw' if raw else 'txt'
    full_path = os.path.join(PATH_TO_FILES, year, file_type)        
    files = os.listdir(full_path)
    pbar2 = ProgressBar(widgets=[year, SimpleProgress(), Percentage(), Bar(), ETA()], maxval=len(files)).start()
    for i in range(len(files)):
        filename = os.path.join(full_path, files[i])
        with open(filename, 'r') as f:
            text = f.read()
            text = text.decode('utf-8') #the regular text was throwing an exception complaining about ascii
            texts.append(text) #Keeping each file in a seperate array element
            pbar2.update(i+1)
    pbar2.finish()
    return texts    


## Fix Unicode and Incomplete Sentences

# In[179]:

def fix_unicode(s):
    text = ''
    try:
        text = str(s)
        return text
    except:
        try:
#             print 'encoding:', chardet.detect(s)['encoding']
            text = s.encode(chardet.detect(s)['encoding'])
            return text
        except Exception, e:
#             print e
            try:
                text = unidecode(s)
                return text
#                 f.write(sent)
            except Exception, e2:
#                 print 'unidecode:', e2
                print 'error: ', e2
                print s
                return text
                pass
INCOMPLETE_SUFFIXES = ['Mr.', 'Ms.', 'Ch.']
def fix_incomplete_sentences(para):
    
    sents = []
    for i in range(len(para)):
        sent = para[i]
        out_sent=para[i]
        while any(sent.endswith(suffix) for suffix in INCOMPLETE_SUFFIXES) and i<(len(para)-1):
            i+=1
            out_sent+=' %s'%(para[i].strip())
            sent=para[i]
        sents.append(out_sent)
    return sents


## Load XML Files

# In[180]:

from lxml import etree
#data ={}
def load_xml_files(year = None, path = PATH_TO_XML_FILES, show_pbar=True):
    data = {}
    years = []
    if year is None:
        years = [ year for year in os.listdir(path)]
    else:
        years = [str(year)]
    
    if show_pbar:
        pbar = ProgressBar(widgets=[SimpleProgress(), Percentage(), Bar(), ETA()], maxval=len(years)).start()
    for i in range(len(years)):
        y = years[i]
        data[y] = load_xml_files_by_year(y, path, show_pbar)
        if show_pbar:
            pbar.update(i+1)
    if show_pbar:
        pbar.finish()
    return data

def load_xml_files_by_year(year, path = PATH_TO_XML_FILES, show_pbar = True):
    documents = {}
    full_path = os.path.join(path, year)    
#     print full_path
    files = [fname for fname in os.listdir(full_path) if fname.endswith('.xml')]
    if show_pbar:
        pbar2 = ProgressBar(widgets=[year, SimpleProgress(), Percentage(), Bar(), ETA()], maxval=len(files)).start()
    for i in range(len(files)):
        f = files[i]
        filename = os.path.join(full_path, f)
        documents[f]=[]
        #with open(filename, 'r') as f:
        tree = etree.parse(filename)
        root = tree.getroot()
        xparas =  root.getchildren()[0].getchildren()[0].getchildren()
        for xpara in xparas:
           documents[f].append([fix_unicode(sent.text.strip()) for sent in xpara if len(sent.text.strip())>0])
        #text = f.read()
        #text = text.decode('utf-8') #the regular text was throwing an exception complaining about ascii
        #texts.append(text) #Keeping each file in a seperate array element
        if show_pbar:
            pbar2.update(i+1)
    if show_pbar:
        pbar2.finish()
    return documents



def flatten_document_structure_paragraphs(doc_dict):
    print 'flattening paragraphs'
    flat = [fix_incomplete_sentences(para) for year in doc_dict for doc in doc_dict[year] for para in doc_dict[year][doc]]
    return flat
def flatten_document_structure(doc_dict):
    print 'flattening'
    text = [fix_incomplete_sentences(para) for year in doc_dict for doc in doc_dict[year] for para in doc_dict[year][doc]]
    text = [sent for para in text for sent in para]
        
    return text
   

def flatten_document_structure_long(doc_dict):
    return flatten_document_structure(doc_dict)
#     text = [ sent for year in doc_dict for doc in doc_dict[year] for para in doc_dict[year][doc] for sent in para]


### Sentence Tokenizers

# In[181]:

sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
def tokenize_sentences(text, use_nltk_tokenizer = False ):
    sents = []
    if use_nltk_tokenizer:

        sents = sent_tokenizer.sentences_from_text(text)
    else:
        #sents = "\n".join(texts) # join all the documents into one big string
        #split the document by \n and remove any empty line and extra whitespace
        sents = [sent.strip() for sent in text.split('\n') if len(sent.strip())>0] 
    return sents
def tokenize_sentences2(text, use_nltk_tokenizer = False ):
    sents = []
    global sent_tokenizer
    if use_nltk_tokenizer:
        sents = sent_tokenizer.sentences_from_text(text)
    else:
        #sents = "\n".join(texts) # join all the documents into one big string
        #split the document by \n and remove any empty line and extra whitespace
        paragraphs = [sent.strip() for sent in text.split('\n') if len(sent.strip())>0] 
        #some sentence boundaries are wrong. Some text is split on numbered lists and other abbreviations. hence the join
        sents = [" ".join(sent) for sent in [sent_tokenizer.sentences_from_text(para) for para in paragraphs]]
    return sents


## Sentence Statistics

# In[182]:

def get_sentence_count(sentences):
    return len(sentences)

def get_average_words_per_sentence(sentences):
    
    return sum([len(sent.split(' ')) for sent in sentences])/float(len(sentences))

def get_average_characters_per_sentence(sentences):
    return sum([len(sent) for sent in sentences])/float(len(sentences))

def get_longest_sentence_by_words(sentences):
    return max(sentences, key=lambda w:len(w)).split(" ")

def get_longest_sentence_by_characters(sentences):
    return max(sentences, key=lambda w:len(w))

def print_sentence_statistics(sentences):
    print '%-32s' % 'Info type', '%-16s' % 'Value',  '\n----------------------------------------'
    print '%-32s' % 'number of sentences', '%-16d' % len(sentences)
    print '%-32s' % 'average sentence length(words)', '%-16.2f' % get_average_words_per_sentence(sentences)
    print '%-32s' % 'average sentence length(letters)', '%-16.2f' % get_average_characters_per_sentence(sentences)
    print '%-32s' % 'longest sentence (words)', '%-16s' % len(get_longest_sentence_by_words(sentences))
    print '%-32s' % 'longest sentence (letters)', '%-16s' % len(get_longest_sentence_by_characters(sentences))


## Word Tokenizer

# In[183]:

from nltk.corpus import stopwords
english_stopwords = stopwords.words('english')

def tokenize_text(text, alnum_only = False,  alpha_only = False,remove_stopwords=False, use_pattern = 1):
    pattern1 = ["\w+[\-|']\w+", #words joined with '-' or words with ' in them \
               "(\w+/)+\w+", #document references and words that are seperated with '\' \
               "\([\w+\s*]\)", #words with parenthesis in them. this will exclude parenthisis \
               "\w+"]

    pattern2 =["(?x)([A-Z]\.)+",
               "\w+([-']\w+)*",
               "\$?\d+(\.\d+)?%?",
               "\.\.\.",
               "[.,?;]+"]
    pattern  = pattern1 if use_pattern ==1 else pattern2
    pattern = "|".join(pattern)
    text = " ".join(text) if isinstance(text, list)== True else text
    tokens = nltk.regexp_tokenize(text,pattern)
    tokens =  [token for token in tokens                   if ((remove_stopwords and token.lower() not in english_stopwords) or not remove_stopwords)                   and ((alnum_only and token.isalnum()) or not alnum_only)
                  and ((alpha_only and token.isalpha()) or not alpha_only)]
    return tokens

def tokenize_sentence_text(sentences, alnum_only = False, alpha_only = False, remove_stopwords=False, use_pattern = 1, show_pbar = False):
    sent_tokens = []
    if show_pbar:
        pbar = ProgressBar(widgets=["Tokenizing senteces", SimpleProgress(), Percentage(), Bar(), ETA()], maxval=len(sentences)).start()
    i = 0
    for sent in sentences:
        sent_token = tokenize_text(sent, alnum_only=alnum_only, alpha_only = alpha_only, remove_stopwords=remove_stopwords, use_pattern=use_pattern)
        sent_tokens.append(sent_token)
        i+=1
        if show_pbar:
            pbar.update(i)
    if show_pbar:
        pbar.finish()
    return sent_tokens


## Word Statistics

# In[184]:

def get_word_count(tokens):
    return len(tokens)

def get_unique_word_count(tokens):
    return len(set(tokens))

def get_average_word_length(tokens):
    return sum([len(token) for token in tokens])/float(len(tokens))

def get_longest_word(tokens, ignore_join_words = True):
    if ignore_join_words:
        return ", ".join([max([token for token in tokens if token.isalpha()], key=lambda token:len(token))])
    else:
        return ", ".join([max([token for token in tokens], key=lambda token:len(token))])
def print_word_stats(tokens):
    print '%-32s' % 'Info type', '%-16s' % 'Value'
    print '%-32s' % 'number of words', '%-16d' % get_word_count(tokens)
    print '%-32s' % 'number of unique words', '%-16d' % get_unique_word_count(tokens)
    print '%-32s' % 'average word length', '%-16.2f' % get_average_word_length(tokens)
    #exclude joint words for longest word
    print '%-32s' % 'longest single word', '%-16s' % get_longest_word(tokens, ignore_join_words = True)
    print '%-32s' % 'longest word', '%-16s' % get_longest_word(tokens, ignore_join_words = False)


## Part of Speech Taggers

# In[185]:

def build_backoff_tagger (train_sents, default='NN'):
    t0 = nltk.DefaultTagger(default)
    t1 = nltk.UnigramTagger(train_sents, backoff=t0)
    t2 = nltk.BigramTagger(train_sents, backoff=t1)
    return t2
def get_brown_tagger(category = None):
    if category:
        return build_backoff_tagger(brown.tagged_sents(categories=category))
    else:
        return build_backoff_tagger(brown.tagged_sents())
def get_default_treebank_tagger():
    return nltk.data.load('taggers\maxent_treebank_pos_tagger\english.pickle')

def tag_pos_sentences(tokenized_sentences, tagger=get_default_treebank_tagger(), show_pbar = False):
    if show_pbar:
        pbar = ProgressBar(widgets=[SimpleProgress(), Percentage(), Bar(), ETA()], maxval=len(tokenized_sentences)).start()
    i = 0
    tagged_sentences = []
    for sent in tokenized_sentences:
        tagged_sentences.append(tagger.tag(sent))
        i+=1
        if show_pbar:
            pbar.update(i)
    if show_pbar:
        pbar.finish()
    return tagged_sentences
    


## Text Chunker

# In[186]:

def get_chunker(grammer=None, tag_set=None):
    if not grammer:
        if tag_set is None or type=='treebank':
            grammer = r"""PNS: {<DT|JJ|NN|NNS|NNP|NNPS>+<IN>*<DT|JJ|NN|NNS|NNP|NNPS>*<NNP|NNPS><CD>*}
                          {<DT|JJ|NN|NNS|NNP|NNPS>*<NNP|NNPS><CD>*}
                            """
        elif tag_set=='brown':
            DJNP = "<DT|JJ|JJ\$|JJ+JJ|JJR+CS|JJS|JJT|JJ-TL|JJ-HL|FW-JJ|FW-JJR|VBG-TL|VBN-TL"                +"|NN|NN\$|NN\$-TL|NN-HL|NN-TL|NNS|NNS-HL|NNS-TL|NNS-TL-HL|FW-NN|FW-NNS|FW-NN-TL"                +"|NP|NP\$|NP-HL|NP-TL|NPS|FW-NP|FW-NPS>"
            #proper nouns
            NPS = "<NP|NP\$|NP-HL|NP-TL|NPS|FW-NP|FW-NPS>" 

            grammer = r"PNS: {"+DJNP+"+<IN|IN-TL>*"+DJNP+"*"+NPS+"<CD|MD>*}"+"\n{"+DJNP+"*"+NPS+"<CD|CD-TL|MD>*}" 
        elif tag_set=='brown_simple':
            grammer = r"""PNS: {<DET|ADJ|N>*<NP><NUM>*}
                            {<DET|ADJ|N>+<IN>*<DET|ADJ|N><NP><NUM>*}"""
        
    return nltk.RegexpParser(grammer)

def get_chunks(tagged_sents, chunker=get_chunker(), target = 'PNS',                      print_output=True, limit=0, randomize= False, show_pbar = False):
    chunks = []
    limit = limit if limit>0 else len(tagged_sents)
    i=0
    if show_pbar:
        pbar = ProgressBar(widgets=[SimpleProgress(), Percentage(), Bar(), ETA()], maxval=limit).start()
    import random
    for index in range(limit):
        sent_index = random.randint(0, len(tagged_sents)-1) if randomize else index
        sent = tagged_sents[sent_index]
        result = chunker.parse(sent) 
        phrase_leaves = [subtree.leaves() for subtree in  result.subtrees() if subtree.node==target]
        words = [" ".join([word.encode('utf-8') for (word,tag) in leaf]) for leaf in phrase_leaves ]
        if len(words)>0:
            chunks.append(words)
        if print_output:
            print "\t".join([word for (word, tag) in sent])
            print "\t".join([tag for (word, tag) in sent])
            print "\n".join(['%d\t%s'%(j+1, words[j]) for j in range(len(words))])
            print '\n'
#         print result
        i+=1
        if show_pbar:
            pbar.update(i)
    if show_pbar:
        pbar.finish()
    return [phrase for phrases in chunks for phrase in phrases]


## Printing Functions

# In[187]:

def print_FreqDist(fd, limit =0):
    if limit == 0:
        limit = len(fd.items())
    print "\n".join(["%d\t%s"%( value, word) for (word, value) in fd.items()[:limit]])
#prints multiple frequency distribution next to each other to compare results.
def print_FreqDists(fds, titles=None, limit = 50, csv=False):
    lines = ''
    html_str =''
    if limit ==0:
        limit = max([len(fd) for fd in fds])
    titles = titles if titles else [i for i in range(len(fds))]
    lines+=",".join(['phrase %s,frequency %s'%(t,t) for t in titles])+'\n'
    for i in range(limit):
        line = '%d'%(i+1)
        for fd in fds:
            key = ''
            val = 0
            if i < len(fd.items()):
                key =fd.items()[i][0]
                val = fd.items()[i][1]
            if csv:
                line='%s,%s,%d'%(line,key,val)
            else:
                line += '%d\t%s\t'%(val, key)
       
#         print line
        lines+='%s\n'%line
    return lines

def print_csv_table(csv_lines):
    import pandas, io
    if isinstance(csv_lines, list):
        csv_lines = str("\n".join(csv_lines))
    plines= pandas.read_csv(io.BytesIO(csv_lines))
    plines

def print_pos_tagged_sentences(tagged_sentences):
    formatted_sents = []
    import pandas, io
    for sent in tagged_sentences:
        words = [word for (word, tag) in sent]
        tags = [tag for (word, tag) in sent]
        csv_line = "%s\n%s"%(",".join(words), ",".join(tags))
        plines=pandas.read_csv(io.BytesIO(str(csv_line).decode('utf-8')))
        plines
        formatted_sents.append(",".join(words))
        formatted_sents.append(",".join(tags))
#         formatted_sents.append('\n')
#     print "\n".join(formatted_sents)
#     print_csv_table(formatted_sents)


# In[188]:

# files = load_xml_files('ENERGY')


# In[189]:

# sents = flatten_document_structure_long(files)
# sents[:15]

