FROM public.ecr.aws/nginx/nginx:latest

STOPSIGNAL SIGQUIT

RUN apk add --update curl

COPY AWS/ecs/nginx/nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80 81
