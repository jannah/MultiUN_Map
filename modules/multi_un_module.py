
# coding: utf-8

## Multi United Nations Corpus Sever Functions

# This is a list of all the service functions used to access and process the Multi UN corpus.

# In[11]:

import nltk
import re
import os
import chardet
import string
import inspect
from unidecode import unidecode
from progressbar import AnimatedMarker, Bar, BouncingBar,                            Counter, ETA, Percentage, ProgressBar, SimpleProgress, FileTransferSpeed
from nltk.corpus import brown


## Progress Bar Settings

# In[12]:

show_pbars = True
def disable_pbars():
    print 'Disabling progress bars'
    global show_pbars
    show_pbars = False
def is_show_pbars():
    global show_pbars
#     print 'show pbars is ' , show_pbars
    return show_pbars


### Load Data Path

# In[13]:

FILENAME = inspect.getframeinfo(inspect.currentframe()).filename
F_PATH = os.path.dirname(os.path.abspath(FILENAME))
ROOT_CORPUS_DIR = ''
RELATIVE_PATH_TO_XML = 'data/multiUN.en/un/xml/en'
RELATIVE_PATH_TO_TXT = 'data/multiUN.en/un/txt/en'
PATH_TO_FILES = os.path.abspath(os.path.join(F_PATH, '..', RELATIVE_PATH_TO_TXT))
# PATH_TO_XML_FILES=os.path.join("..","data","multiUN.en","un","xml","en")
PATH_TO_XML_FILES =  os.path.abspath(os.path.join(F_PATH, '..', RELATIVE_PATH_TO_XML))


## Fix Unicode and Incomplete Sentences

# In[14]:

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


### Load Files

# In[15]:

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
        data.update(load_files_by_year(y, raw))
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


## Load XML Files

# In[16]:

from lxml import etree
#data ={}
def load_xml_files(year = None, path = PATH_TO_XML_FILES, show_pbar=None, content=True):
    show_pbar = show_pbar if show_pbar is not None else is_show_pbars()
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
        data.update(load_xml_files_by_year(y, path, show_pbar, content))
        if show_pbar:
            pbar.update(i+1)
    if show_pbar:
        pbar.finish()
    return data

def load_xml_files_by_year(year, path = PATH_TO_XML_FILES, show_pbar = None, content=True):
    show_pbar = show_pbar if show_pbar is not None else is_show_pbars()
    documents = {}
    full_path = os.path.join(path, year)    
#     print full_path
    files = [fname for fname in os.listdir(full_path) if fname.endswith('.xml')]
    if show_pbar and len(files)>0:
        pbar2 = ProgressBar(widgets=[year, SimpleProgress(), Percentage(), Bar(), ETA()], maxval=len(files)).start()
    for i in range(len(files)):
        f = files[i]
        filename = os.path.join(full_path, f)
        documents[f] = load_xml_file(filename=filename, content=content)
        if show_pbar:
            pbar2.update(i+1)
    if show_pbar and len(files)>0:
        pbar2.finish()
    return documents

def get_year_from_filename(filename):
    sep = '\\' if '\\' in filename else '/'
    return str(filename.split(sep)[-2:-1][0])


def load_xml_file(filename = None, content=True, year = None):
    f = {}
    tree = etree.parse(filename)
    root = tree.getroot()
    f=dict(root.attrib)
    f['year'] = year if year else get_year_from_filename(filename)
    if content:
        xparas =  root.getchildren()[0].getchildren()[0].getchildren()
        content = []
        for xpara in xparas:
          content.append([fix_unicode(sent.text.strip()) for sent in xpara if len(sent.text.strip())>0])
        f['content'] =  content
    return f

# def flatten_document_structure_paragraphs(doc_dict):
#     print 'flattening paragraphs'
#     flat = [fix_incomplete_sentences(para) for doc in doc_dict for para in doc_dict[doc]['content']]
#     return flat

 


## Load Document Map

# 

# In[17]:

import json, zipfile
RELATIVE_PATH_TO_MAP = 'util/MUN_MAP.zip'
PATH_TO_MAP = os.path.abspath(os.path.join(F_PATH, '..', RELATIVE_PATH_TO_MAP))
map_zip = zipfile.ZipFile(PATH_TO_MAP)
MUN_MAP = None
MAP_FILE = 'map.json'

DOC_ID_MAP = None


# In[39]:

def change_map_file(map_file=MAP_FILE):
    global MAP_FILE
    MAP_FILE = map_file
    print 'Chaged map file to ', map_file
    
    
