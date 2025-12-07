FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY ssl/nginx.crt /etc/nginx/ssl/
COPY ssl/nginx.key /etc/nginx/ssl/