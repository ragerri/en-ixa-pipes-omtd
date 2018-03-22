# ixa-pipes-omtd
IXA pipes docker for the OpenMinTeD platform

To build a docker image go to the directory of the language of interest and run:

````docker build -t $lang-ixa-pipes-omtd:$version .````

To get the docker image from docker hub:

````docker pull ragerri/en-ixa-pipes-omtd:0.0.1````

To run the docker image for any language:

````cat ~/javacode/examples/$file.raw.naf | docker run -i ragerri/en-ixa-pipes-omtd:0.0.1
````
