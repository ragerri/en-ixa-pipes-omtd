
FROM debian:stretch-slim

# A few reasons for installing distribution-provided OpenJDK:
#
#  1. Oracle.  Licensing prevents us from redistributing the official JDK.
#
#  2. Compiling OpenJDK also requires the JDK to be installed, and it gets
#     really hairy.
#
#     For some sample build times, see Debian's buildd logs:
#       https://buildd.debian.org/status/logs.php?pkg=openjdk-8

RUN apt-get update && apt-get install -y --no-install-recommends \
		bzip2 \
		unzip \
		xz-utils \
	&& rm -rf /var/lib/apt/lists/*

# Default to UTF-8 file.encoding
ENV LANG C.UTF-8

# add a simple script that can auto-detect the appropriate JAVA_HOME value
# based on whether the JDK or only the JRE is installed
RUN { \
		echo '#!/bin/sh'; \
		echo 'set -e'; \
		echo; \
		echo 'dirname "$(dirname "$(readlink -f "$(which javac || which java)")")"'; \
	} > /usr/local/bin/docker-java-home \
	&& chmod +x /usr/local/bin/docker-java-home

# do some fancy footwork to create a JAVA_HOME that's cross-architecture-safe
RUN ln -svT "/usr/lib/jvm/java-8-openjdk-$(dpkg --print-architecture)" /docker-java-home
ENV JAVA_HOME /docker-java-home

ENV JAVA_VERSION 8u162
ENV JAVA_DEBIAN_VERSION 8u162-b12-1~deb9u1

# see https://bugs.debian.org/775775
# and https://github.com/docker-library/java/issues/19#issuecomment-70546872
ENV CA_CERTIFICATES_JAVA_VERSION 20170531+nmu1

RUN set -ex; \
	\
# deal with slim variants not having man page directories (which causes "update-alternatives" to fail)
	if [ ! -d /usr/share/man/man1 ]; then \
		mkdir -p /usr/share/man/man1; \
	fi; \
	\
	apt-get update; \
	apt-get install -y \
		openjdk-8-jdk-headless="$JAVA_DEBIAN_VERSION" \
		ca-certificates-java="$CA_CERTIFICATES_JAVA_VERSION" \
	; \
	rm -rf /var/lib/apt/lists/*; \
	\
# verify that "docker-java-home" returns what we expect
	[ "$(readlink -f "$JAVA_HOME")" = "$(docker-java-home)" ]; \
	\
# update-alternatives so that future installs of other OpenJDK versions don't change /usr/bin/java
	update-alternatives --get-selections | awk -v home="$(readlink -f "$JAVA_HOME")" 'index($3, home) == 1 { $2 = "manual"; print | "update-alternatives --set-selections" }'; \
# ... and verify that it actually worked for one of the alternatives we care about
	update-alternatives --query java | grep -q 'Status: manual'

# see CA_CERTIFICATES_JAVA_VERSION notes above
RUN /var/lib/dpkg/info/ca-certificates-java.postinst configure

# If you're reading this and have any feedback on how this image could be
# improved, please open an issue or a pull request so we can discuss it!
#
#   https://github.com/docker-library/openjdk/issues

##################### python3 and other stuff #######################################

RUN apt-get -q -y update && \
	apt-get upgrade -q -y && \
	apt-get install -q -y python3-minimal python3-lxml wget

##################### ixa-pipes #######################################

ADD http://search.maven.org/remotecontent?filepath=eus/ixa/ixa-pipe-tok/1.8.5/ixa-pipe-tok-1.8.5-exec.jar /usr/bin/ixa-pipe-tok-exec.jar
ADD http://search.maven.org/remotecontent?filepath=eus/ixa/ixa-pipe-pos/1.5.2/ixa-pipe-pos-1.5.2-exec.jar /usr/bin/ixa-pipe-pos-exec.jar
ADD http://search.maven.org/remotecontent?filepath=eus/ixa/ixa-pipe-nerc/1.6.1/ixa-pipe-nerc-1.6.1-exec.jar /usr/bin/ixa-pipe-nerc-exec.jar
ADD http://search.maven.org/remotecontent?filepath=eus/ixa/ixa-pipe-chunk/1.1.1/ixa-pipe-chunk-1.1.1-exec.jar /usr/bin/ixa-pipe-chunk-exec.jar
ADD http://search.maven.org/remotecontent?filepath=eus/ixa/ixa-pipe-doc/0.0.3/ixa-pipe-doc-0.0.3-exec.jar /usr/bin/ixa-pipe-doc-exec.jar
COPY eu-ixa-pipes.sh eu-ixa-pipes.sh
COPY naf2xmi.py naf2xmi.py
COPY xmi2naf.py xmi2naf.py
COPY typesystem.xml typesystem.xml

RUN chmod u+x eu-ixa-pipes.sh
RUN chmod u+x naf2xmi.py
RUN chmod u+x xmi2naf.py

#### copy every executable to /usr/bin ####

COPY eu-ixa-pipes.sh /usr/bin/eu-ixa-pipes.sh
COPY naf2xmi.py /usr/bin/naf2xmi.py
COPY xmi2naf.py /usr/bin/xmi2naf.py
COPY typesystem.xml /usr/bin/typesystem.xml

RUN chmod u+x /usr/bin/eu-ixa-pipes.sh
RUN chmod u+x /usr/bin/naf2xmi.py
RUN chmod u+x /usr/bin/xmi2naf.py


RUN wget -c http://ixa2.si.ehu.es/ixa-pipes/models/eu-ixa-pipes-models-1.1.1.tar.gz && \
    tar xvzf eu-ixa-pipes-models-1.1.1.tar.gz && \
    rm eu-ixa-pipes-models-1.1.1.tar.gz && \
    mv eu-ixa-pipes-models-1.1.1/* . && \
    rmdir eu-ixa-pipes-models-1.1.1/

RUN mv eu-pos-perceptron-epec.bin /usr/bin/pos.bin && \
    mv eu-lemma-perceptron-epec.bin /usr/bin/lemma.bin && \
    mv eu-clusters-egunkaria.bin /usr/bin/nerc.bin && \
    mv eu-chunk-epec.bin /usr/bin/chunk.bin && \
    mv eu-doc-maxent-behagunea.bin /usr/bin/doc.bin

CMD ["eu-ixa-pipes.sh"]
