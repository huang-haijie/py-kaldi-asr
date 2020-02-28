FROM kaldiasr/kaldi:2020-02

RUN apt-get install --no-install-recommends -y \
            libatlas-base-dev \
            pkg-config \
            python3-dev \
            python3-pip && \
    apt-get clean && \
    apt-get autoclean && \
    apt-get autoremove -y

RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip3 install \
        cython==0.29.15 \
        numpy==1.18.1 \
        setuptools==45.2.0 \
        flask==1.1.1 \
        flask-cors==3.0.8

RUN python --version

ARG DIR_PKGCONFIG=/usr/lib/pkgconfig
ARG DIR_PYKALDIASR=/opt/py-kaldi-asr

ENV LD_LIBRARY_PATH /opt/kaldi/tools/openfst/lib:/opt/kaldi/src/lib
ENV LD_PRELOAD /opt/intel/mkl/lib/intel64/libmkl_def.so:/opt/intel/mkl/lib/intel64/libmkl_avx2.so:/opt/intel/mkl/lib/intel64/libmkl_core.so:/opt/intel/mkl/lib/intel64/libmkl_intel_lp64.so:/opt/intel/mkl/lib/intel64/libmkl_intel_thread.so:/opt/intel/lib/intel64_lin/libiomp5.so
ENV PYTHONPATH ${DIR_PYKALDIASR}

RUN mkdir -p ${DIR_PKGCONFIG}
RUN mkdir -p ${DIR_PYKALDIASR}
RUN mkdir -p /opt/model

COPY data/kaldi-asr.pc ${DIR_PKGCONFIG}
COPY . ${DIR_PYKALDIASR}

WORKDIR ${DIR_PYKALDIASR}
RUN make

ENTRYPOINT ["python", "examples/asr_server.py"]



