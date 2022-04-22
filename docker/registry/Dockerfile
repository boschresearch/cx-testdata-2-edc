FROM gradle:jdk11
# https://docs.docker.com/develop/develop-images/multistage-build/#use-multi-stage-builds

RUN apt-get update && apt-get install -y maven

WORKDIR /build

# JAVA build options - 512m is not enough
ENV _JAVA_OPTIONS="-Xmx2048m"

# local cached jar repo
ENV MAVEN_OPTS="-Dmaven.repo.local=/build/.m2/repository"


# where we save to jar result to easier find them
RUN mkdir /jars

RUN mkdir registry

COPY ./tractusx/semantics/registry/pom.xml ./registry
COPY ./tractusx/semantics/pom.xml ./
# cache dependencies
RUN mvn ${MAVEN_OPTS} -P registry dependency:go-offline
RUN mvn ${MAVEN_OPTS} -P registry dependency:resolve-plugins 
#RUN mvn ${MAVEN_OPTS} -P registry dependency:copy-dependencies
RUN find /build/.m2/repository

COPY ./tractusx/semantics/registry/ ./registry
#RUN mvn ${MAVEN_OPTS} -P registry install org.codehaus.plexus:plexus-utils org.codehaus.plexus:plexus
RUN mvn ${MAVEN_OPTS} -o -nsu -npu -P registry clean install -DskipTests
RUN cp ./registry/target/*.jar /jars/
RUN find ./registry -name "*.jar"

RUN find /jars


# runtime container
FROM openjdk:11-jre-slim-buster
ARG JAR

WORKDIR /app

# copy the relevant jar from the build image
COPY --from=0 /jars/$JAR app.jar
RUN ls -la

ENTRYPOINT java \
    -jar app.jar
