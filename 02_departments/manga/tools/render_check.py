"""動作確認用: サンプル立体を、陰影3階調の漫画風で描き出す。

使い方:
    bash 02_departments/manga/tools/setup.sh
    python3 02_departments/manga/tools/render_check.py 出力先.png
"""
import sys

import bpy
from PIL import Image

out = sys.argv[1] if len(sys.argv) > 1 else "render_check.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
bpy.ops.object.shade_smooth()
bpy.context.object.modifiers.new("smooth", "SUBSURF").levels = 2
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -1))
bpy.ops.object.camera_add(location=(1.5, -4, 0.8), rotation=(1.45, 0, 0.35))
scene.camera = bpy.context.object
bpy.ops.object.light_add(type="SUN", location=(2, -2, 3))
bpy.context.object.data.energy = 4

world = bpy.data.worlds.new("paper")
world.color = (1, 1, 1)
scene.world = world

scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.view_settings.view_transform = "Standard"
scene.render.resolution_x = scene.render.resolution_y = 600

# 線画(Freestyle): 線を少し揺らして手描き感を出す
scene.render.use_freestyle = True
fs = scene.view_layers[0].freestyle_settings
lineset = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("ink")
style = lineset.linestyle or bpy.data.linestyles.new("ink")
lineset.linestyle = style
style.thickness = 3
style.geometry_modifiers.new("wobble", "PERLIN_NOISE_1D").amplitude = 1.5

scene.render.filepath = out
bpy.ops.render.render(write_still=True)

# 陰影を白・灰・黒の3階調に分けて、トーン風にする
img = Image.open(out).convert("L")
img.point(lambda v: 255 if v > 170 else (150 if v > 90 else 60)).save(out)
print("saved", out)
