import math

def get_srm_data(data):
    pass

def decode_string(arr):
    NAME_ENCODING = "あいうえおやゆよかきくけこわをんさしすせそがぎぐたちつてとげござなにぬねのじずぜはひふへほぞだぢまみむめもづでどらりるれろばびぶべぼぱぴぷぺぽゃゅょっぁぃぅぇぉアイウエオヤユヨカキクケコワヲンサシスセソガギグタチツテトゲゴザナニヌネノジズゼハヒフヘホゾダヂマミムメモヅデドラリルレロバビブベボパピプペポャュョッァィゥェォ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ「」?!,-<> 。~"

    return map(lambda x: NAME_ENCODING[x], arr)

# formatter can be number, string, or time
def get_value(offset, formatter = None, bits = 8, shift = 0):
    bytes = math.ceil((bits + shift) / 8)

def frames_to_timecode(frames, framerate=60.08):
    seconds = frames / framerate
    return '{h:02d}:{m:02d}:{s:02d}:{f:02d}' \
        .format(h=int(seconds/3600),
                m=int(seconds/60%60),
                s=int(seconds%60),
                f=round((seconds-int(seconds))*framerate))