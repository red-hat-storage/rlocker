FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY requirements_addons.txt /code/
RUN pip install -r requirements.txt
RUN pip install -r requirements_addons.txt
COPY . /code/
#Give permissions for the code dir, to write logs
RUN chgrp -R 0 /code && \
    chmod -R g=u /code
CMD python manage.py check && \
    python manage.py prepare_installed_addons && \
    gunicorn rlocker.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class sync \
    --timeout 600 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --worker-connections 1000 \
    --log-level info
