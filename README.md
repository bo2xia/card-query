# 卡密查询系统

一个简单易用的卡密管理和查询系统，支持Docker部署。

## 功能特性

- 🔐 管理员登录系统
- 👥 账号管理（添加、删除、修改密码）
- 🎫 卡密管理（批量生成、查询、删除）
- 📊 使用统计和过期管理
- 🐳 Docker容器化部署
- 🔒 生产环境安全配置

## 快速开始

### 方式一：Docker部署（推荐）

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd card-query
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑.env文件，修改SECRET_KEY和数据库密码
   ```

3. **运行部署脚本**
   
   Linux/Mac:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
   
   Windows:
   ```cmd
   deploy.bat
   ```

4. **访问应用**
   - 应用地址: http://localhost:5000
   - 默认管理员: admin/admin123

### 方式二：手动Docker部署

```bash
# 启动所有服务
docker-compose up -d

# 仅启动应用和数据库（不包含Nginx）
docker-compose up -d web db

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式三：开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export FLASK_ENV=development
export SECRET_KEY=dev-secret-key

# 运行应用
python app.py
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| FLASK_ENV | 运行环境 | production |
| SECRET_KEY | Flask密钥 | 必须设置 |
| DATABASE_URL | 数据库连接 | SQLite |
| PORT | 应用端口 | 5000 |
| POSTGRES_DB | PostgreSQL数据库名 | cardquery |
| POSTGRES_USER | PostgreSQL用户名 | postgres |
| POSTGRES_PASSWORD | PostgreSQL密码 | 必须设置 |

### Docker服务

- **web**: Flask应用服务
- **db**: PostgreSQL数据库
- **nginx**: 反向代理（可选）

## 使用说明

### 管理员功能

1. **登录**: 使用默认账号 admin/admin123
2. **账号管理**: 添加用户账号，重置密码
3. **卡密生成**: 批量生成卡密，设置查询次数和有效期
4. **卡密管理**: 查看、删除卡密
5. **修改密码**: 修改管理员密码

### 用户查询

访问 `/query?card_key=卡密` 查询账号信息

## 生产环境部署

### 安全建议

1. **修改默认密码**: 首次部署后立即修改管理员密码
2. **设置强密钥**: 使用复杂的SECRET_KEY
3. **数据库安全**: 设置强数据库密码
4. **HTTPS**: 配置SSL证书启用HTTPS
5. **防火墙**: 限制数据库端口访问

### 性能优化

1. **Nginx代理**: 启用nginx服务处理静态文件
2. **数据库优化**: 根据需要调整PostgreSQL配置
3. **监控**: 配置日志监控和告警

### 备份

```bash
# 数据库备份
docker-compose exec db pg_dump -U postgres cardquery > backup.sql

# 恢复数据库
docker-compose exec -T db psql -U postgres cardquery < backup.sql
```

## 故障排除

### 常见问题

1. **端口占用**: 修改.env中的PORT变量
2. **数据库连接失败**: 检查数据库服务状态和连接配置
3. **权限问题**: 确保Docker有足够权限

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs web
docker-compose logs db

# 实时查看日志
docker-compose logs -f web
```

## 开发

### 项目结构

```
card-query/
├── app.py              # 主应用文件
├── requirements.txt    # Python依赖
├── Dockerfile         # Docker镜像配置
├── docker-compose.yml # Docker编排配置
├── templates/         # HTML模板
├── static/           # 静态文件
├── nginx/            # Nginx配置
└── logs/             # 日志文件
```

### 本地开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 设置开发环境
export FLASK_ENV=development
export SECRET_KEY=dev-key

# 运行应用
python app.py
```

## 许可证

MIT License
