# Daily Show HN Blog

这是一个自动收集和展示 Hacker News 上 "Show HN" 帖子的 Flask 应用。

## 系统要求

- Python 3.8+
- pip
- virtualenv (推荐)

## 安装

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/ShowHN_Blog.git
   cd ShowHN_Blog
   ```

2. 创建并激活虚拟环境：
   ```
   python -m venv venv
   source venv/bin/activate  # 在 Windows 上使用 venv\Scripts\activate
   ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 配置

1. 复制 `.env.example` 文件并重命名为 `.env`：
   ```
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，设置必要的环境变量。

## 数据库初始化

1. 初始化数据库：
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

## 运行应用

1. 启动 Flask 开发服务器：
   ```
   flask run
   ```

2. 在浏览器中访问 `http://localhost:5000`

## 定期更新

应用配置为每24小时自动更新一次 Show HN 帖子。如果需要手动更新，可以运行：
