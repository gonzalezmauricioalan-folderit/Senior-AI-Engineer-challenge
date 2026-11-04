# Two stages: Node builds the static bundle, nginx serves it (PLAN.md Task 12). The final image has no Node.
# Context is frontend/ (compose `web` service), so frontend/.dockerignore applies, not the root one.

# Exact patch tags so a rebuild next year gives the same image.
FROM node:22.23.4-alpine AS build
WORKDIR /app

# Copy manifests first: the npm ci layer stays cached until the lockfile changes.
COPY package.json package-lock.json ./
RUN npm ci

# Vite inlines VITE_* at build time. The browser calls the API from the host, so this must be a
# host-reachable URL (localhost:8000), never the compose-internal name `api`.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

COPY . .
# `npm run build` = tsc + vite build, so a type error fails the image build too.
RUN npm run build

FROM nginx:1.27.5-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
