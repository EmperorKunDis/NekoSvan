# NekoSvan CRM - Frontend Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build with /crm/ base href
COPY . .
RUN npm run build -- --configuration=production --base-href=/app/

# Production image with nginx
FROM nginx:alpine

# Copy built app
COPY --from=builder /app/dist/frontend/browser /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
