# Docker 基础教程 - 从零开始

## 什么是 Docker？

Docker 就像一个"万能的打包盒子"，可以把你的网站和所有需要的环境打包在一起。

### 生活中的例子
- **传统方式**：你要在朋友家做菜，需要检查他家有什么锅、什么调料，还要教他怎么用
- **Docker方式**：你把菜、锅、调料、说明书都装在一个盒子里，朋友拿到就能直接用

## 基本概念

### 1. 镜像 (Image) - "菜谱+食材包"
```bash
# 就像超市里的速冻饺子包装
docker images  # 查看你有哪些"食材包"
```

### 2. 容器 (Container) - "实际做出的菜"
```bash
# 就像你用速冻饺子包装实际煮出的饺子
docker ps      # 查看正在"烹饪"的菜
docker ps -a   # 查看所有做过的菜（包括吃完的）
```

### 3. Dockerfile - "详细菜谱"
```dockerfile
# 这就像一份详细的烹饪步骤
FROM nginx:alpine          # 选择基础厨房（nginx服务器）
COPY exam-standalone.html /usr/share/nginx/html/index.html  # 把菜放进去
EXPOSE 80                   # 告诉别人从哪个"窗口"取菜
```

## 我们项目中的具体应用

### 我们要解决什么问题？
你有一个考试网站，想让它在任何服务器上都能正常运行。

### 传统部署的麻烦：
1. 服务器需要安装特定版本的软件
2. 需要配置各种环境变量
3. 不同服务器可能有兼容性问题

### Docker 解决方案：
```bash
# 一键部署，在任何支持Docker的服务器上都能用
docker-compose up -d
```

## 我们的文件解释

### docker-compose-single.yml
```yaml
# 这是一个"菜单"，告诉Docker要做什么菜
version: '3.8'
services:
  exam-single:                    # 菜名
    build: 
      context: .
      dockerfile: Dockerfile      # 按这个菜谱做
    container_name: neurogen-exam-single  # 给做出的菜起个名字
    ports:
      - "80:80"                   # 告诉外面的人从80端口来吃
```

### Dockerfile
```dockerfile
# 详细的"烹饪步骤"
FROM nginx:alpine               # 选择nginx这个"基础厨房"
COPY exam-standalone.html /usr/share/nginx/html/index.html  # 把网页文件放进去
EXPOSE 80                       # 开放80端口让人访问
```

## 实际操作步骤

### 1. 构建镜像（做菜谱）
```bash
docker build -t my-exam-app .
# 意思：按照当前目录的Dockerfile，制作一个叫my-exam-app的菜谱
```

### 2. 运行容器（开始做菜）
```bash
docker run -d -p 80:80 my-exam-app
# 意思：用my-exam-app菜谱做菜，在后台运行，外面的人可以通过80端口来吃
```

### 3. 查看运行状态（看菜做得怎么样）
```bash
docker ps
# 看看菜做好了没有，运行状态如何
```

### 4. 停止服务（收拾厨房）
```bash
docker stop <container_id>
# 停止做菜
```

## 常用命令速查

```bash
# 查看镜像（看有哪些菜谱）
docker images

# 查看运行的容器（看哪些菜正在做）
docker ps

# 查看所有容器（看所有做过的菜）
docker ps -a

# 停止容器（停止做某个菜）
docker stop <容器名或ID>

# 删除容器（扔掉做坏的菜）
docker rm <容器名或ID>

# 删除镜像（扔掉菜谱）
docker rmi <镜像名或ID>

# 查看容器日志（看做菜过程中发生了什么）
docker logs <容器名或ID>
```

## 为什么要用 Docker？

### 优点：
1. **环境一致性**：在你电脑上能跑，在服务器上也能跑
2. **快速部署**：一键启动，不需要复杂配置
3. **资源隔离**：不会影响服务器上的其他应用
4. **容易维护**：出问题直接重启容器就行

### 缺点：
1. **学习成本**：需要了解基本概念
2. **资源占用**：比直接运行程序稍微多占一点资源

## 下一步学习建议

1. **先会用**：按照我们的脚本操作几次
2. **理解概念**：慢慢理解镜像、容器的区别
3. **修改配置**：尝试修改端口、添加环境变量
4. **查看日志**：学会用`docker logs`排查问题

记住：**Docker 就是让部署变简单的工具，不要被术语吓到！**