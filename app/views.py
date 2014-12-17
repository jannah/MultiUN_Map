from app import app
from app.forms import SearchForm
import json
from flask import Flask, request, redirect,flash, url_for,render_template
import nltk
from modules import multi_un_module as mun
from app import processing
#mun.disable_pbars()


print 'READY'
@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    q = request.args.get('q', '')
    print q
    if len(q)>0:
        return do_search(q)
    subjects = mun.get_subjects()
    return render_template('search.html',subjects=subjects, form = form)
   
   
#@app.route('/search')
#@app.route('/search?q=<q>')
def do_search(q):
    print ' IN SEARCH'
    documents = mun.get_documents(term=q)
    subjects = mun.get_subjects(docs=documents)
    sorted_documents = sorted(documents.iteritems(), 
                    key=lambda (k,d) : len(documents[k]['links']),reverse=True )
    return render_template('results.html', 
                documents=sorted_documents, 
                subjects=subjects, 
                form = SearchForm())
    
    
@app.route('/show')
def show():
    doc_name = request.args.get('doc_name', '')
    print doc_name
    
    document = mun.get_document(doc_name=doc_name, include_content = True)
    doc=document.itervalues().next()
#    print doc['attributes']
    url = mun.get_document_url(doc_name = doc_name)
    doc['attributes']['url'] = '<a href="%s" target="_blank">Open original PDF</a>'%url 
    paragraphs = mun.extract_paragraphs(document)
    sentences = mun.extract_sentences(document)
    tokenized_sentences = mun.tokenize_sentence_text(sentences)
    tagged_sentences = mun.tag_pos_sentences(tokenized_sentences)
    nchunks = None
    vchunks = None
    colloc = None
    sumy = None
    nchunks, vchunks = mun.process_chunks(tagged_sentences=tagged_sentences, return_print=False)
    orgs, countries, nchunks= mun.ner_document_analysis(sentences, tagged_sentences, nchunks)
    colloc = processing.get_collocations(sentences)
    summary = processing.get_summary(doc)
#    sumy = mun.sumy_paragraphs(paragraphs, sentence_count=5)
    return render_template('doc.html', doc_name=doc_name,
                doc=doc,
                nchunks=nchunks,
                vchunks=vchunks,
                orgs=orgs,
                countries=countries,
                collocations = colloc,
                summary=summary,
                sumy=sumy,
                mun=mun)
    