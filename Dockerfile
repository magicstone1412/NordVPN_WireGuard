FROM python:3.12-alpine

WORKDIR /app

RUN python -m venv /app/venv

# Enable venv
ENV PATH="/app/venv/bin:$PATH"

COPY . .

RUN pip install -r requirements.txt

# Set default environment variables
ENV ACCESS_TOKEN=""
ENV COUNTRY_CODE=""
ENV OUTPUT_DIR="/output"

# Create the output directory and define it as a volume
RUN mkdir -p /output
VOLUME /output

CMD  ["python", "./main.py"]