def load_doc_map(path_prefix=None):
    global MUN_MAP
    global DOC_ID_MAP
    if MUN_MAP is None:
        MUN_MAP = json.loads(map_zip.read(MAP_FILE,'r'))
        DOC_ID_MAP = dict(sorted([(MUN_MAP[doc]['attributes']['id'].strip(), doc) for doc in MUN_MAP], reverse=True))
        if path_prefix is not None:
            print 'Changing paths to ', path_prefix
            for k,doc in MUN_MAP.iteritems():
                MUN_MAP[k]['attributes']['path'] = '%s/%s'%(path_prefix, MUN_MAP[k]['attributes']['path'])

        
#     return MUN_MAP


def validate_search_term(doc, term=None, doc_name=None, doc_id = None, doc_n=None, filename = None, title=None):
    load_doc_map()
    if doc is not None and doc==doc_name:
        return True
    if doc_id is not None:
        return doc_id in DOC_ID_MAP
#     if term is None and doc_name is not None:
#         term = doc_name
    
    return (
                term is not None and
                (term in MUN_MAP[doc]['attributes']['n']
                or term in MUN_MAP[doc]['attributes']['id']
                or doc.endswith(term)
                or ( 'scrape' in MUN_MAP[doc]  
                 and (( 'Title' in MUN_MAP[doc]['scrape'] and term.lower() 
                       in (MUN_MAP[doc]['scrape']['Title']).lower())
                      or ('Subjects' in MUN_MAP[doc]['scrape'] and term.lower() 
                          in " ".join(MUN_MAP[doc]['scrape']['Subjects']).lower()))
                    )
                )
                or (title is not None 
                    and 'scrape' in MUN_MAP[doc]   
                    and 'Title' in MUN_MAP[doc]['scrape'] 
                    and title.lower() in MUN_MAP[doc]['scrape']['Title'].lower())
                or doc_n==MUN_MAP[doc]['attributes']['n']
                or doc_id == MUN_MAP[doc]['attributes']['id']
            )


def load_contents(docs):
    if docs is not None:
        for doc in docs:
            path = docs[doc]['attributes']['path']
            doc_data = load_xml_file(filename = path, content=True)
            if doc_data: 
                docs[doc]['content'] = doc_data['content']
    return docs


def get_documents(term = None, doc_name = None, doc_id=None, doc_n=None, filename = None, title=None, limit = None, 
                  include_content = False):
    load_doc_map()
    if doc_name is not None and doc_name in MUN_MAP:
            result =  {doc_name:MUN_MAP[doc_name]}
    else:
        result = {}
        counter = 0
        term = term if term is not None else doc_name
        for doc in MUN_MAP:
            if validate_search_term(doc, term, doc_name, doc_id, doc_n, filename, title):
                result[doc] = MUN_MAP[doc]
                if 'links' not in result[doc]:
                    print result[doc]
                    result[doc]['links']=[]
                counter+=1
            if limit is not None and counter>= limit:
                break
#     order =  sorted(result, key=lambda d: len(result[d]['links']),reverse=True )
#     print order
#     result = dict([(d, result[d]) for d in order])
    if include_content:
        result = load_contents(result)
    return result

def get_document(term = None, doc_name = None, doc_id=None, doc_n=None, filename = None, title=None, include_content = False):
    load_doc_map()
    if doc_name and doc_name in MUN_MAP:
            result = {doc_name:MUN_MAP[doc_name]}
    else:
#         term = term if term is not None else doc_name
        try:
            result =  next({doc:MUN_MAP[doc]} for doc in MUN_MAP if validate_search_term(doc, term, doc_name, doc_id, doc_n, filename, title))
        except Exception,e:
            return None
    if include_content:
        result = load_contents(result)
    return result


def get_subjects(docs=None):
    load_doc_map()
    subjects = []
    if docs is not None:
        subjects_list = [MUN_MAP[doc]['scrape']['Subjects']
            for doc in docs 
            if 'scrape' in MUN_MAP[doc]
            and 'Subjects' in MUN_MAP[doc]['scrape']]
    else:
        subjects_list = [MUN_MAP[doc]['scrape']['Subjects']
            for doc in MUN_MAP 
            if 'scrape' in MUN_MAP[doc]
            and 'Subjects' in MUN_MAP[doc]['scrape']]
    subjects = [ subject for subjects in subjects_list for subject in subjects]
    return subjects


### Extract Paragraphs and Sentences

# Functions to extract sentence or paragraph-sentence lists from document dictionary

# In[19]:

def extract_paragraphs(doc_dict, merge_paragraphs=False):
    flat = [fix_incomplete_sentences(para) for doc in doc_dict for para in doc_dict[doc]['content']]
    if merge_paragraphs:
        flat = [" ".join(para) for para in flat]
    return flat

