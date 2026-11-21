#!/usr/bin/env bash
# 漫画制作部の作業環境をクラウド環境(Claude Code on the web)に用意する。
# Blender本体はダウンロードできないため、PyPIのbpy(Blenderのpythonモジュール版)を使う。
set -euo pipefail
python3 -c "import bpy" 2>/dev/null || pip install -q bpy
python3 -c "import PIL" 2>/dev/null || pip install -q pillow
python3 -c "import gradio_client" 2>/dev/null || pip install -q gradio_client
python3 -c "import bpy; print('Blender', bpy.app.version_string, 'ready')"
