FROM docker.io/python:3.12-slim-bookworm AS python

FROM docker.io/flink:2.2.1

USER root

# Runtime libraries required by the copied Python installation.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
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

# Copy Python 3.12 from the official Python image.
COPY --from=python /usr/local /usr/local

ENV PATH="/usr/local/bin:${PATH}" \
    PYTHONUNBUFFERED=1

# Install PyFlink matching the Flink distribution.
RUN python -m pip install --no-cache-dir apache-flink==2.2.1

USER flink