def extract_sentences(doc_dict):
    print 'flattening'
    text = [fix_incomplete_sentences(para) for doc in doc_dict for para in doc_dict[doc]['content']]
    text = [sent for para in text for sent in para]
        
    return text


### Sentence Tokenizers

# In[20]:

sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
def parse_sentences_from_text(text, use_nltk_tokenizer = False ):
    sents = []
    if use_nltk_tokenizer:
        sents = sent_tokenizer.sentences_from_text(text)
    else:
        #split the document by \n and remove any empty line and extra whitespace
        sents = [sent.strip() for sent in text.split('\n') if len(sent.strip())>0] 
    return sents


## Sentence Statistics

# In[21]:

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

# Create word tokens from sentences
# * pattern1: no punctuation
# * pattern2: include punctuations

# In[22]:

from nltk.corpus import stopwords
english_stopwords = stopwords.words('english')

def tokenize_text(text, alnum_only = False,  alpha_only = False,remove_stopwords=False, use_pattern = 2):
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


# tokenize words but keep sentences seperate
def tokenize_sentence_text(sentences, alnum_only = False, alpha_only = False, remove_stopwords=False, 
                           use_pattern = 1, show_pbar=None):
    show_pbar = show_pbar if show_pbar is not None else is_show_pbars()
    
    sent_tokens = []
    if show_pbar:
        pbar = ProgressBar(widgets=["Tokenizing sentences", SimpleProgress(), Percentage(), Bar(), ETA()], maxval=len(sentences)).start()
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

# In[23]:

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

# 
# This is a manually tagged tagger of cities and countries from the gazetteers corpus. I also appended a special tag or United Nations because the tagger kept detecting United as a verb. 
# 
# I am using custom tags (NPLOC and NPORG) because I don't want them to be mixed with other NPs while having the chunker detect them as a sub class of NP. United Nations was especially important because it occurs alot and is United is flagged as a verb which throws off the chunker, especially the verb object chunker.
# 
# I experimented with The regex tagger only support 100 groups max and the it won't deal with tokenized sentences

# In[24]:

#location/organization tagger
def get_location_tagger_tags():
    from nltk.corpus import gazetteers as gz
    pos_tags_locations =[[('United', 'NPORG'), ('Nations', 'NPORG')],
                         [('Working', 'NPORG'), ('Party', 'NPORG')]]
    pos_tags_locations +=[[(word, 'NPLOC') for word in words.split(' ') if word not in english_stopwords] for words in gz.words()]
    '''
#   pos_tags_locations += [[(words, 'NPLOC') ]for words in gz.words() ]
#   pos_tags_locations = [(words, 'NPLOC') for words in [gzwords for gzwords in gz.words() if len(gzwords.split(' '))>2]][:90]
    pos_tags_locations+=[(r'\w* Republic \w*', 'NPLOC'),(r'\w* Kingdom \w*', 'NPLOC'),('United Nations', 'NPORG'),('Working Party', 'NPORG')]
    '''
    
    return pos_tags_locations


#the tagger here can be a 3 stage tagger or 5 state if the location tagger is included
#note that the location tagger is used first to ensure the location/orgainzations are detected properly
def build_backoff_tagger (train_sents, default='NN', include_location_tagger=False):
    t0 = nltk.DefaultTagger(default)
    t1 = nltk.UnigramTagger(train_sents, backoff=t0)
    t2 = nltk.BigramTagger(train_sents, backoff=t1)
    t4=t2
    if include_location_tagger:
        t3 = nltk.RegexpTagger([(r'UN[A-Z]*', 'NPORG')], backoff=t2)
        t4 = nltk.UnigramTagger(get_location_tagger_tags(), backoff=t3) #tag using the custom tagger first if requested
    return t4


def build_location_tagger():
    t0 = nltk.DefaultTagger('U')
    return nltk.BigramTagger(get_location_tagger_tags(), backoff=t0)


def get_brown_tagger(category = None, include_location_tagger=False):
    if category:
        return build_backoff_tagger(brown.tagged_sents(categories=category), include_location_tagger=include_location_tagger)
    else:
        return build_backoff_tagger(brown.tagged_sents(), include_location_tagger=include_location_tagger)

    
def get_default_treebank_tagger():
    return nltk.data.load('taggers/maxent_treebank_pos_tagger/english.pickle')


#Tag the sentences based on the selected tagger
def tag_pos_sentences(tokenized_sentences, tagger=get_default_treebank_tagger(), show_pbar=None):
    show_pbar = show_pbar if show_pbar is not None else is_show_pbars()
    if show_pbar:
        pbar = ProgressBar(widgets=["tagging sentences", SimpleProgress(), Percentage(), Bar(), ETA()],
                           maxval=len(tokenized_sentences)).start()
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

