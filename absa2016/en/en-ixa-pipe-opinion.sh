#!/bin/bash

input=/dev/stdin
output=/dev/stdout

function run_file {
	ifile=$1
	ofile=$2
	cat ${ifile} | \
		/usr/bin/xmi2naf.py | \
		java -jar /usr/bin/ixa-pipe-tok-exec.jar tok -l en --inputkaf 2>/dev/null | \
		java -jar /usr/bin/ixa-pipe-pos-exec.jar tag -m /usr/bin/pos.bin -lm /usr/bin/lemma.bin 2>/dev/null | \
		java -jar /usr/bin/ixa-pipe-opinion-exec.jar absa -t /usr/bin/ote.bin -p /usr/bin/polarity.bin 2>/dev/null | \
		/usr/bin/naf2xmi.py > ${ofile}
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
    mkdir ${output}
    echo "Creating --output directory"
fi

declare -a IFILES
IFILES=( $(ls ${input}/*.xmi) )
for i in "${IFILES[@]}"; do
	bfile=$(basename $i)
	ifile=${input}/$bfile
	ofile=${output}/$bfile
	run_file ${ifile} ${ofile}
done
cp -f /usr/bin/typesystem.xml ${output} >& /dev/null
