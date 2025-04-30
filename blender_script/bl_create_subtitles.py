import bpy # BPY - Doc - https://docs.blender.org/api/current/index.html
import mathutils

# clears existing sequences in the Video Sequence Editor
# bpy.context.scene.sequence_editor_clear()

if not bpy.context.scene.sequence_editor:
    bpy.context.scene.sequence_editor_create()

scene = bpy.context.scene

scene_resolution_X = bpy.context.scene.render.resolution_x
scene_resolution_Y = bpy.context.scene.render.resolution_y

seq_editor = scene.sequence_editor

def create_subtitle(start: int, end: int, text: str, blend_time: int = 10, crop_time: int = 30, channel: int = 1):
    # creates effect strip and sets properties
    strip = seq_editor.sequences.new_effect(
        name="Subtitle",
        type='TEXT',
        channel=channel,
        frame_start=start,
        frame_end=end
    )
    strip.text=text
    strip.align_x='LEFT'
    strip.align_y='BOTTOM'
    strip.location = mathutils.Vector((0.05, 0.05))
    
    # creates keyframes for blending and cropping animation
    strip.blend_alpha = 0.0
    strip.keyframe_insert(data_path='blend_alpha', frame=start)
    strip.crop.max_x = scene_resolution_X
    strip.crop.keyframe_insert(data_path='max_x', frame=start)
    strip.blend_alpha = 1.0
    strip.keyframe_insert(data_path='blend_alpha', frame=start+blend_time)
    strip.crop.max_x = 0
    strip.crop.keyframe_insert(data_path='max_x', frame=start+crop_time)
    strip.blend_alpha = 1.0
    strip.keyframe_insert(data_path='blend_alpha', frame=end-blend_time)
    strip.blend_alpha = 0.0
    strip.keyframe_insert(data_path='blend_alpha', frame=end)

    return strip
    
def test():
    print('###########################################')
    print('###########################################')
    create_subtitle(start=1, end=300, text='test Text 1111', channel=1)
    create_subtitle(start=301, end=600, text='test Text 2222', channel=2)
    create_subtitle(start=601, end=900, text='test Text 3333', channel=3)

test()