"""片倉椎菜(かたくら しいな)の3D素体を簡単な形の組み合わせで作り、設定画(正面・横)を描き出す。

使い方:
    python3 02_departments/manga/characters/shiina/build_shiina.py 出力先フォルダ
"""
import math
import os
import sys

import bpy
from mathutils import Vector

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- 材質(漫画のトーン用に灰色の濃さで塗り分ける) ----------
def mat(name, v):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (v, v, v, 1)
    bsdf.inputs["Roughness"].default_value = 1.0
    return m

SKIN = mat("skin", 0.95)
HAIR = mat("hair", 0.85)
WHITE = mat("cloth_white", 0.95)
DARK = mat("dark", 0.12)
MID = mat("mid", 0.35)
EYE = mat("eye", 0.05)
INNER_EAR = mat("inner_ear", 0.6)

def finish(obj, material, smooth=True, sub=0):
    obj.data.materials.append(material)
    if smooth:
        bpy.ops.object.shade_smooth()
    if sub:
        obj.modifiers.new("sub", "SUBSURF").levels = sub
    return obj

def sphere(loc, scale, material, sub=1, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    return finish(o, material, sub=sub)

def cyl(loc, r1, r2, depth, material, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    return finish(bpy.context.object, material)

def limb(a, b, r1, r2, material):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = cyl((a + b) / 2, r1, r2, d.length, material)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    return o

# ---------- 体(頭身は約6頭身) ----------
H = 0.27  # 頭の高さの半分
head = sphere((0, 0, 1.62), (0.17, 0.165, 0.19), SKIN)
sphere((0, -0.03, 1.52), (0.11, 0.1, 0.09), SKIN)  # あご
cyl((0, 0, 1.40), 0.045, 0.05, 0.12, SKIN)  # 首
cyl((0, 0, 1.38), 0.055, 0.055, 0.03, DARK)  # チョーカー

# 目(大きめ・縦長。ハイライト付き)
for x in (-0.065, 0.065):
    e = sphere((x, -0.155, 1.60), (0.038, 0.012, 0.055), EYE, sub=0)
    sphere((x + 0.012, -0.166, 1.625), (0.012, 0.004, 0.014), WHITE, sub=0)
    # まつげ(上まぶたの線)
    lash = cyl((x, -0.16, 1.655), 0.045, 0.045, 0.01, DARK, rot=(math.radians(90), 0, 0))
    lash.scale = (1, 0.25, 1)
# 口(小さく笑う)
m = sphere((0, -0.16, 1.51), (0.025, 0.006, 0.012), MID, sub=0)

# 胴体・ブラウス(パフスリーブ)
cyl((0, 0, 1.18), 0.13, 0.11, 0.38, WHITE)
sphere((0, -0.02, 1.25), (0.12, 0.09, 0.08), WHITE)  # 胸
for s in (-1, 1):
    sphere((s * 0.15, 0, 1.30), (0.075, 0.07, 0.075), WHITE)  # パフスリーブ
    limb((s * 0.17, 0, 1.25), (s * 0.22, -0.02, 0.98), 0.033, 0.028, SKIN)  # 上腕〜前腕
    limb((s * 0.22, -0.02, 0.98), (s * 0.24, -0.04, 0.88), 0.03, 0.026, DARK)  # 手袋
    sphere((s * 0.245, -0.045, 0.85), (0.03, 0.022, 0.04), DARK)  # 手

# ネクタイ
tie = cyl((0, -0.115, 1.22), 0.025, 0.04, 0.22, MID, verts=4)
tie.scale = (1, 0.25, 1)
sphere((0, -0.105, 1.335), (0.025, 0.012, 0.02), MID, sub=0)  # 結び目
# 腰の帯
cyl((0, 0, 0.98), 0.115, 0.115, 0.06, MID)

# スカート(フレア)
cyl((0, 0, 0.88), 0.30, 0.115, 0.17, DARK, verts=24)

# 脚
for s in (-1, 1):
    limb((s * 0.06, 0, 0.86), (s * 0.065, 0, 0.45), 0.055, 0.04, SKIN)
    limb((s * 0.065, 0, 0.45), (s * 0.065, 0, 0.08), 0.04, 0.03, SKIN)
    sphere((s * 0.065, -0.04, 0.04), (0.04, 0.08, 0.035), DARK)  # 靴

# ---------- 髪 ----------
sphere((0, 0.01, 1.66), (0.185, 0.18, 0.2), HAIR)  # 頭頂
# 前髪(束を数本)
for i, x in enumerate((-0.12, -0.06, 0, 0.06, 0.12)):
    b = cyl((x, -0.13, 1.71 - abs(x) * 0.4), 0.04, 0.008, 0.16, HAIR, rot=(math.radians(-15), 0, -x * 1.5))
# 後ろ髪(腰までのロング)
back = cyl((0, 0.07, 1.22), 0.2, 0.13, 0.85, HAIR)
back.scale = (1, 0.55, 1)
# 横の髪束(リボンで結ぶ細い房)
for s in (-1, 1):
    limb((s * 0.17, -0.05, 1.62), (s * 0.20, -0.02, 1.05), 0.035, 0.008, HAIR)
    rib = sphere((s * 0.175, -0.05, 1.56), (0.03, 0.02, 0.04), DARK, sub=0)  # リボン

# ---------- 狐耳・しっぽ ----------
for s in (-1, 1):
    ear = cyl((s * 0.12, 0.0, 1.88), 0.07, 0.0, 0.2, HAIR, rot=(0, s * math.radians(-18), 0), verts=3)
    ear.scale = (1, 0.45, 1)
    inner = cyl((s * 0.118, -0.018, 1.87), 0.045, 0.0, 0.15, INNER_EAR, rot=(0, s * math.radians(-18), 0), verts=3)
    inner.scale = (1, 0.3, 1)
tail = sphere((0.12, 0.30, 0.78), (0.14, 0.13, 0.32), HAIR, rot=(math.radians(35), math.radians(-20), 0))
sphere((0.18, 0.42, 1.02), (0.08, 0.08, 0.1), WHITE)  # しっぽの先(白)

# ---------- 撮影設定 ----------
world = bpy.data.worlds.new("paper")
world.color = (1, 1, 1)
scene.world = world
bpy.ops.object.light_add(type="SUN", location=(2, -3, 4), rotation=(math.radians(45), 0, math.radians(30)))
bpy.context.object.data.energy = 3.5

scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.view_settings.view_transform = "Standard"
scene.render.resolution_x = 600
scene.render.resolution_y = 1000
scene.render.film_transparent = False

scene.render.use_freestyle = True
scene.render.line_thickness_mode = "ABSOLUTE"
scene.render.line_thickness = 1.8
fs = scene.view_layers[0].freestyle_settings
fs.crease_angle = math.radians(120)
lineset = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("ink")
style = lineset.linestyle or bpy.data.linestyles.new("ink")
lineset.linestyle = style
style.color = (0, 0, 0)
style.thickness = 2.2
style.geometry_modifiers.new("wobble", "PERLIN_NOISE_1D").amplitude = 0.8

bpy.ops.object.camera_add()
cam = bpy.context.object
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.2
scene.camera = cam

views = {"front": ((0, -5, 1.0), (math.radians(90), 0, 0)),
         "side": ((5, 0, 1.0), (math.radians(90), 0, math.radians(90))),
         "back": ((0, 5, 1.0), (math.radians(90), 0, math.radians(180)))}
for name, (loc, rot) in views.items():
    cam.location, cam.rotation_euler = loc, rot
    scene.render.filepath = os.path.join(OUT, f"raw_{name}.png")
    bpy.ops.render.render(write_still=True)
print("done")
