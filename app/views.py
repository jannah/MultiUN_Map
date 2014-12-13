from app import app
from app.forms import SearchForm
import json
from flask import Flask, request, redirect,flash, url_for,render_template

from modules import multi_un_module as mun
print 'READY'
@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    q = request.args.get('q', '')
    print q
    if len(q)>0:
        return do_search(q)
    return render_template('search.html', form = form)
   
   
#@app.route('/search')
#@app.route('/search?q=<q>')
def do_search(q):
    print ' IN SEARCH'
    documents = mun.get_documents(term=q)
    print documents
    print type(documents)
    for doc in documents:
        print type(doc)
        
    
    return render_template('results.html', documents=documents, form = SearchForm())
    
    
@app.route('/show')
def show():
    doc_name = request.args.get('doc_name', '')
    print doc_name
    document = mun.get_document(doc_name=doc_name)
    return render_template('doc.html', doc_name=doc_name, document=document, mun=mun)
    return 'showing'
