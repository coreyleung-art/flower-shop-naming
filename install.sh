#!/bin/bash
# ============================================================
# 花店物品命名审查工具 - 独立安装脚本
# 支持: macOS / Linux / Windows (Git Bash)
# ============================================================

set -e

REPO_URL="https://github.com/coreyleung-art/flower-shop-naming.git"
INSTALL_DIR="$HOME/.flower-shop-naming"
BIN_DIR="$HOME/.local/bin"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  花店物品命名审查工具 安装程序${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查Python
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}错误: 未找到Python，请先安装Python 3.8+${NC}"
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓${NC} 检测到Python版本: $PYTHON_VERSION"
}

# 安装方式选择
echo "请选择安装方式:"
echo "  1) 从GitHub克隆并安装 (推荐)"
echo "  2) 本地安装 (当前目录)"
echo "  3) pip安装 (PyPI)"
echo ""
read -p "请输入选项 [1-3]: " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}正在从GitHub克隆...${NC}"

        # 清理旧安装
        if [ -d "$INSTALL_DIR" ]; then
            echo "清理旧安装目录..."
            rm -rf "$INSTALL_DIR"
        fi

        # 克隆仓库
        git clone "$REPO_URL" "$INSTALL_DIR"

        # 创建可执行脚本
        mkdir -p "$BIN_DIR"

        cat > "$BIN_DIR/flower-naming" << EOF
#!/bin/bash
$PYTHON_CMD "$INSTALL_DIR/item_naming_cli.py" "\$@"
EOF
        chmod +x "$BIN_DIR/flower-naming"

        echo ""
        echo -e "${GREEN}✓ 安装完成!${NC}"
        echo ""
        echo "使用方法:"
        echo "  flower-naming \"商品名称\""
        echo ""
        echo "如需全局使用，请将以下路径添加到PATH:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
        echo "或将以上命令添加到 ~/.bashrc 或 ~/.zshrc"
        ;;

    2)
        echo ""
        echo -e "${YELLOW}本地安装模式...${NC}"

        # 创建快捷命令
        CURRENT_DIR=$(pwd)

        cat > "./flower-naming" << EOF
#!/bin/bash
$PYTHON_CMD "$CURRENT_DIR/item_naming_cli.py" "\$@"
EOF
        chmod +x "./flower-naming"

        echo ""
        echo -e "${GREEN}✓ 安装完成!${NC}"
        echo ""
        echo "使用方法:"
        echo "  ./flower-naming \"商品名称\""
        ;;

    3)
        echo ""
        echo -e "${YELLOW}使用pip安装...${NC}"
        pip install git+"$REPO_URL"
        echo ""
        echo -e "${GREEN}✓ 安装完成!${NC}"
        echo ""
        echo "使用方法:"
        echo "  flower-naming \"商品名称\""
        ;;

    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  感谢使用花店物品命名审查工具!${NC}"
echo -e "${GREEN}========================================${NC}"
