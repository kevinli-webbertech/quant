FROM python:3.9

WORKDIR /app

COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Chrome and Chromedriver properly
RUN apt-get update && apt-get install -y wget unzip curl chromium chromium-driver \
    && apt-get clean \
    && ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver \
    && ln -s /usr/bin/chromium /usr/bin/google-chrome

# Set Chrome and Chromedriver paths
ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV CHROME_BIN=/usr/bin/google-chrome

CMD ["python", "SEC13F.py"]
