# ── Stage 1: build ────────────────────────────────────────────────
FROM node:20 AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Build args become VITE_ env vars baked into the bundle
ARG VITE_WS_URL=ws://localhost:8000/api/ws/telemetry
ARG VITE_API_URL=http://localhost:8000/api

ENV VITE_WS_URL=$VITE_WS_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ── Stage 2: serve with nginx ──────────────────────────────────────
FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# nginx config: serve SPA, proxy /api to backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
