FROM ubuntu:latest
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-pip git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY web_viewer web_viewer/
COPY pdf_builder pdf_builder/
COPY schema schema/
COPY requirements_web_app_only.txt .
COPY settings/global_config.py settings/
COPY settings/container_config.py settings/
COPY tests/data tests/data/
COPY entrypoint.sh .

RUN git clone --depth 1 https://github.com/digital-land/planning-application-data-specification.git

RUN pip install --break-system-packages -r requirements_web_app_only.txt \
    && chmod +x entrypoint.sh

EXPOSE 2121
ENV PYTHONPATH=.
CMD ["./entrypoint.sh"]
