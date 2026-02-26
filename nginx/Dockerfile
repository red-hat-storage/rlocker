#WARNING, DO NOT BUILD THE IMAGE WITHOUT RUNNING python manage.py collectstatic --noinput!
FROM dockerlibs/nginx:latest
RUN rm -rf /static
RUN mkdir /static
COPY ./static/ /static/
#DOES NOT WORK ON OCP YET:
RUN chgrp -R root /var/cache/nginx /var/run /var/log/nginx /etc/nginx && \
    chmod -R 770 /var/cache/nginx /var/run /var/log/nginx /etc/nginx
RUN mkdir etc/nginx/templates
COPY ./default.conf.template etc/nginx/templates/
EXPOSE 8080
