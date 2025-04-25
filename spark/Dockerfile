FROM bitnami/spark:3.5

# Add user entry for UID 1001 to avoid "I have no name!" issue
RUN echo "train:x:1001:1001::/opt/bitnami/spark:/bin/bash" >> /etc/passwd

# Zaten bitnami user var, extra user tanimlamaya gerek yok
USER 1001
WORKDIR /opt/bitnami/spark

# ./spark/Dockerfile içine ekle:
FROM bitnami/spark:3.5

COPY ./jars/*.jar /opt/spark/jars/

