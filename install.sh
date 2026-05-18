#!/usr/bin/env bash
set -e

REPO="https://github.com/burylife/ccwise.git"
INSTALL_DIR="$HOME/.ccwise"
BIN_PATH="/usr/local/bin/ccwise"

echo "Installing ccwise..."

# 克隆或更新
if [ -d "$INSTALL_DIR/.git" ]; then
    git -C "$INSTALL_DIR" pull --quiet
else
    git clone --quiet "$REPO" "$INSTALL_DIR"
fi

# 创建虚拟环境并安装依赖
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --quiet rich

# 写入可执行入口
cat > "$BIN_PATH" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/.venv/bin/python" "$INSTALL_DIR/ccwise.py" "\$@"
EOF
chmod +x "$BIN_PATH"

echo "Done. Run: ccwise"
