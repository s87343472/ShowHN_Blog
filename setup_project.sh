#!/bin/bash

# 定义项目根目录
PROJECT_ROOT="ShowHN_Blog"

# 创建目录结构
mkdir -p "$PROJECT_ROOT"/{app/{main,api,models,services,utils,static,templates},tests}

# 创建文件
touch "$PROJECT_ROOT"/{config.py,run.py,requirements.txt,README.md}
touch "$PROJECT_ROOT"/app/{__init__.py,main/{__init__.py,routes.py,views.py},api/{__init__.py,routes.py},models/{__init__.py,post.py},services/{__init__.py,hn_service.py,rss_service.py},utils/{__init__.py,data_utils.py,screenshot_utils.py}}

# 函数：如果文件不存在或在错误的位置，则移动或创建
move_or_create() {
    if [ -f "$2" ]; then
        echo "File $2 already exists."
    elif [ -f "$1" ]; then
        mv "$1" "$2"
        echo "Moved $1 to $2"
    else
        touch "$2"
        echo "Created $2"
    fi
}

# 检查并更正文件位置
move_or_create "$PROJECT_ROOT/app/routes.py" "$PROJECT_ROOT/app/main/routes.py"
move_or_create "$PROJECT_ROOT/app/views.py" "$PROJECT_ROOT/app/main/views.py"

echo "Project structure has been set up or corrected."