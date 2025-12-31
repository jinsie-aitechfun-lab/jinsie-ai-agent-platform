#!/usr/bin/env bash

echo "=== Setup SILICONFLOW_API_KEY for this machine (zsh) ==="

read -s -p "请输入你的 SILICONFLOW_API_KEY（输入不可见，回车确认）: " SILICONFLOW_API_KEY
echo
if [ -z "$SILICONFLOW_API_KEY" ]; then
  echo "未输入 API Key，退出。"
  exit 1
fi

ZSHRC="$HOME/.zshrc"

# 如果 .zshrc 里还没有这一行，再追加
if ! grep -q "SILICONFLOW_API_KEY" "$ZSHRC" 2>/dev/null; then
  echo "" >> "$ZSHRC"
  echo "# AI 项目：SiliconFlow / 通义 API Key" >> "$ZSHRC"
  echo "export SILICONFLOW_API_KEY=\"$SILICONFLOW_API_KEY\"" >> "$ZSHRC"
  echo "已在 $ZSHRC 中追加 SILICONFLOW_API_KEY 配置。"
else
  echo "$ZSHRC 中已存在 SILICONFLOW_API_KEY，请手动检查是否需要更新。"
fi

echo
echo "现在执行：source ~/.zshrc"
echo "然后你可以跑：echo \$SILICONFLOW_API_KEY 检查是否生效。"
echo
echo "如果你打算使用 .env 文件，请在项目根目录创建 .env，并确保 .gitignore 已包含 .env。"
echo "=== Done ==="