# My pride an joy chunker tries to do alot. I experimented heavily with it in previous assignments to ensure it captures complex objects. I am targeting 2 main classes:
# * **PNS**: Proper nouns which in this case can be as long as 7 words for some UN organizations
# * **VNS**: Verb noun subjects (or who did what)

# In[25]:

def remove_punctuation(text):
    return "".join(c for c in text if c not in string.punctuation)


#it assumes brown tag set and proper nouns as default parameters. I found brown to be best in detecting proper nouns
def get_chunker(grammer=None, tag_set=None, target='PNS'):
    if not grammer:
        #not used here
        if tag_set=='treebank':
            grammer = r"""PNS: {<DT|JJ.*|N.*>+<IN>*<DT|J.*|N.*>*<NNP.*><CD>*}
                          {<DT|J.*|N.*>*<NNP.*><CD>*}
                            """
        elif tag_set is None or tag_set=='brown':
            if target=='PNS':
                #words that precede or folllow proper nouns that are part of it (e.g. UN commission for xxx)
                DJNP = "<DT|J.*|FW-J.*|VBG.*|VBN.*"                    +"|N.*|FW-N.*"                    +"|NP.*|FW-NP.*>"
                #proper nouns
                NPS = "<NP.*|FW-NP.*>" 

                grammer = r"PNS: {"+DJNP+"+<IN.*>*"+DJNP+"*"+NPS+"<CD|MD>*}"+"\n{"+DJNP+"*"+NPS+"<CD|CD-TL|MD|N.*>*}"
            
            elif target=='VNS':
                #verbs and teh different nouns that come before it or after it
                grammer  = r"""VNS: {<N.*|J.*>*<VB.*>+<CD|TO|IN|CC|DT|PRP>*<DT|J.*|N.*>*<N.*|J.*>}
                        {<N.*|J.*>+<CD|TO|IN|CC|DT|PRP>*<DT|J.*|N.*>*<VB.*>+}
                         """
        #not used here
        elif tag_set=='brown_simple':
            grammer = r"""PNS: {<DET|ADJ|N>*<NP><NUM>*}
                            {<DET|ADJ|N>+<IN>*<DET|ADJ|N><NP><NUM>*}"""
    return nltk.RegexpParser(grammer)


# returns chunk trees based on teh chunker and target chosesn
# randomize and limit are for testing purposues. They allow the chunker to run on a limited number of random sentences
def get_chunks(tagged_sents, chunker=get_chunker(), target = 'PNS', limit=0, randomize= False, show_pbar=None):
    show_pbar = show_pbar if show_pbar is not None else is_show_pbars()
    chunks = []
    limit = limit if limit>0 else len(tagged_sents)
    i=0
    if show_pbar:
        pbar = ProgressBar(widgets=["Chunking ", SimpleProgress(), Percentage(), Bar(), ETA()], maxval=limit).start()
    import random
    for index in range(limit):
        sent_index = random.randint(0, len(tagged_sents)-1) if randomize else index
        sent = tagged_sents[sent_index]
        if len(sent)>0:
            result = chunker.parse(sent) 
            chunks.append(result)
        i+=1
        if show_pbar:
            pbar.update(i)
    if show_pbar:
        pbar.finish()
    return chunks


#extracts the target chunks from the tree. I seperated this because in some cases I need the trees
def extract_target_from_chunks(raw_chunks, target='PNS',print_output=False, print_leaves = False):
    chunks=[]
    for result in raw_chunks:
        phrase_leaves = [subtree.leaves() for subtree in  result.subtrees() if subtree.node==target]
        if print_leaves:
            print phrase_leaves
        words = [" ".join([word for (word,tag) in leaf]) for leaf in phrase_leaves ]
        if len(words)>0:
            chunks.append(words)
        if print_output:
            print "\t".join([word for (word, tag) in sent])
            print "\t".join([tag for (word, tag) in sent])
            print "\n".join(['%d\t%s'%(j+1, words[j]) for j in range(len(words))])
            print '\n'
        
    return [phrase for phrases in chunks for phrase in phrases]


#flattens the trees but doesn't remove anything. It only groups the target one tuple. 
# This helps generate collocations based on complex chunker grammer which was very useful
def flatten_chunks(chunks, target='PNS'):
    flat_chunks = []
    for chunk in chunks:
        flat_chunk=[]
        for n in chunk:
            if isinstance(n, tuple):
                flat_chunk.append(n)
            elif isinstance(n, nltk.tree.Tree):
                flat_node = (" ".join([word for (word, tag) in n.leaves()]), n.node)
                flat_chunk.append(flat_node)
        flat_chunks.append(flat_chunk)
    return flat_chunks



