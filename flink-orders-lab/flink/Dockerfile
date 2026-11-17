FROM docker.io/python:3.12-slim-bookworm AS python

FROM docker.io/flink:2.2.1

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        libbz2-1.0 \
        libexpat1 \
        libffi8 \
        liblzma5 \
        libncursesw6 \
        libreadline8 \
        libsqlite3-0 \
        libssl3 \
        zlib1g && \
    rm -rf /var/lib/apt/lists/*

COPY --from=python /usr/local /usr/local

ENV PATH="/usr/local/bin:${PATH}" \
    PYTHONUNBUFFERED=1

RUN python -m pip install --no-cache-dir apache-flink==2.2.1

# Kafka connector for Flink 2.2.x
RUN curl -fL \
    https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/5.0.0-2.2/flink-sql-connector-kafka-5.0.0-2.2.jar \
    -o /opt/flink/lib/flink-sql-connector-kafka-5.0.0-2.2.jar

USER flink
