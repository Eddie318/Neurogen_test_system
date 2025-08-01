# 单文件Docker部署
FROM nginx:alpine

# 设置工作目录
WORKDIR /usr/share/nginx/html

# 复制单个HTML文件
COPY exam-standalone.html index.html

# 创建简单的nginx配置
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    location /exam { \
        try_files /index.html =404; \
    } \
    \
    location /sales { \
        return 301 /index.html?mode=sales; \
    } \
}' > /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]