### Process Chunks to generate chunk Frequency Distrubtions

# * Named Entities using a multi stage chunker
# * Verb objects

# In[26]:


def process_chunks(sentences=None, sent_tokens=None, tagged_sentences = None,  remove_months = True, tagger = None, return_print = True):
 if not tagged_sentences:
     sent_tokens = sent_tokens if sent_tokens else          tokenize_sentence_text(sentences, alnum_only=False, remove_stopwords=False, use_pattern = 2)
     tagger = get_brown_tagger(include_location_tagger=True)
 tagged_sentences = tagged_sentences if tagged_sentences else tag_pos_sentences(sent_tokens, tagger=tagger)
 #get the proper noun chunks from teh chunker
 nchunks = get_chunks(tagged_sentences, chunker=get_chunker(tag_set='brown', target='PNS'), target = 'PNS')
 nchunks = extract_target_from_chunks(nchunks, target='PNS')
 # there are many month names mentioned in the FrewDist, I am removing them because I don' think they add much value
 if remove_months:
     import calendar
     nchunks = [chunk for chunk in nchunks if len(remove_punctuation(chunk))>1 and chunk not in calendar.month_name]
 
 vchunks = get_chunks(tagged_sentences, chunker=get_chunker(tag_set='brown', target='VNS'), target = 'VNS')
 vchunks = extract_target_from_chunks(vchunks, target='VNS')
#     vchunks = [chunk for chunk in vchunks if chunk not in nchunks]
 nchunks_fd = nltk.FreqDist(nchunks)
 vchunks_fd = nltk.FreqDist(vchunks)
 if return_print:
     return print_FreqDists([nchunks_fd, vchunks_fd], titles=['Proper Nouns', 'Verb Objects'], csv=True)
 else:
     return nchunks_fd.items(), vchunks_fd.items()


## Collocations 

# There are two collocation implementations here:
# * word based: collocation of individual words
# * chunk based: collocation using a whole chunker grammer element (e.g. PNS). This will treat the whole element as one words and generate collocation of other words with it. this helps especially when dealing with multi-words country or organization names
# 
# The output is four finders nbests:
# (bigram, trigram) x (pmi, chi_sq)

# In[27]:

from nltk.collocations import *
#find pure word frequency collocations
#it doesn't matter whether I pass tagged sentences or not since I am focusing on words only
def get_collocations(sentences=None, sent_tokens=None, filter_limit = 3, finder_limit = 20):
#     from nltk.collocations import *
    sent_tokens = sent_tokens if sent_tokens else tokenize_sentence_text(sentences,alpha_only = True,                                                                         remove_stopwords=True, use_pattern = 1)
    word_tokens = [word for sent in sent_tokens for word in sent]
#     print word_tokens[:5]
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    trigram_measures = nltk.collocations.TrigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(word_tokens)
    finder3 = TrigramCollocationFinder.from_words(word_tokens)
    finder.apply_freq_filter(filter_limit)
    finder3.apply_freq_filter(filter_limit)
    #print 4 finders (bigram, trigram) x (pmi, chi_sq)
    f1= finder.nbest(bigram_measures.pmi, finder_limit)
    f2= finder.nbest(bigram_measures.chi_sq, finder_limit)
    f3= finder3.nbest(trigram_measures.pmi, finder_limit)
    f4= finder3.nbest(trigram_measures.chi_sq, finder_limit)
    return f1, f2,f3,f4

#get the colloations based on chunks    
def get_chunked_collocations(sentences=None,tagged_sentences=None, tagger=None,                              target='PNS', chunker = None, filter_limit = 3, finder_limit = 20):

    #I can pass pre-tagged sentences if needed
    if tagger is None:
        get_brown_tagger(include_location_tagger=True)
    if sentences:
        sent_tokens = tokenize_sentence_text(sentences, alnum_only=False, remove_stopwords=False, use_pattern = 2)
        tagged_sentences = tag_pos_sentences(sent_tokens, tagger=tagger)
    
    chunker = chunker if chunker else get_chunker(tag_set='brown', target = target)
    chunks = get_chunks(tagged_sentences,chunker=chunker, target = target)
    flat_chunks = flatten_chunks(chunks, target=target)
    flat_chunk_tokens = [token for flat_chunk in flat_chunks for token in flat_chunk]
    
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    trigram_measures = nltk.collocations.TrigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(flat_chunk_tokens)
    finder3 = TrigramCollocationFinder.from_words(flat_chunk_tokens)
    
    #after some testing, I found that many collocations are numeric so I am filtering out non alpha words
    #This filters out any pairs that don't included the target chunk grammer
    finder.apply_ngram_filter(lambda (w1, t1), (w2,t2): target not in (t1,t2) or not w1.isalpha() or not w2.isalpha())
    finder3.apply_ngram_filter(lambda (w1, t1), (w2,t2), (w3, t3):                                target not in (t1,t2,t3) or not w1.isalpha() or not w2.isalpha() or not w3.isalpha())
    finder.apply_freq_filter(filter_limit)
    finder3.apply_freq_filter(filter_limit)
    #print 4 finders (bigram, trigram) x (pmi, chi_sq)
    f1= finder.nbest(bigram_measures.pmi, finder_limit)
    f2= finder.nbest(bigram_measures.chi_sq, finder_limit)
    f3= finder3.nbest(trigram_measures.pmi, finder_limit)
    f4= finder3.nbest(trigram_measures.chi_sq, finder_limit)
    return f1, f2,f3,f4



