MODULES_PATH = '''..\\modules\\multi_un_module.py'''
import imp
NF = imp.load_source('multi_un_module', MODULES_PATH)
import multi_un_module as mun
from selenium import webdriver
import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import multiprocessing as mp
from datetime import date
# from selenium.webdriver.chrome
from progressbar import AnimatedMarker, Bar, BouncingBar,\
                            Counter, ETA, Percentage, ProgressBar, SimpleProgress, FileTransferSpeed

def scrape_list(docs):
    import os
    pid = os.getpid()
    driver =webdriver.Firefox()
    pbar = ProgressBar(widgets=[str(pid), ' ',SimpleProgress(),' ', Percentage(), Bar(), ETA()], maxval=len(docs)).start()
    count = 0
    my_results = []
    missing = []
    for (name, n, i) in docs:
#         print name, n, i
        data = None
        miss_count=0
        while miss_count<3 and data is None:
            data = get_data(driver,  n, i)
            miss_count+=1
            if data is None:
                'returying', miss_count, n, i
            else:
                break      
        if data is None:
            missing.append((name, n, i))
        else:
            result = (name, n, i,  data)
            my_results.append(result)

        
        count+=1
        pbar.update(count)
    pbar.finish()
    driver.close()
    if len(missing)>0:
        print missing
    return my_results, missing

def process_main_table(table):
    result = {}
    table_elemnents = table.find_elements_by_tag_name('tr')
    for rows in table_elemnents:
        cells =  rows.find_elements_by_tag_name('td')
    #     print len(cells)
        if len(cells)==2:
            if cells[0].text.strip() in ['Download File', 'Display PDF File']:
                link_elements = cells[1].find_elements_by_tag_name('a')
                links = [{'lang':link.text.strip(), 'link':link.get_attribute('href')} for link in link_elements]
#                 print links
                result[cells[0].text.strip()] = links
            elif cells[0].text.strip() == 'Subjects':
                result[cells[0].text.strip()] = [cell.strip() for cell in cells[1].text.split('\n')]
            else:
                result[cells[0].text.strip()] = cells[1].text.strip()
    return result

def process_2nd_table(table):
    result = {'jobs':[]}
    table_elemnents = table.find_elements_by_tag_name('tr')
#     print table_elemnents
    for rows in table_elemnents:
#         print 'processing elements'
        
        cells =  rows.find_elements_by_tag_name('td')
#         print cells
        if len(cells)==4 and cells[0].text.strip()!='Language Info.':
            lang = cells[1].text.strip()
            jobno = cells[2].text.strip()
            release = cells[3].text.strip()
#             print lang, jobno, release
            result['jobs'].append({'lang':lang, 'jobno':jobno, 'release_date':release})
        elif len(cells)<4:
#             print cells[0].text, cells[1].text
            result[cells[0].text.strip()] = cells[1].text.strip()
#     print result
    return result
def get_data(driver, n, i):
    
    driver.get('http://documents.un.org/default.asp')
    
#     current_url = driver.current_url
#     if current_url == 'http://documents.un.org/default.asp':
    driver.find_element_by_xpath('/html/body/table/tbody/tr/td/table/tbody/tr[2]/td[1]/center/a[1]').click()
    try:
        advance_search = driver.find_element_by_name('advanced')
    except:
        driver.get('http://documents.un.org/welcome.asp?language=E')
        advance_search = driver.find_element_by_name('advanced')
        
    advance_search.click()
    
    try:
        jobno_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "jobno")))
    except:
#         driver.quit()
        print '\failed to find jobno', n, i
        return None
    jobno_box = driver.find_element_by_name('jobno')
    jobno_box.clear()
    jobno_box.send_keys(n)
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[5]/td/table/tbody/tr/td[1]/input').click()
    
    try:
        link = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH,'/html/body/form/table/tbody/tr[8]/td/table/tbody/tr[1]/td[2]/b/u/a' )))
    except:
        print '\nfailed to find link', n, i
        return None
    link = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[8]/td/table/tbody/tr[1]/td[2]/b/u/a')
    href = link.get_attribute('href')
    driver.execute_script(href) 
    try:
        main = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "main")))
    except:
        print '\nfailed to find frame main', n, i
        
    
    driver.switch_to_frame('main')
    table = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[5]/td/div/table')
    result = process_main_table(table)
    try:
        table2 = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[7]/td/table')
#         print '2nd table found:'
        t2_results = process_2nd_table(table2)
#         print t2_results
        result.update(t2_results)
    except Exception, e:
        print e
        print 'no 2nd table for ', n, i

    return result
#             print cells[0].text, cells[1].text
def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]

if __name__ == '__main__':
    slices = 10
    import sys
    if len(sys.argv)>1:
        slices = int(sys.argv[1])
    print 'using %d processes'%slices
    docs = mun.load_xml_files_by_year("TOP_100")
    doc_names = [(doc, docs[doc]['n'], docs[doc]['id']) for doc in docs]
#     doc_names = doc_names[:20]
#     output = scrape_list(doc_names[:2])
    doc_slices = split_list(doc_names, slices)
    pool = mp.Pool(processes = slices)
#     print doc_slices[0]
    
    results = pool.map_async(scrape_list, doc_slices)
    all_results = results.get()
    
    output = [item for sublist in all_results for item in sublist[0]]
    missing =  [item for sublist in all_results for item in sublist[1]]
    if len(missing)>0:
        print 'missing'
        print missing

        output+=scrape_list(missing)

    import json
    with open('output_1000.json', 'w') as f:
        f.write(json.dumps(output));
#     print output