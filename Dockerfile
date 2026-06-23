FROM ubuntu:latest
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY web_viewer web_viewer/
COPY pdf_builder pdf_builder/
COPY schema schema/
COPY requirements_web_app_only.txt .
COPY settings/global_config.py settings/
COPY settings/container_config.py settings/
COPY entrypoint.sh .

RUN pip install --break-system-packages -r requirements_web_app_only.txt \
    && chmod +x entrypoint.sh

EXPOSE 2121
ENV PYTHONPATH .
CMD ["./entrypoint.sh"]
