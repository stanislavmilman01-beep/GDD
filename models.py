
import bpy
import math
import random
from mathutils import Vector

# ==========================================
# UNDERGROUND ROOM - TEST VERSION 0.1
# Blender 5.2
# ==========================================

random.seed(42)

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ------------------------------------------
# Materials
# ------------------------------------------

def create_material(name, color, roughness=0.85):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.roughness = roughness
    return mat

stone = create_material(
    "Stone - Dark Grey",
    (0.20, 0.22, 0.24)
)

floor_mat = create_material(
    "Floor - Grey Stone",
    (0.30, 0.29, 0.26)
)

wood = create_material(
    "Wood - Support Beams",
    (0.22, 0.095, 0.035)
)

rock_mat = create_material(
    "Rock Details",
    (0.12, 0.14, 0.16)
)

torch_mat = create_material(
    "Torch Flame",
    (1.0, 0.32, 0.04),
    0.4
)

# ------------------------------------------
# Object helpers
# ------------------------------------------

def cube(name, location, scale, material, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=location
    )

    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    if material:
        obj.data.materials.append(material)

    if bevel > 0:
        mod = obj.modifiers.new(
            "Soft Edges",
            'BEVEL'
        )
        mod.width = bevel
        mod.segments = 2

        obj.modifiers.new(
            "Weighted Normals",
            'WEIGHTED_NORMAL'
        )

    return obj


# ------------------------------------------
# Room dimensions
# ------------------------------------------

ROOM_SIZE = 10
WALL_HEIGHT = 5
WALL_THICKNESS = 0.5

# Floor
cube(
    "Room_Floor",
    (0, 0, -0.25),
    (ROOM_SIZE, ROOM_SIZE, 0.5),
    floor_mat
)

# Left and right walls
cube(
    "Wall_Left",
    (-5, 0, 2.5),
    (0.5, 10, 5),
    stone
)

cube(
    "Wall_Right",
    (5, 0, 2.5),
    (0.5, 10, 5),
    stone
)

# Back wall
cube(
    "Wall_Back",
    (0, 5, 2.5),
    (10, 0.5, 5),
    stone
)

# Front wall - two sections leave a doorway
cube(
    "Wall_Front_Left",
    (-3.5, -5, 2.5),
    (3, 0.5, 5),
    stone
)

cube(
    "Wall_Front_Right",
    (3.5, -5, 2.5),
    (3, 0.5, 5),
    stone
)

cube(
    "Wall_Front_Top",
    (0, -5, 4.25),
    (4, 0.5, 1.5),
    stone
)

# ------------------------------------------
# Wooden support beams
# ------------------------------------------

for y in [-3.8, 3.8]:

    # Vertical pillars
    for x in [-4.2, 4.2]:
        cube(
            "Wood_Pillar",
            (x, y, 2.5),
            (0.35, 0.35, 5),
            wood
        )

    # Horizontal beam
    cube(
        "Wood_Crossbeam",
        (0, y, 4.65),
        (8.7, 0.4, 0.35),
        wood
    )

# ------------------------------------------
# Decorative rocks
# ------------------------------------------

for i in range(18):
    x = random.uniform(-4.2, 4.2)
    y = random.uniform(-4.2, 4.2)

    # Keep center relatively clear
    if abs(x) < 2 and abs(y) < 2:
        continue

    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=random.uniform(0.2, 0.5),
        location=(x, y, 0.1)
    )

    obj = bpy.context.object
    obj.name = "Rock_Detail"
    obj.scale.z = random.uniform(0.5, 1.2)
    obj.data.materials.append(rock_mat)

# ------------------------------------------
# Torches
# ------------------------------------------

for x, y in [(-4.4, -2), (4.4, 2)]:

    cube(
        "Torch_Wood",
        (x, y, 2.2),
        (0.12, 0.12, 0.7),
        wood
    )

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12,
        ring_count=8,
        radius=0.22,
        location=(x, y, 2.65)
    )

    flame = bpy.context.object
    flame.name = "Torch_Flame"
    flame.data.materials.append(torch_mat)

    light_data = bpy.data.lights.new(
        name="Torch_Light",
        type='POINT'
    )
    light_data.energy = 450
    light_data.color = (1.0, 0.38, 0.12)
    light_data.shadow_soft_size = 1.5

    light_obj = bpy.data.objects.new(
        "Torch_Light",
        light_data
    )
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (x, y, 2.8)

# ------------------------------------------
# Ceiling
# ------------------------------------------

cube(
    "Room_Ceiling",
    (0, 0, 5.25),
    (10, 10, 0.5),
    stone
)

# ------------------------------------------
# Camera
# ------------------------------------------

bpy.ops.object.camera_add(
    location=(13, -16, 13)
)

camera = bpy.context.object
camera.name = "Room_Camera"

target = Vector((0, 0, 2))
direction = target - camera.location

camera.rotation_euler = direction.to_track_quat(
    '-Z', 'Y'
).to_euler()

camera.data.lens = 40
bpy.context.scene.camera = camera

# ------------------------------------------
# Lighting
# ------------------------------------------

bpy.ops.object.light_add(
    type='AREA',
    location=(0, 0, 8)
)

main_light = bpy.context.object
main_light.name = "Main_Light"
main_light.data.energy = 1800
main_light.data.shape = 'DISK'
main_light.data.size = 8

# ------------------------------------------
# Render settings
# ------------------------------------------

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'

scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100

scene.world.color = (0.05, 0.05, 0.05)

# Camera view
bpy.context.view_layer.objects.active = camera
bpy.ops.object.select_all(action='DESELECT')
camera.select_set(True)

print("Underground Room v0.1 created successfully!")
