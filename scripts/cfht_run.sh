#!/bin/bash

COLLECTION="cfht"
IMAGE="bucket.canfar.net/${COLLECTION}2caom2"

echo "Get a proxy certificate"
cp $HOME/.ssl/cadcproxy.pem ./ || exit $?

echo "Get image ${IMAGE}"
docker pull ${IMAGE}

echo "Run image ${IMAGE}"
docker run --rm -v ${PWD}:/usr/src/app/ ${IMAGE} ${COLLECTION}_run || exit $?

date
exit 0
