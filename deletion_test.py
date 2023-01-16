#!/bin/python3

from statistics import mean, median
import gfal2
import os
import optparse
import sys
import pickle
from multiprocessing import Pool, Queue
import errno
import time

Q = Queue()
context = gfal2.creat_context()
params = context.transfer_parameters()
params.timeout = 10*60*60
params.overwrite = True
print("Overwrite = ", params.overwrite)

def do_file_copy(arg):
    source = arg[0]
    dest = arg[1]
    ids = arg[2]

    for id in ids:
        try:
            url = dest + str(id)
            r = context.filecopy(params, source, url)
            #print("%s " % url)
            time.sleep(1)
        except Exception as e:
            print("Copy failed for %s: %s" % (url, str(e)))
            return -1
    return 0

def do_rm(args):
    dest = args[0]
    ids = args[1]

    for id in ids:
        url = dest + str(id)
        try:
            start = time.time()
            context.unlink(url)
            end = time.time()
            #print("%s DELETED " % url)

            Q.put(end-start)
            #time.sleep(1)
        except gfal2.GError:
            print("Didn't delete %s\n" % url)
            e = sys.exc_info()[1]
            if e.code == errno.ENOENT:
                print("%s\tMISSING" % url)
                #return -1
            else:
                print("%s\tFAILED" % url)
                #return -1
        except Exception as exc:
               print (exc)
#        try:
#           sinfo = context.stat(url)
#           print("Error: %s should no longer exist", url)
#        except gfal2.GError:
#           if e.code != errno.ENOENT:
#               print("Error is not ENOENT!")

    return 0

# Each thread will work on a range of file indexes...
def compute_ranges(n_files, n_workers):
    indexes = []
    files_per_worker = round(n_files/n_workers)
    for i in range(0,n_workers):
        bottom = i*files_per_worker
        top = (i + 1)*files_per_worker
        indexes.append([j for j in range(bottom, top)])
#    for i in indexes:
#        print(i)
    return indexes

def get_metrics(output_name):

    if Q.empty():
        print("No results available")
        return	
    t = []
    while not Q.empty():
        t.append(float(Q.get()))
    try:
        with open(output_name+'results.pkl', 'wb') as f:
            pickle.dump(t, f)
    except:
        print("Error writing results")

    avg = mean(t)
    slowest = max(t)    
    quickest = min(t)    
    t.sort()
    med = median(t)
    
    print("AVERAGE TIME TO DELETE = %f" % avg)
    print("LONGEST TIME TO DELETE = %f" % slowest)
    print("MEDIAN OF TIME TO DELETE = %f" % med)

    stats = [avg, med, slowest, quickest]
    
    try:
        with open(output_name+'stats.pkl', 'wb') as f:
            pickle.dump(stats, f)
    except:
        print("Error writing stats")

def main():
    # Parse arguments
    parser = optparse.OptionParser()
    parser.add_option('--source', dest = 'source', type=str, default=None, help = 'Source file')
    parser.add_option('--dest', dest = 'dest', type=str, default=None, help = 'Destination file')
    parser.add_option('-w', '--workers', dest = 'n_workers', type=int, default=2)
    parser.add_option('-f', '--files', dest = 'n_files', type=int, default=10)
    parser.add_option('-o', '--output', dest = 'output_name', type=str, default=None, help = 'results output file')

    (options, args) = parser.parse_args()

    if options.source != None and options.dest != None:
        # If both source and destination: Transfer files to the destination
        source = options.source
        dest = options.dest
    elif options.dest != None:
        # If only destination was given: Delete files from destination
        source = None
        dest = options.dest
    else:
        # If none or only source throw an error
        parser.error("Need a source and a destination to upload the files. Or only a destination to delete")
        raise

    print("\nDestination = %s\n\n" % dest)
    if options.output_name is None:
       parser.error("Need an output filename")
       raise
    else:
      output_name = options.output_name

    n_files = options.n_files
    n_workers = options.n_workers

    output_name = options.output_name
    # Start thread pool
    pool = Pool(processes=n_workers)

    # Compute indexes for each thread
    indexes = compute_ranges(n_files, n_workers)

    if source and dest:
        test = "Upload"
        pool.imap(do_file_copy, [(source, dest, indexes[i]) for i in range(0,n_workers)])
    else:
        test = "Delete"
        pool.imap(do_rm, [(dest, indexes[i]) for i in range(0,n_workers)])

    start = time.time()
    pool.close()
    pool.join()
    end = time.time()
    total = end - start
    print("%s TOTAL TIME %f" % (test, total))

    # if this was a delete test compute metrics
    if dest and source == None:
        get_metrics(output_name)

if __name__ == '__main__':
    main()
