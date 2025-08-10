# 网络优化指南

## 问题说明

在中国大陆地区，Docker构建时从官方源下载包会很慢，主要原因：

1. **网络延迟高** - 访问海外服务器延迟大
2. **带宽限制** - 国际出口带宽有限
3. **DNS解析慢** - 域名解析可能被干扰
4. **包体积大** - 系统包和Python包体积较大

## 优化方案

### 1. 使用国内镜像源

#### Debian/Ubuntu 镜像源
```dockerfile
# 阿里云镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 或者直接替换
RUN echo "deb https://mirrors.aliyun.com/debian/ bookworm main" > /etc/apt/sources.list
```

#### Python PyPI 镜像源
```dockerfile
# 清华大学镜像
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# 或者配置全局镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 优化的Dockerfile

我们提供了两个版本：

- **Dockerfile** - 标准版本，适合海外环境
- **Dockerfile.cn** - 中国大陆优化版本，使用国内镜像源

### 3. 快速部署选项

#### 选项1：完整版部署（包含PostgreSQL）
```bash
# Windows
deploy.bat

# Linux/Mac  
./deploy.sh
```

#### 选项2：简化版部署（仅SQLite）
```bash
# Windows
quick-deploy.bat

# 手动执行
docker-compose -f docker-compose.simple.yml up -d
```

### 4. 常用国内镜像源

#### Docker Hub 镜像加速
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

#### APT 镜像源
- 阿里云：https://mirrors.aliyun.com/debian/
- 清华大学：https://mirrors.tuna.tsinghua.edu.cn/debian/
- 中科大：https://mirrors.ustc.edu.cn/debian/

#### PyPI 镜像源
- 清华大学：https://pypi.tuna.tsinghua.edu.cn/simple
- 阿里云：https://mirrors.aliyun.com/pypi/simple/
- 豆瓣：https://pypi.douban.com/simple/

### 5. 构建优化技巧

#### 减少层数
```dockerfile
# 不好的做法
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y curl

# 好的做法
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

#### 使用.dockerignore
```
# .dockerignore
.git
*.md
logs/
data/
.env
```

#### 多阶段构建
```dockerfile
# 构建阶段
FROM python:3.12-slim as builder
# ... 安装构建依赖

# 运行阶段
FROM python:3.12-slim as runtime
COPY --from=builder /app /app
```

### 6. 故障排除

#### 构建失败
```bash
# 清理Docker缓存
docker system prune -a

# 强制重新构建
docker-compose build --no-cache
```

#### 网络超时
```bash
# 增加超时时间
export DOCKER_CLIENT_TIMEOUT=120
export COMPOSE_HTTP_TIMEOUT=120
```

#### DNS问题
```bash
# 使用公共DNS
docker run --dns=8.8.8.8 --dns=114.114.114.114 ...
```

### 7. 推荐部署流程

1. **首次部署**：使用 `quick-deploy.bat` 快速测试
2. **生产环境**：配置 `.env` 后使用 `deploy.bat`
3. **网络问题**：使用 `Dockerfile.cn` 和国内镜像源

### 8. 性能对比

| 方案 | 构建时间 | 网络要求 | 适用场景 |
|------|----------|----------|----------|
| 官方源 | 10-30分钟 | 稳定国际网络 | 海外服务器 |
| 国内镜像源 | 2-5分钟 | 国内网络 | 中国大陆 |
| 简化版 | 1-3分钟 | 任意网络 | 快速测试 |

选择适合您网络环境的部署方案，可以大大提升构建速度！
