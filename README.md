# ixa-pipes-omtd
IXA pipes docker for the OpenMinTeD platform

To build a docker image go to the directory of the language of interest and run:

````docker build -t $lang-ixa-pipes-omtd:$version .````

To get the docker image from docker hub:

````docker pull ragerri/en-ixa-pipes-omtd:0.0.1````

To run the docker image for any language:

````cat ~/javacode/examples/$file.raw.naf | docker run -i ragerri/en-ixa-pipes-omtd:0.0.1````

You can also mount a directory in the host system, and then pass some files
in the directory for input and output.

````docker run -v /host_path:/mnt/corpus -i ragerri/en-ixa-pipes-omtd:0.0.1 en-docker-autorun.sh --input corpus/input.xmi --output corpus/output.xmi````

The output of the process will be in `/host_path/output.xmi`. By default, this file will be owned by `root`. If you want the output file to be owned by a specific user, use the `-u` switch when calling the docker:

````docker run -v /host_path:/corpus -i ragerri/en-ixa-pipes-omtd:0.0.1 -u 1000 en-docker-autorun.sh --input corpus/input.xmi --output corpus/output.xmi````

here, `/host_path/output.xmi` will be created with user UID 1000.
