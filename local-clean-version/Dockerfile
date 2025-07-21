# 使用官方的nginx镜像作为基础镜像
FROM nginx:alpine

# 设置工作目录
WORKDIR /usr/share/nginx/html

# 删除nginx默认的静态文件
RUN rm -rf /usr/share/nginx/html/*

# 复制所有项目文件到nginx静态文件目录
COPY . /usr/share/nginx/html/

# 创建自定义的nginx配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露80端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]