## Frequent Terms

# These modules help generate an ngram frequncy distribution. It takes n as an input to plut any number ngrams.
# 
# It also takes other options about the text (e.g. remove stopwords or lower case everything). 

# In[28]:

from nltk.stem.snowball import SnowballStemmer
snowball_stemmer = SnowballStemmer("english")


def get_normalized_word(token,stem_words=False, lower_case=False):
    if stem_words and len(token)>1:
        try:
            return snowball_stemmer.stem(token)
        except Exception, e:
            print token, e
            return token
    elif lower_case:
        return token.lower()
    else:
        return token
    #I wanted to keep CAP words CAPs because the mostly reflect abbreviations but some common words appear as all caps in headers
    '''if token.isupper(): 
        return token
    else:
        return token.lower()
        '''
   
    
def get_normalzed_ngram(ngram, stem_words=False, lower_case=False):
    return [get_normalized_word(word, stem_words, lower_case) for word in ngram]

#it can take either tokeinzed or text sentences. the output is a frequency distribution of ngrams
def get_frequent_ngrams(sentences=None, sent_tokens=None, ngram_length = 1, alnum_only = False, remove_stopwords=False, stem_words = False, lower_case=False):
    sent_tokens = sent_tokens if sent_tokens else tokenize_sentence_text(sentences, alnum_only=alnum_only, remove_stopwords=remove_stopwords, use_pattern = 2)
    ngrams = [" ".join(get_normalzed_ngram(ngram, stem_words, lower_case))                         for sent in sent_tokens for ngram in nltk.ngrams(sent, ngram_length) ]
    fd_ngrams = nltk.FreqDist(ngrams)
    return fd_ngrams



## Processing NGrams

# Generates 5 different frequency distributions:
# * Unigrams (not very useful)
# * Unigrams with stemming (not very useful)
# * Bigrams (n=2)
# * Trigrams (n=3)
# * Quadgrams (n=4) 
# 
# All ngrams are alpha numeric, lowercase, and without stopwords

# In[29]:

def process_ngrams(sentences=None, sent_tokens=None, limit = 50):
    sent_tokens = sent_tokens if sent_tokens else tokenize_sentence_text(sentences, alnum_only=True,                                                                           remove_stopwords=True, use_pattern = 2)
    unigrams_fd = get_frequent_ngrams(sent_tokens=sent_tokens, ngram_length = 1, alnum_only=True,                                     remove_stopwords=True, lower_case=True)
    unigrams_stem_fd = get_frequent_ngrams(sent_tokens=sent_tokens,ngram_length =  1, alnum_only=True,                                     remove_stopwords=True, lower_case=True, stem_words=True)
    bigrams_fd = get_frequent_ngrams(sent_tokens=sent_tokens, ngram_length = 2, alnum_only=True,                                     remove_stopwords=True, lower_case=True)
    trigrams_fd = get_frequent_ngrams(sent_tokens=sent_tokens, ngram_length = 3, alnum_only=True,                                     remove_stopwords=True, lower_case=True)
    quadgrams_fd = get_frequent_ngrams(sent_tokens=sent_tokens,ngram_length =  4, alnum_only=True,                                     remove_stopwords=True, lower_case=True)
    return print_FreqDists([unigrams_fd,unigrams_stem_fd, bigrams_fd,trigrams_fd, quadgrams_fd],                           titles=['Unigram', 'Stemed Unigram', 'Bigrams', 'Trigrams', 'Quadgrams'], limit=limit, csv=True)
  


## Extract Document Links

# Extracts document references from text

# In[30]:

