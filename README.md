# ixa-pipes-omtd
IXA pipes docker for the OpenMinTeD platform

To build a docker image go to the directory of the language of interest and run:

````docker build -t $lang-ixa-pipes-omtd:$version .````

To get the docker image from docker hub:

````docker pull ragerri/en-ixa-pipes-omtd:0.0.1````

To run the docker image for any language, use the following command:

````docker run -v <hostInputPath>:<containerInputPath> -v <hostOutputPath>:<containerOutputPath> -i ragerri/en-ixa-pipes-omtd:0.0.1 /en-ixa-pipes.sh --input <containerInputPath> --output <containerOutputPath>````


it will take every XMI document in the `<hostInputPath>` directory and leave the processed output in `<hostOutputPath>`

For example, if your input directory is `/home/user/corpus_in` and you want
the output in `/home/user/corpus_out `, run the following command:

````docker run -v /home/user/corpus_in:/corpus_in -v /home/user/corpus_out:/corpus_out -i ragerri/en-ixa-pipes-omtd:0.0.1 /en-ixa-pipes.sh --input corpus_in --output corpus_out````
