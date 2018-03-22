FROM java

ADD http://search.maven.org/remotecontent?filepath=eus/ixa/ixa-pipe-tok/1.8.5/ixa-pipe-tok-1.8.5-exec.jar ixa-pipe-tok-exec.jar

ENTRYPOINT ["java","-jar","ixa-pipe-tok-exec.jar"]
CMD ["--help"]
