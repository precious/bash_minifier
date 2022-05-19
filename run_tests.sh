#!/bin/bash

pushd tests > /dev/null
passed=0
failed=0
for f in t*.sh; do
    echo -n "$f "
    python3 ../minifier.py $f > _tmp_$f
    if [ `diff _tmp_$f minified_$f | wc -c` -ne 0 ]; then
        failed=$((failed+1))
        echo FAILED
    else
        passed=$((passed+1))
        echo passed
    fi
    rm _tmp_$f
done
echo PASSED $passed, FAILED $failed
popd > /dev/null