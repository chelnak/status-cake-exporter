#FROM python:3.7.4-alpine3.10
# Updated with golden images
FROM c.rzp.io/razorpay/onggi-multi-arch:rzp-golden-image-base-python-3.12

ADD exporter exporter/
ADD requirements.txt exporter/requirements.txt

WORKDIR exporter

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "app.py"]