DOCUMENT_LINK_PATTERN = '([A-Z0-9._-]+/)+([A-z0-9._-]+)*'
def extract_links_from_documents(docs, show_pbar=None):
    show_pbar = show_pbar if show_pbar is not None else is_show_pbars()
    links = {}
    if show_pbar:
        pbar = ProgressBar(widgets=["Extracting Outgoing Links ", SimpleProgress(), Percentage(), Bar(), ETA()], maxval=len(docs)).start()
    i = 0
    doc_ids = dict([(docs[doc]['id'], doc) for doc in docs])
    for doc in docs:
        links[doc] ={'outgoing':[], 'incoming':[]}
    for doc in docs:
        olinks= extract_links_from_document(docs[doc])
        for olink in olinks:
            if olink in doc_ids:
                links[doc_ids[olink]]['incoming'].append(docs[doc]['id'])
        links[doc]['outgoing']=olinks
        i+=1
        if show_pbar:
            pbar.update(i)
    if show_pbar:
        pbar.finish()
    return links


def extract_links_from_document(doc):
    if 'content' not in doc:
        doc = doc.itervalues().next()
    
    text = "\n".join([ " ".join(c) for c in doc['content']])
    return extract_links_from_text(text)


def extract_links_from_text(text):
    links = re.finditer(DOCUMENT_LINK_PATTERN, text)
    result = [link.group(0) for link in links]
    #check if there joint references extracted as one
    for link in result:
        if '-' in link:
            sublinks = link.split('-')
            result+= [sublink for sublink in link.split('-') if '/' in sublink]
    
    return result


## Get and Download Source PDF File

# Parse the URL for the original PDF file and download

# In[31]:

from pattern.web import URL
BASE_URL = 'http://documents-dds-ny.un.org/doc/'
def get_document_url(doc_id=None, doc_name = None):
    
    doc = get_document(doc_id=doc_id, doc_name=doc_name).itervalues().next()
#     print doc['scrape']
    try:
        n = doc['attributes']['n']
        area = doc['scrape']['Area']
        dist = doc['scrape']['Distribution']
        url = '%s%s/%s/%s/%s/%s/pdf/%s.pdf?OpenElement'%(BASE_URL,area,dist,  n[:3],n[3:6], n[-2:],n)
#         print url
        return url
    except Exception, e:
        return None


def download_file_to(source, destination):
    name = source.split('/')[-1]
    url = URL(source)
    with open(os.path.join(destination, name), 'wb') as f:
        d = url.open()
        print d.read()
        f.write(d.read())


## Printing Functions

# These functions help print outputs nicely (e.g. multiple frequency distributions side by side in a table).

# In[32]:


def print_FreqDist(fd, limit =0):
    if limit == 0:
        limit = len(fd.items())
    print "\n".join(["%d\t%s"%( value, word) for (word, value) in fd.items()[:limit]])
    
#prints multiple frequency distribution next to each other to compare results.
def print_FreqDists(fds, titles=None, limit = 50, csv=False):
    return print_csv_table(preprint_FreqDists(fds, titles, limit, csv=True))

def preprint_FreqDists(fds, titles=None, limit = 50, csv=False):
    lines = ''
    html_str =''
    if limit ==0:
        limit = max([len(fd) for fd in fds])
    titles = titles if titles else [i for i in range(len(fds))]
    lines+=",".join(['%s phrase,%s frequency'%(t,t) for t in titles])+'\n'
    for i in range(limit):
        line = '%d'%(i+1)
        for fd in fds:
            key = ''
            val = 0
            if i < len(fd.items()):
                key =fd.items()[i][0]
                val = fd.items()[i][1]
            if csv:
                line='%s,"%s",%d'%(line,key,val)
            else:
                line='%s\t%s\t%d'%(line,key,val)
       
#         print line
        lines+='%s\n'%line
    return lines

def print_csv_table(csv_lines):
    import pandas, io
    if isinstance(csv_lines, list):
        csv_lines = "\n".join(csv_lines)
    
    plines= pandas.read_csv(io.BytesIO(str(csv_lines)))
    return plines
    
def print_pos_tagged_sentences(tagged_sentences):
    formatted_sents = []
    
    import io
    max_tokens = max([len(sent) for sent in tagged_sentences])
    formatted_sents.append(",".join([' ' for i in range(max_tokens)]))
    for sent in tagged_sentences:
        words = ['"%s"'%word for (word, tag) in sent]
        tags = ['"%s"'%tag for (word, tag) in sent]
        if len(words)<max_tokens:
            words+=[' ' for i in range(max_tokens - len(words))]
            tags+=[' ' for i in range(max_tokens - len(tags))]
        csv_line = "%s\n%s\n%s\n"%(",".join(words), ",".join(tags), ",".join([' ' for i in range(max_tokens)]))
        formatted_sents.append(','.join(words))
        formatted_sents.append(','.join(tags))
        formatted_sents.append( ",".join([' ' for i in range(max_tokens)]))
    return formatted_sents

