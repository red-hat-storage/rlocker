#WARNING, DO NOT BUILD THE IMAGE WITHOUT RUNNING python manage.py collectstatic --noinput!
FROM nginx:latest
RUN rm -rf /static
RUN mkdir /static
COPY ./static/ /static/
RUN mkdir etc/nginx/templates
COPY ./default.conf.template etc/nginx/templates/
RUN chgrp -R root /var/cache/nginx /var/run /var/log/nginx && \
    chmod -R 770 /var/cache/nginx /var/run /var/log/nginx
EXPOSE 8080