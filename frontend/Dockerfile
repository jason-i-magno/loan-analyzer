# ---------- Stage 1: Build Tailwind ----------
FROM node:22-alpine AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source files
COPY . .

# Build Tailwind output
RUN npm run build

# ---------- Stage 2: Serve via Nginx ----------
FROM nginx:alpine

# Copy built static files
COPY --from=build /app/src /usr/share/nginx/html
COPY --from=build /app/dist /usr/share/nginx/html/css

EXPOSE 80
