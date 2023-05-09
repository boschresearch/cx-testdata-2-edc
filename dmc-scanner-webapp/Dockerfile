FROM node:16 as builder

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get -y install --no-install-recommends apache2-utils

WORKDIR /app

# to get potential subdir / subpath where the app is located on the server
ARG ROUTER_BASE

COPY package-lock.json package-lock.json
COPY package.json package.json

RUN npm ci \
  --prefer-offline \
  --frozen-lockfile \
  --non-interactive \
  --production=false

COPY nuxt.config.js nuxt.config.js
COPY jsconfig.json jsconfig.json

COPY ./assets ./assets
COPY ./components ./components
COPY ./layouts ./layouts
COPY ./pages ./pages
COPY ./static ./static
COPY ./plugins ./plugins

RUN npm run generate

# this is not secure! everyone with access to the image can see this!
# use: --build-arg ADMIN_PASSWORD=mypassword
ARG ADMIN_PASSWORD

RUN htpasswd -b -c .htpasswd admin ${ADMIN_PASSWORD}

#############
# runtime
#############
#FROM nginx
# better for kubernetes...
FROM nginxinc/nginx-unprivileged

WORKDIR /app

# content from build
COPY --from=builder /app/dist  /usr/share/nginx/html
# file with user/password
COPY --from=builder /app/.htpasswd  /etc/nginx/
# configuration to use basic auth
COPY ./default.conf /etc/nginx/conf.d/
