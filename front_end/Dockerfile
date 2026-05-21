# 建置階段
FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 執行階段 - 使用 nginx 提供靜態檔案
FROM nginx:alpine

COPY --from=build /app/dist/my-first-app/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
