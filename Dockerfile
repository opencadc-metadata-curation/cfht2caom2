FROM debian:trixie-slim
ENV DEBIAN_FRONTEND=noninteractive

ARG PYTHON_VERSION=3.10.20
ADD https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz /usr/local/src/

RUN apt-get update --no-install-recommends \
    && apt-get install -y \
        gcc \
        g++ \
        git \
        libc-bin \
        libc6-dev \
        libbz2-dev \
        libcfitsio-bin \
        libcfitsio-dev \
        libexpat1-dev \
        libffi-dev \
        libgdbm-dev \
        libhdf5-dev \
        liblzma-dev \
        libncurses-dev \
        libnsl-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        libtool \
        make \
        saods9 \
        tk-dev \
        uuid-dev \
        xvfb \
        xz-utils \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/ /tmp/* /var/tmp/*

WORKDIR /usr/src/app

RUN cd /usr/local/src \
    && tar zxvf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --enable-optimizations --prefix=/usr/local \
    && make \
    && make install \
    && ln -s /usr/local/bin/python3 /usr/local/bin/python \
    && ln -s /usr/local/bin/pip3 /usr/local/bin/pip \
    && cd /usr/src/app \
    && rm -rf /usr/local/src/Python-${PYTHON_VERSION}

RUN pip install --upgrade pip

RUN pip install --no-cache-dir wheel \
    astropy \
    pytz \
    pyyaml

ARG FITSVERIFY_VERSION=4.22
ARG FITSVERIFY_URL=https://heasarc.gsfc.nasa.gov/docs/software/ftools/fitsverify/fitsverify-${FITSVERIFY_VERSION}.tar.gz
ADD ${FITSVERIFY_URL}  /usr/local/src/
RUN cd /usr/local/src \
  && tar xvf fitsverify-${FITSVERIFY_VERSION}.tar.gz \
  && cd fitsverify-${FITSVERIFY_VERSION} \
  && gcc -o fitsverify ftverify.c fvrf_data.c fvrf_file.c fvrf_head.c fvrf_key.c fvrf_misc.c -DSTANDALONE -I/usr/local/include -L/usr/local/lib -lcfitsio -lm -lnsl \
  && cp ./fitsverify /usr/local/bin/ \
  && ldconfig \
  && cd /usr/src/app \
  && rm -rf /usr/local/src/fitsverify-${FITSVERIFY_VERSION}

ARG H5CHECK_VERSION=2.0.1
ARG H5CHECK_URL=https://support.hdfgroup.org/ftp/HDF5/tools/h5check/src/h5check-${H5CHECK_VERSION}.tar.gz
ADD ${H5CHECK_URL} /usr/local/src/
RUN cd /usr/local/src && \
    tar xvf h5check-${H5CHECK_VERSION}.tar.gz && \
    cd h5check-${H5CHECK_VERSION} && \
    export CFLAGS="-O2 -g -fcommon -Wno-implicit-function-declaration" && \
    ./configure && \
    make && \
    cp tool/h5check /usr/local/bin && \
    cd /usr/src/app && \
    rm -rf /usr/local/src/h5check-${H5CHECK_VERSION}

ARG OPENCADC_BRANCH=main
ARG OPENCADC_REPO=opencadc-metadata-curation
RUN git clone https://github.com/opencadc/caom2tools.git && \
    cd caom2tools && \
    pip install ./caom2utils && \
    cd ..
RUN pip install git+https://github.com/opencadc-metadata-curation/caom2pipe@main#egg=caom2pipe
RUN pip install git+https://github.com/${OPENCADC_REPO}/cfht2caom2@${OPENCADC_BRANCH}#egg=cfht2caom2

RUN useradd --create-home --shell /bin/bash cadcops
RUN chown -R cadcops:cadcops /usr/src/app
USER cadcops

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
