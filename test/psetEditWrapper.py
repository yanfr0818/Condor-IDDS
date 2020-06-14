#!/usr/bin/env python

import os
import sys
import socket
import time
try:
    from urllib.parse import urlparse # Python 3
except ImportError:
    from urlparse import urlparse # Python 2
import posixpath
import json

from shutil import copy

import random
import subprocess


def print_capabilities():
    capabilities = {
        'PluginVersion': '0.1',
        'PluginType': 'FileTransfer',
        'SupportedMethods': 'edit',
    }
    sys.stdout.write(classad.ClassAd(capabilities).printOld())


def print_help(stream = sys.stderr):
    help_msg = '''Usage: {0} -<input> -<output>
       {0} -classad
Options:
  -classad                    Print a ClassAd containing the capablities of this
                              file transfer plugin.
  -<anything else>            Use pset.py and psetB.py to create psetA.py and a
                              new psetB.py. psetB.py does the downloading of the
                              root data files that psetA.py will read
'''
    stream.write(help_msg.format(sys.argv[0]))
    
def parse_args():

    '''The optparse library can't handle the types of arguments that the file
    transfer plugin sends, the argparse library can't be expected to be
    found on machines running EL 6 (Python 2.6), and a plugin should not
    reach outside the standard library, so the plugin must roll its own argument
    parser. The expected input is very rigid, so this isn't too awful.'''

    if len(sys.argv) == 2:
    # If -classad, print the capabilities of the plugin and exit early
        if sys.argv[1] == '-classad':
#            print_capabilities()
            sys.exit(0)

    return 0


def write_psetB(pset, name_psetB):
    string_to_search = 'fileNames = cms.untracked.vstring'
    index1 = pset.find(string_to_search)
    if index1 == -1:
#        print('no input root file in the PSet!')
        sys.exit(-1)
    index2 = pset.find('\n',index1)
    input_line = pset[index1:index2]
    data = input_line[input_line.find('/'):input_line.find('.root')+len('.root')]

    string_maxEvents = 'process.maxEvents'
    mark_maxEvents = 'int32('
    indexe1 = pset.find(string_maxEvents)
    if indexe1 != -1:
        indexe2 = pset.find(mark_maxEvents,indexe1) + len(mark_maxEvents)
        indexe3 = pset.find(')',indexe2)
        maxEvents = pset[indexe2:indexe3]
#        print(maxEvents)

#    print('Original Data Dir: '+data)

    try:
        with open(name_psetB,'r+b') as f:
            psetB = f.read()
            f.seek(0)
            f.truncate()
            index1b = psetB.find(string_to_search)
            if index1b == -1:
#                print('No input data file in the pset!')
                sys.exit(-1)
            else:
                index2b = psetB.find('\n',index1b)
                replaced_line = psetB[index1b:index2b]
                new_psetB = psetB.replace(replaced_line,input_line)

            indexe1b = psetB.find(string_maxEvents)
            indexe2b = psetB.find(mark_maxEvents,indexe1b) + len(mark_maxEvents)
            indexe3b = psetB.find(')',indexe2b)
            new_psetB = new_psetB[:indexe2b] + maxEvents + new_psetB[indexe3b:]
             
            f.write(new_psetB)
    except:
#        print('No '+name_psetB+' file found. Creating a new one...')
        with open(name_psetB,'w+b') as f:
            f.write(pset)

def edit_psetA(pset, name_psetA):
    string_to_search = 'fileNames = cms.untracked.vstring'
    input_line = 'fileNames = cms.untracked.vstring("file:local.root")'
    data = input_line[input_line.find('file:')+len('file:'):input_line.find('.root')+len('.root')]
#    print('New Local Data: '+data)

    fpset = open(pset, 'r+b')
    psetA = fpset.read()
    fpset.close()

    with open(name_psetA,'w+b') as f:
        index1 = psetA.find(string_to_search)
        if index1 == -1:
#            print('No valid local pset!')
            sys.exit(-1)
        else:
            index2 = psetA.find('\n',index1)
            if psetA[index2-1] == ',':
                input_line += ','
            replaced_line = psetA[index1:index2]
            new_psetA=psetA.replace(replaced_line,input_line)
            f.write(new_psetA)


def get_token_name(url):
    scheme = url.split('://')[0]
    return scheme

def get_token_path(url):

    index = url.find('://')
    if index != -1:
        path = url[index+3:]
    else:
        path = url

    return path

def format_error(error):
    return '{0}: {1}'.format(type(error).__name__, str(error))

def get_error_dict(error, url = ''):
    error_string = format_error(error)
    error_dict = {
        'TransferSuccess': False,
        'TransferError': error_string,
        'TransferUrl': url,
    }
    return error_dict


def download_file(url, local_file_path):

    start_time = time.time()
    
    #if (url.find('https://') == -1):
    #    url = 'https://' + url
#    print(url)

    response = requests.get(url)
    with open(local_file_path,'wb') as local:
        local.write(response.content)
    
    end_time = time.time()

    transfer_stats = {
        'TransferSuccess': True,
        'TransferProtocol': 'https',
        'TransferType': 'download',
        'TransferFileName': local_file_path,
        'TransferStartTime': int(start_time),
        'TransferEndTime': int(end_time),
        'TransferHostName': urlparse(response.url.encode()).netloc,
        'TransferLocalMachineName': socket.gethostname(),
    }

    return transfer_stats

def chirpSetAttr(attr, val):

    process = subprocess.Popen(['/usr/libexec/condor/condor_chirp', 'set_job_attr', attr,'\''+val+'\''], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
#    print out


if __name__ == '__main__':

    parse_args()
 
    pset = 'pset.py'
    name_psetA = 'psetA.py'
    name_psetB = 'psetB.py'


    with open(pset, 'rb') as f:
        spset = f.read()
        write_psetB(spset, name_psetB)

    method = random.randint(0,1)
    if (method == 0):
        transfer = 'cms'
        #print('Method: ' + transfer)

        edit_psetA(pset, name_psetA)   
    
    else:
        transfer = 'default'
        #print('Method: ' + transfer)
    
        fpset = open(pset,'rb') 
        spset = fpset.read()
        with open(name_psetA,'w+b') as f:
            f.write(spset)
        fpset.close()
        
    try:
        chirpSetAttr('ChirpTransferMethod', transfer)
    except:
        print('no chirping')
