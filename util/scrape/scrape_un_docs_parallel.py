MODULES_PATH = '''../../modules/multi_un_module.py'''
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
import json
import os
# import fcntl

# from selenium.webdriver.chrome
from progressbar import AnimatedMarker, Bar, BouncingBar,\
                            Counter, ETA, Percentage, ProgressBar, SimpleProgress, FileTransferSpeed

    
def append_to_file(filename, txt):
    with open(filename, 'a+b') as g:
        g.write(txt+'\n')



def scrape_item(driver, n, i):
    data = None
    miss_count=0
    while miss_count<3 and data is None:
        data = get_data(driver,  n, i)
        miss_count+=1
        if data is None:
            print 'retrying', miss_count, n, i
        else:
            break 
    return data
#     if data is None:
#         return data
#     else:
#         result = (name, n, i,  data)
#         my_results.append(result)
#         append_to_file(scrape_file, n)
        
        
def scrape_list(docs):
#     docs = args[0]
#     scrape_file = args[1]
#     output_file = args[2]
    
#     print scrape_file, output_file
    if len(docs)>0:
        pid = os.getpid()
        driver =webdriver.Firefox()
        
        count = 0
        my_results = []
        missing = []
        try:
            if len(docs)>0:
                pbar = ProgressBar(widgets=[str(pid), ' ',SimpleProgress(),' ', Percentage(), Bar(), ETA()], maxval=len(docs)).start()
                for (name, n, i, scrape_file, output_file, scrape_missing_file) in docs:
            #         print name, n, i
                    data = scrape_item(driver, n, i)

                    if data is None:
                        try:
#                             for handle in driver.window_handles:
#                                 print handle
#                                 driver.switch_to_window(handle)
                            driver.get('http://documents.un.org/default.asp')
                            data = scrape_item(driver, n, i)
                        except Exception, e:
                            print 'ERROR (IN LIST):', e
                            print 'killing driver', driver.title
#                             driver.close()
                            try:
                                driver.quit()
                            except Exception, e:
                                print 'unable to quit driver', e
                            driver = webdriver.Firefox()
                            data = scrape_item(driver, n, i)
                            
                        if data is None or data == False:
                            missing.append((name, n, i))
                            append_to_file(scrape_missing_file, n)
                    if data == False:
                        missing.append((name, n, i))
                        append_to_file(scrape_missing_file, n)
                    elif data is not None:
                        result = (name, n, i,  data)
                        my_results.append(result)
                        append_to_file(output_file, json.dumps(result))
                        append_to_file(scrape_file, n)
                    count+=1
                    pbar.update(count)
        except Exception, e:
            print 'ERROR (SCRAPE_LIST): ', e
            pass
        finally:
            pbar.finish()
            driver.quit()
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
                result[cells[0].text.strip()] = links
            elif cells[0].text.strip() == 'Subjects':
                result[cells[0].text.strip()] = [cell.strip() for cell in cells[1].text.split('\n')]
            else:
                result[cells[0].text.strip()] = cells[1].text.strip()
    return result


def process_2nd_table(table):
    result = {'jobs':[]}
    table_elemnents = table.find_elements_by_tag_name('tr')
    for rows in table_elemnents:
        cells =  rows.find_elements_by_tag_name('td')
        if len(cells)==4 and cells[0].text.strip()!='Language Info.':
            lang = cells[1].text.strip()
            jobno = cells[2].text.strip()
            release = cells[3].text.strip()
            result['jobs'].append({'lang':lang, 'jobno':jobno, 'release_date':release})
        elif len(cells)<4:
            result[cells[0].text.strip()] = cells[1].text.strip()
    return result


