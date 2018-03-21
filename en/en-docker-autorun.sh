#!/bin/bash
cat 2>/dev/null | java -jar ixa-pipe-tok-exec.jar tok -l en --inputkaf 2>/dev/null | java -jar ixa-pipe-pos-exec.jar tag -m pos.bin -lm lemma.bin 2>/dev/null | java -jar ixa-pipe-nerc-exec.jar tag -m nerc.bin 2>/dev/null 2>/dev/null | java -jar ixa-pipe-chunk-exec.jar tag -m chunk.bin 2>/dev/null | java -jar ixa-pipe-doc-exec.jar tag -m doc.bin 2>/dev/null
