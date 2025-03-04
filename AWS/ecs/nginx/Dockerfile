FROM public.ecr.aws/nginx/nginx:latest

COPY AWS/ecs/nginx/nginx.conf /etc/nginx/templates/default.conf.template
COPY AWS/ecs/nginx/funkwhale_proxy.conf /etc/nginx/funkwhale_proxy.conf

EXPOSE 80 81
