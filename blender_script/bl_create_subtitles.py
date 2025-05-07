import bpy # BPY - Doc - https://docs.blender.org/api/current/index.html
import mathutils
import re

# clears existing sequences in the Video Sequence Editor
bpy.context.scene.sequence_editor_clear()

if not bpy.context.scene.sequence_editor:
    bpy.context.scene.sequence_editor_create()

###################
#### CONSTANTS ####
###################

SEQ_EDITOR = bpy.context.scene.sequence_editor
SCENE_FRAMES_PER_SECOND = bpy.context.scene.render.fps
SCENE_RESOLUTION_X = bpy.context.scene.render.resolution_x
SCENE_RESOLUTION_Y = bpy.context.scene.render.resolution_y
SCENE_FRAME_START = bpy.context.scene.frame_start
SCENE_FRAME_END = bpy.context.scene.frame_end

INPUT_FILE = '<<FILENAME>>'
AVERAGE_CHAR_WIDTH = 32
MAX_WIDTH = SCENE_RESOLUTION_X * 0.8

###################

def castFloat(text: str):
    try:
        return float(text)
    except ValueError:
        return False

def read_file(filename: str):
    lines = []
    f = open(file=filename, mode='r', encoding='utf-8')
    try:
        for line in f:
            lines.append(line)
    except IOError as error:
        print(f"Error while trying reading from file: {error}")
        exit(1)
    finally:
        f.close()
    
    return lines

def parseFile(filename: str):
    lines = read_file(filename=filename)
    subtitles = []
    for line in lines:
        if line and not line.strip() == '':
            sub = Subtitle()
            sub.parseString(text=line)
            subtitles.append(sub)
    return subtitles

class Subtitle:
    def __init__(self, framesPerSecond: int = SCENE_FRAMES_PER_SECOND):
        self.framesPerSecond = framesPerSecond
        self.text = ''
        self.start = 0
        self.end = 0
        self.startFrame = 0
        self.endFrame = 0
        
    def parseString(self, text: str):
        pattern = re.compile("(.+?);\\((.+?),(.+?)\\)")
        if(pattern.match(text)):
            matches = re.search(pattern, text)
            self.text = matches.group(1).strip()
            self.start = castFloat(matches.group(2).strip())
            self.end = castFloat(matches.group(3).strip())
            self.startFrame = int(self.start * self.framesPerSecond) if not self.start is False else False
            self.endFrame = int(self.end * self.framesPerSecond) if not self.end is False else False
    
    def setEnd(self, num: float|bool):
        self.end = num
        self.endFrame = int(num * self.framesPerSecond) if not num is False else SCENE_FRAME_END

    def setStart(self, num: float|bool):
        self.start = num
        self.startFrame = int(num * self.framesPerSecond) if not num is False else SCENE_FRAME_START

def merge_subtitles(subtitles: list[Subtitle]):
    sub = Subtitle()
    subs = []
    for subtitle in subtitles:
        newText = f"{sub.text} {subtitle.text}".strip()
        if len(newText)*AVERAGE_CHAR_WIDTH < MAX_WIDTH:
            sub.text = newText
            sub.setEnd(subtitle.end)
        else:
            sub.setEnd(subtitle.start)
            subs.append(sub)
            sub = subtitle
    if len(sub.text) > 0:
        subs.append(sub)
    return subs

def create_subtitle(start: int, end: int, text: str, blend_time: int = 10, crop_time: int = 30, channel: int = 1):
    # creates effect strip and sets properties
    strip = SEQ_EDITOR.sequences.new_effect(
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
    strip.crop.max_x = SCENE_RESOLUTION_X
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

subtitles = parseFile(INPUT_FILE)
mergedSubtitles = merge_subtitles(subtitles)
for sub in mergedSubtitles:
    create_subtitle(start=sub.startFrame, end=sub.endFrame, text=sub.text, channel=2)