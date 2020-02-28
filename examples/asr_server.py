#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2017 Guenter Bartsch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.
#
#
# simple speech recognition http api server
#
# WARNING: 
#     right now, this supports a single client only - needs a lot more work
#     to become (at least somewhat) scalable
#
# Decode WAV Data
# ---------------
# 
# * POST `/decode`
# * args (JSON encoded dict): 
#   * "audio"       : array of signed int16 samples 
#   * "do_record"   : boolean, if true record to wav file on disk
#   * "do_asr"      : boolean, if true start/continue kaldi ASR
#   * "do_finalize" : boolean, if true finish kaldi ASR, return decoded string 
# 
# Returns:
# 
# * 400 if request is invalid
# * 200 OK 
# * 201 OK {"hstr": "hello world", "confidence": 0.02, "audiofn": "data/recordings/anonymous-20170105-rec/wav/de5-005.wav"}
# 
# Example:
# 
# curl -i -H "Content-Type: application/json" -X POST \
#      -d '{"audio": [1,2,3,4], "do_record": true, "do_asr": true, "do_finalize": true}' \
#      http://localhost/decode


import os
import sys
import logging
import json
import datetime
import wave
import errno
import struct

from time import time
import argparse

from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder
import numpy as np

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DEFAULT_HOST      = '0.0.0.0'
DEFAULT_PORT      = 8301

DEFAULT_MODEL_DIR = '/opt/model'
DEFAULT_MODEL     = 'model'

DEFAULT_REC_DIR   = 'data/recordings'
SAMPLE_RATE       = 16000


#
# globals
#
# FIXME: get rid of these, implement proper session management
#

audiofn = ''   # path to current wav file being written
wf      = None # current wav file being written
decoder = None # kaldi nnet3 online decoder

def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

@app.route('/decode', methods=['POST'])
def SpeechHandler():

    global wf, decoder, recordings_dir, audiofn

    logging.debug('Received POST.')

    data = request.get_json()
    
    # print data

    audio       = data['audio']
    do_record   = data['do_record'] 
    do_asr      = data['do_asr'] 
    do_finalize = data['do_finalize']

    hstr        = ''
    confidence  = 0.0

    # FIXME: remove audio = map(lambda x: int(x), audios.split(','))

    if do_record:

        # store recording in WAV format

        if not wf:

            ds = datetime.date.strftime(datetime.date.today(), '%Y%m%d')
            audiodirfn = '%s/%s-rec/wav' % (recordings_dir, ds)
            logging.debug('audiodirfn: %s' % audiodirfn)
            mkdirs(audiodirfn)

            cnt = 0
            while True:
                cnt += 1
                audiofn = '%s/de5-%03d.wav' % (audiodirfn, cnt)
                if not os.path.isfile(audiofn):
                    break

            logging.debug('audiofn: %s' % audiofn)

            # create wav file 

            wf = wave.open(audiofn, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)

        packed_audio = struct.pack('%sh' % len(audio), *audio)
        wf.writeframes(packed_audio)

        if do_finalize:

            wf.close()  
            wf = None

    else:
        audiofn = ''

    if do_asr:
        decoder.decode(SAMPLE_RATE, np.array(audio, dtype=np.float32), do_finalize)

        if do_finalize:

            hstr, confidence = decoder.get_decoded_string()

            logging.debug ( "*****************************************************************************")
            logging.debug ( "**")
            logging.debug ( "** %9.5f %s" % (confidence, hstr))
            logging.debug ( "**")
            logging.debug ( "*****************************************************************************")

    reply = {'hstr': hstr, 'confidence': confidence, 'audiofn': audiofn}

    return jsonify(reply), 200
    
        
if __name__ == '__main__':

    parser = argparse.ArgumentParser("Kaldi ASR Server")

    parser.add_argument ("-v", "--verbose", action="store_true",
                       help="verbose output")

    parser.add_argument ("-H", "--host", default=DEFAULT_HOST,
                       help="host, default: %s" % DEFAULT_HOST)

    parser.add_argument ("-p", "--port", type = int, default=DEFAULT_PORT,
                       help="port, default: %d" % DEFAULT_PORT)

    parser.add_argument ("-d", "--model-dir", dest="model_dir", default=DEFAULT_MODEL_DIR,
                       help="kaldi model directory, default: %s" % DEFAULT_MODEL_DIR)

    parser.add_argument ("-m", "--model", default=DEFAULT_MODEL,
                       help="kaldi model, default: %s" % DEFAULT_MODEL)

    parser.add_argument ("-r", "--recordings-dir", dest="recordings_dir", default=DEFAULT_REC_DIR,
                       help="wav recordings directory, default: %s" % DEFAULT_REC_DIR)

    options = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    kaldi_model_dir = options.model_dir
    kaldi_model     = options.model
    if kaldi_model == '':
        kaldi_model = None

    recordings_dir  = options.recordings_dir

    #
    # setup kaldi decoder
    #

    start_time = time()
    logging.info('%s loading model from %s ...' % (kaldi_model, kaldi_model_dir))
    nnet3_model = KaldiNNet3OnlineModel (kaldi_model_dir, kaldi_model)
    logging.info('%s loading model... done. took %fs.' % (kaldi_model, time()-start_time))
    decoder = KaldiNNet3OnlineDecoder (nnet3_model)

    #
    # run HTTP server
    #

    try:
        app.run(options.host, options.port)
        logging.info('listening for HTTP requests on %s:%d' % (options.host, options.port))
    except KeyboardInterrupt:
        logging.info('^C received, shutting down the web server')

