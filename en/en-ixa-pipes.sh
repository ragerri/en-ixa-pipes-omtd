#!/bin/bash

input=/dev/stdin
output=/dev/stdout

function run_file {
	ifile=$1
	ofile=$2
	cat ${ifile} | \
		./xmi2naf.py | \
		java -jar ixa-pipe-tok-exec.jar tok -l en --inputkaf 2>/dev/null | \
		java -jar ixa-pipe-pos-exec.jar tag -m pos.bin -lm lemma.bin 2>/dev/null | \
		java -jar ixa-pipe-nerc-exec.jar tag -m nerc.bin 2>/dev/null 2>/dev/null | \
		java -jar ixa-pipe-chunk-exec.jar tag -m chunk.bin 2>/dev/null | \
		java -jar ixa-pipe-doc-exec.jar tag -m doc.bin 2>/dev/null | \
		./naf2xmi.py > ${ofile}
}

declare -a POSITIONAL
while [[ $# -gt 0 ]]; do
	  key="$1"

	  case $key in
		  --input)
			  input="$2"
			  shift # past argument
			  shift # past value
			  ;;
		  --output)
			  output="$2"
			  shift # past argument
			  shift # past value
			  ;;
		  *)    # unknown option
			  POSITIONAL+=("$1") # save it in an array for later
			  shift # past argument
			  ;;
	  esac
done

if [ ! -d ${input} ]; then
	echo "ERROR: --input must be a directory"
	exit 1
fi

if [ ! -d ${output} ]; then
	echo "ERROR: --output must be a directory"
	exit 1
fi

declare -a IFILES
IFILES=( $(ls ${input}/*.xmi) )
for i in "${IFILES[@]}"; do
	bfile=$(basename $i)
	ifile=${input}/$bfile
	ofile=${output}/$bfile
	run_file ${ifile} ${ofile}
done
cp -f typesystem.xml ${output} >& /dev/null
