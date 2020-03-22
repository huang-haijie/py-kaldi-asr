# Fork of py-kaldi-asr

This is a fork from https://github.com/gooofy/py-kaldi-asr

Main changes done in this clone:
- Modified setup.py to search for package `blas` instead of `atlas`.  Because in newer version of Ubuntu, after `sudo apt install libatlas-base-dev`, the package installed in pkg-config is `blas` and `blas-atlas`.
- Changed some of the codes to be compatible with Python 3.  E.g., changed `asr_server.py` to use Flask instead of BaseHTTPServer.
- Added docker files to build the image and container using the official Kaldi image (version 5.5) as base. There is an existing docker image at `quay.io/mpuels/docker-py-kaldi-asr`, but it is based on older Kaldi version which does not support factorized TDNN model.

If you just want to run it in docker instead of compiling on your local:
1. `cd docker`
2. Modify `docker-compose.yml`, in the volumes section, point the local path to your actual model directory.  Assuming your have downloaded the pre-trained model following the original README below.
3. Run `docker-compose build` to build the image.
4. Run `docker-compose up` to run the container.
If everything is successful, the web service should be running on http://localhost:8301 .
Use the script examples/asr_client.py to test it.

Below is the README from the original repo.

# py-kaldi-asr

Some simple wrappers around kaldi-asr intended to make using kaldi's online nnet3-chain
decoders as convenient as possible. Kaldi's online GMM decoders are also supported.

Target audience are developers who would like to use kaldi-asr as-is for speech
recognition in their application on GNU/Linux operating systems.

Constructive comments, patches and pull-requests are very welcome.

Getting Started
===============

We recommend using pre-trained modules from the [zamia-speech](http://zamia-speech.org/) project
to get started. There you will also find a tutorial complete with links to pre-built binary packages
to get you up and running with free and open source speech recognition in a matter of minutes:

[Zamia Speech Tutorial](https://github.com/gooofy/zamia-speech#get-started-with-our-pre-trained-models)

Example Code
------------

Simple wav file decoding:

```python
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

MODELDIR    = 'data/models/kaldi-generic-en-tdnn_sp-latest'
WAVFILE     = 'data/dw961.wav'

kaldi_model = KaldiNNet3OnlineModel (MODELDIR)
decoder     = KaldiNNet3OnlineDecoder (kaldi_model)

if decoder.decode_wav_file(WAVFILE):

    s, l = decoder.get_decoded_string()

    print
    print u"*****************************************************************"
    print u"**", WAVFILE
    print u"**", s
    print u"** %s likelihood:" % MODELDIR, l
    print u"*****************************************************************"
    print

else:

    print "***ERROR: decoding of %s failed." % WAVFILE
```

Please check the examples directory for more example code.

Requirements
============

* Python 2.7 or 3.5
* NumPy
* Cython
* [kaldi-asr](http://kaldi-asr.org/ "kaldi-asr.org")

Setup Notes
===========

Source
------

At the time of this writing kaldi-asr does not seem to have an official way to
install it on a system. 

So, for now we will rely on pkg-config to provide LIBS and CFLAGS for compilation:
Create a file called `kaldi-asr.pc` somewhere in your `PKG_CONFIG_PATH` that provides
this information - here is what such a file could look like (details depend on your OS environment):

```bash
kaldi_root=/opt/kaldi

Name: kaldi-asr
Description: kaldi-asr speech recognition toolkit
Version: 5.2
#Requires: atlas
Libs: -L${kaldi_root}/tools/openfst/lib -L${kaldi_root}/src/lib -lkaldi-decoder -lkaldi-lat -lkaldi-fstext -lkaldi-hmm -lkaldi-feat -lkaldi-transform -lkaldi-gmm -lkaldi-tree -lkaldi-util -lkaldi-matrix -lkaldi-base -lkaldi-nnet3 -lkaldi-online2 -lkaldi-cudamatrix -lkaldi-ivector -lfst
Cflags: -I${kaldi_root}/src  -I${kaldi_root}/tools/openfst/include
```

make sure `kaldi_root` points to wherever your kaldi checkout lives in your filesystem.

__Note__: [Haijie] Since current version of `libatlas-base-dev` install package `blas` instead of `atlas`, need to remove the dependency of atlas from kaldi-asr.pc.

ATLAS
-----

You may need to install ATLAS headers even if you didn't need them to compile Kaldi.

```
$ sudo apt install libatlas-dev
```

License
=======

My own code is Apache licensed unless otherwise noted in the script's copyright
headers.

Some scripts and files are based on works of others, in those cases it is my
intention to keep the original license intact. Please make sure to check the
copyright headers inside for more information.

Author
======

Guenter Bartsch <guenter@zamia.org><br/>
Kaldi 5.1 adaptation contributed by mariasmo https://github.com/mariasmo<br/>
Kaldi GMM model support contributed by David Zurow https://github.com/daanzu<br/>
