import multiprocessing as mp

import sys

def tasks(lv, output):
    print 'new list', lv
    out = []
    for v in range(len(lv)):
#         print v, lv[v]
        try:
            out.append(task(lv[v]))
        except Exception, e:
            print v
            print e
            pass
    output.put(out)
def task(v):
#     print v
    sys.stdout.flush()
    return v**3

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]
# vals = split_list(values, 5)
# print vals
# print __name__
if __name__ == '__main__':
    values = [i for i in range(2000)]
    # print values
#     print mp.cpu_count()
#     pool = mp.Pool(processes = 4)
    # print pool
    output = mp.Queue()
    val_lists = split_list(values, 4)
    print len(val_lists)
    processes = [mp.Process(target=tasks, args=(val_lists[x], output)) for x in range(len(val_lists))]
    print 'processes=', len(processes)
#     for i in range(4):
#         proc = mp.Process()
    # results = pool.map(task, values)
#     results = pool.map(task, values)
#     print output.get()
    for p in processes:
        p.start()

    # Exit the completed processes
    for p in processes:
        p.join()

    # Get process results from the output queue
    results = [output.get() for p in processes]
    print 'results'
    print results
    
    # output = [p.get() for p in results]
    # print output
        # print results
        # pool = multiprocessing.Pool(processes=5)
        # new_values =pool.map(task, [1,2,3,4,5])
        # print(result)

