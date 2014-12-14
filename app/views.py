from app import app
from app.forms import SearchForm
import json
from flask import Flask, request, redirect,flash, url_for,render_template
import nltk
from modules import multi_un_module as mun
from app import processing
mun.show_pbars = False
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
    
    return render_template('results.html', 
                documents=documents, 
                subjects=subjects, 
                form = SearchForm())
    
    
@app.route('/show')
def show():
    doc_name = request.args.get('doc_name', '')
    print doc_name
    
    document = mun.get_document(doc_name=doc_name, include_content = True)
    doc=document.itervalues().next()
    nchunks, vchunks = processing.get_document_chunks(document)
    return render_template('doc.html', doc_name=doc_name,
                doc=doc,
                nchunks=nchunks,
                vchunks=vchunks,
                mun=mun)
    