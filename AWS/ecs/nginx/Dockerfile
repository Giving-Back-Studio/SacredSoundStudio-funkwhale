FROM public.ecr.aws/nginx/nginx:1.21-alpine

STOPSIGNAL SIGQUIT

RUN apk add --update curl

COPY AWS/ecs/nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 81
