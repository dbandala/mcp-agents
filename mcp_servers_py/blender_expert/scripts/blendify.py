# Script to render cube
from blendify import scene
from blendify.materials import PrincipledBSDFMaterial
from blendify.colors import UniformColors
# Add light
scene.lights.add_point(strength=1000, translation=(4, -2, 4))
# Add camera
scene.set_perspective_camera((512, 512), fov_x=0.7, rotation=(0.82, 0.42, 0.18, 0.34), translation=(5, -5, 5))
# Create material
material = PrincipledBSDFMaterial()
# Create color
color = UniformColors((0.0, 1.0, 0.0))
# Add cube mesh
scene.renderables.add_cube_mesh(1.0, material, color)
# Render scene
scene.render(filepath="cube.png")