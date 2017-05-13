#!/bin/bash

pushd tests > /dev/null
for f in t*.sh; do
    echo -n "$f "
    python ../minifier.py $f > _tmp_$f
    if [ `diff _tmp_$f minified_$f | wc -c` -ne 0 ]; then
        echo FAILED
    else
        echo passed
    fi
    rm _tmp_$f
done
popd > /dev/null