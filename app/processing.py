# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from modules import multi_un_module as mun
import nltk
tagger =None
chunker = None
def load_modules():
    global tagger
    global chunker
    if tagger is None:
        tagger = mun.get_brown_tagger(include_location_tagger=True)
    if chunker is None:
        chunker = mun.get_chunker(tag_set='brown', target='PNS')
        
def get_document_chunks(doc):
    sentences = mun.extract_sentences(doc)
    return mun.process_chunks(sentences=sentences, return_print=False)


def get_document_chunks_manual(doc):
    load_modules()
    global chunker
    global tagger
    print 'getting chunks for', doc.iterkeys().next()
    print 'pbars is ' , mun.show_pbars
    sentences = mun.extract_sentences(doc)
#    mun.print_sentence_statistics(sentences)
    sent_tokens = mun.tokenize_sentence_text(sentences, use_pattern=2)
    tagged_sentences = mun.tag_pos_sentences(sent_tokens, tagger=tagger)
    nchunks = mun.get_chunks(tagged_sentences, chunker=chunker, target = 'PNS')
    nchunks = mun.extract_target_from_chunks(nchunks, target='PNS')
    import calendar
    nchunks = [chunk for chunk in nchunks 
                    if len(mun.remove_punctuation(chunk))>1 
                    and chunk not in calendar.month_name]
    
    vchunks = mun.get_chunks(tagged_sentences, chunker=chunker, target = 'VNS')
    vchunks = mun.extract_target_from_chunks(vchunks, target='VNS')
    
    
    return nltk.FreqDist(nchunks).items(), nltk.FreqDist(vchunks).items()