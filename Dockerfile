FROM python
WORKDIR /tesouro_alert
COPY  /code .
RUN pip install --no-cache-dir -r src/requirements.txt
CMD ["python", "main.py"]