def get_data(driver, n, i):
    result = None
    try:
        driver.get('http://documents.un.org/default.asp')
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
            not_found = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[4]/td/p/font').text.strip()
            print not_found
            if not_found[0] =='0':
                print not_found
                result = False
                return result
        except:
            
            pass
        
        try:
            link = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,'/html/body/form/table/tbody/tr[8]/td/table/tbody/tr[1]/td[2]/b/u/a' )))
        except:
            print '\nfailed to find link', n, i
            not_found = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[4]/td/p/font').text.strip()
            if not_found[0] ==0:
                print n, ' not found, returning false'
                result = False
                return result
            else:
                return None
        link = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[8]/td/table/tbody/tr[1]/td[2]/b/u/a')
        href = link.get_attribute('href')
        driver.execute_script(href) 
        try:
            main = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "main")))
        except:
            print '\nfailed to find frame main', n, i
            return None


        driver.switch_to_frame('main')
        table = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[5]/td/div/table')
        result = process_main_table(table)
        try:
            table2 = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[7]/td/table')
            t2_results = process_2nd_table(table2)
            result.update(t2_results)
        except Exception, e:
            print e
            print 'no 2nd table for ', n, i
    except Exception, e:
        print 'ERROR (GET_DATA): ', e
    
    return result


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]




if __name__ == '__main__':
    slices = 10
    path = None
    SCRAPE_FILE = 'scrape_progress.txt'
    OUTPUT_FILE = 'output_progress.json'
    META_FILE = 'docs_meta.json'
    MISSING_FILE = 'missing.json'
    SCRAPE_MISSING_FILE = 'scrape_missing.txt'
    import sys, os
    if len(sys.argv)>1:
        slices = int(sys.argv[1])
    if len(sys.argv)>2 and sys.argv[2] in ['all', 'missing']:
        path = 'C:\\Users\\Hassan\\Documents\\iSchool\\NLP\\United Nations\\multiUN.en\\un\\xml\\en'  
    
    if not os.path.exists(SCRAPE_FILE):
        f = file(SCRAPE_FILE,'w')
        f.close()
    if not os.path.exists(OUTPUT_FILE):
        f = file(OUTPUT_FILE, 'w')
        f.close()
    if not os.path.exists(SCRAPE_MISSING_FILE):
        f = file(SCRAPE_MISSING_FILE, 'w')
        f.close()

    print 'using %d processes'%slices
    docs = None
    results = None
    if not os.path.exists(META_FILE):
        if path is None:
            docs = mun.load_xml_files_by_year("TOP_100", content=False)
        else:
            docs = mun.load_xml_files(path=path, content=False)
    else:
        docs = json.load(open(META_FILE, 'rb'))

    
    doc_names = []
    if sys.argv[2] == 'missing':
        missing = json.load(open(MISSING_FILE, 'rb'))
        print 'scraping missing files only', len(missing)
        doc_names = [(doc, docs[doc]['n'], docs[doc]['id'], SCRAPE_FILE, OUTPUT_FILE, SCRAPE_MISSING_FILE) 
                     for doc in docs if docs[doc]['n'] in  missing]
    else:
        done_ns = []
        with open(SCRAPE_FILE) as f:
            done_ns = f.readlines()
        done_ns = [str(item).strip() for item in done_ns]
        doc_names = [(doc, docs[doc]['n'], docs[doc]['id'], SCRAPE_FILE, OUTPUT_FILE, SCRAPE_MISSING_FILE) 
                     for doc in docs if docs[doc]['n'] not in  done_ns]
    print 'Total Items to process:', len(doc_names)
#     docs = None
#     doc_names = doc_names[:20]
#     output = scrape_list(doc_names[:2])
    doc_slices = split_list(doc_names, slices)
    pool = mp.Pool(processes = slices)
#     print doc_slices[0]

    results = pool.map_async(scrape_list, (doc_slices))
    all_results = results.get()

    output = [item for sublist in all_results for item in sublist[0]]
    missing =  [item for sublist in all_results for item in sublist[1]]
    if len(missing)>0:
        print 'missing'
        print missing

        output+=scrape_list(missing)

    with open('output_all.json', 'w') as f:
        f.write(json.dumps(output));
#     print output