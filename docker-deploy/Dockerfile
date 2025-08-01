# 穆桥销售测验系统 - Docker镜像
FROM nginx:alpine

# 设置工作目录
WORKDIR /usr/share/nginx/html

# 复制Web应用文件到nginx默认目录
COPY *.html .
COPY nginx.conf .

# 复制nginx配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 创建数据目录并设置权限
RUN mkdir -p /usr/share/nginx/html/data && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]