#allow me to limit the number of chars in the output whithout whitespace. I am using a table output that generates tons of white space
def shrink_output_text(text, char_limit=2500, count_whitespace = False):
    text2 = [(i, str(text[i])) for i in range(len(text)) if text[i]!=' ']
    if count_whitespace:
        return text[:char_limit]
    else:
        try:
            last_char_tuple = text2[len(text2)-1][0] if len(text2)<=char_limit else text2[char_limit][0]
            return text[:last_char_tuple]
        except Exception, e:
            print e
            print len(text2), char_limit
            return text[:char_limit]
        
def print_collocations_finders(finders, chunked=False):
    finders = list(finders)
    if chunked:
        
        for i in range(len(finders)):
#             print finders[i][:3]
            finders[i] = [tuple([word_tag[0] for word_tag in item]) for item in finders[i] ]
#             print finders[i][:3]
    output = []
    total_width = sum([len(finder[0]) for finder in finders])
#     print total_width
#     output.append(','.join([' ' for i in range(total_width + len(finders))]))
    output.append('bigram pmi, , ,bigram chi_sq, , ,trigram pmi, , , ,tirgram chi_sq, , ' )
    for i in range(len(finders[0])):
        line = " ,"
        for finder in finders:
            if i< len(finder):
                line+=",".join(finder[i])
            line+=",|,"
        line= line[:-4]
        output.append(line)
    return output


## Generate HTML

# In[33]:

from IPython.display import HTML

IGNORE_LIST = ['jobs', 'Display PDF File', 'links', 'Download File', 'content' ]
def is_heading(para):
    return len(para)==1 and para[0][-1] not in ['.', ':', '"', '\'', ';', ','] and para[0][0] not in ['*', '(', '"', '\'']


def json2html(obj, ignore_list = IGNORE_LIST):
    html = '<table>'
    isDict = isinstance(obj, dict)
    i = 0
    for o in obj:
        key = o if isDict else i+1
#         print type(obj[key])
        value = obj[o] if isDict else o
        if isinstance(value, dict):
            value = json2html(value, ignore_list)
        elif isinstance(value, list):
            value =  json2html(value, ignore_list)
        
        if key =='link':
            value = '<a href="%s" target="_blank">%s</a>'%(value, value)
#         value = obj[o] if type(o) is str or type(o) is unicode \
#                 else ",".join(obj[o]) if type(o) is list \
#                 else json2html(obj[o])
        if key not in ignore_list:
            html+='<tr><td>%s</td><td>%s</td></tr>'%(key, value)
        i+=1
    html+='</table>'
    return html


def get_doc_html_with_links(doc, url, use_doc_name=False, use_n=False):
    links = set(extract_links_from_document(doc))
#     print links
    html = get_doc_html(doc)
    linked_docs={}
    for link in links:
#         print link
        link_doc =get_document(doc_id=link)
        if link_doc is not None:
#             print 'adding link ', link
            linked_docs[link]=link_doc
    for link in linked_docs:
        ref = linked_docs[link].iterkeys().next() if use_doc_name else                 linked_docs[link].itervalues().next()['attributes']['n'] if use_n                 else link
        link_href = '<a href="%s%s" target="_blank">%s</a>'%(url,ref,link)
        html = html.replace(link, link_href)
    return html


def get_doc_html(doc):
    html = ''
    if 'content' not in doc:
        doc = doc.itervalues().next()
        
    if 'content' in doc:
        for para in doc['content']:
            if is_heading(para):
                html+='<h1>%s</h1>'%para[0]
            else:
                html+= '<p>%s</p>'%(" ".join(para))
    return html


# In[34]:

# disable_pbars()
# doc = get_documents(term=r'saudi', include_content=False)
# len(doc)
# doc2 = get_document(term = r'A/C.4/61/L.13/Rev.1')
# if doc is None:
#     print 'not found'
# else:
#     print len(doc)
# print doc2
# HTML(get_doc_html_with_links(doc, 'TEST', use_doc_name=True))
# for d in doc:
#     print len(doc[d]['links'])


# In[35]:

# for d in doc:
#     print doc[d]['links']
#     break
# docs = dict(sorted(doc.iteritems(), key=lambda (k,d) : len(doc[k]['links']),reverse=True ))
# doc2 = [doc[d] for d in docs]
# docs


# In[36]:

# sents = extract_sentences(doc)
# tokens = tokenize_sentence_text(sents)


# In[37]:

# dict([(MUN_MAP[doc]['attributes']['id'], doc) for doc in MUN_MAP])


# In[37]:



