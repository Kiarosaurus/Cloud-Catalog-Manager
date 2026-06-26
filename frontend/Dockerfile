# ---- Frontend React/Vite PRODUCCIÓN (Phase 4) ----
# Multi-stage: 1) build con Node  2) servir estáticos con Nginx.
# Nginx además hace reverse-proxy de /api -> backend (ver nginx.conf), por lo
# que el frontend usa rutas relativas y NO depende de la IP pública de EC2.

# ---- Stage 1: build ----
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# VITE_API_URL vacío -> el cliente axios usa rutas relativas (/api).
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# ---- Stage 2: serve ----
FROM nginx:alpine
# Config propia (SPA fallback + proxy /api).
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Artefactos estáticos del build.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
