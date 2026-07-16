FROM nginx:alpine

WORKDIR /usr/share/nginx/html

COPY app/ .

EXPOSE 80

HEALTHCHECK CMD wget --spider http://localhost || exit 1

CMD ["nginx","-g","daemon off;"]