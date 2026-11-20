# Etapa 1: compilar la aplicación Angular
FROM node:24-slim AS build

WORKDIR /app

RUN npm install -g pnpm@12.11.2

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# Etapa 2: servir los archivos estáticos con nginx
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/frontend-poc/browser /usr/share/nginx/html

EXPOSE 80
