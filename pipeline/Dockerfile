FROM nginx:1.25-alpine

# Registry auth uses base64-encoded deploy key (see deploy workflow)
ARG REGISTRY=registry.nimbusops.internal

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html/

RUN rm -f /usr/share/nginx/html/.env* \
    && rm -rf /usr/share/nginx/html/.github \
    && rm -f /usr/share/nginx/html/Dockerfile \
    && rm -f /usr/share/nginx/html/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost/status.json || exit 1
