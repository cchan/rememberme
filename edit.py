import numpy as np
import cv2
import imageio

parts = [
    ("scaled/background/scaled_Clive_bass.mp4.small.mp4",        -5 + 130 + 0*96),
    ("scaled/background/scaled_drew-take1.mp4.small.mp4",        -5 + 35 + 0*96),
    ("scaled/background/scaled_Katherine_Take1.mp4.small.mp4",   -5 + 25 + 0*96),
    ("scaled/background/scaled_Kelly-1.mp4.small.mp4",           -5 + 190 + 0*96),
    ("scaled/background/scaled_Kyla-1.MOV.mp4.small.mp4",        -5 + 5 + 0*96),
    ("scaled/background/scaled_zoey-1.mp4.small.mp4",            -5 + 50 + 0*96),
    ("scaled/background/scaled_Tim_Take 1.mp4.mp4.small.mp4",    -5 + -125 + 0*96),
    ("scaled/background/scaled_yifan video 1.mov.mp4.small.mp4", -5 + 70 + 0*96),
]

solos = [
    ("scaled/solo/scaled_Clive_solo.mp4.small.mp4",        0,   96 * 0,         96 * 5.3),
    ("scaled/solo/scaled_Kyla-Solo-1.MOV.mp4.small.mp4",   10,  96 * 5.3,       96 * 9.3),
    ("scaled/solo/scaled_Clive_solo.mp4.small.mp4",        0,   96 * 9.3,       96 * 13.8),
    ("scaled/solo/scaled_zoey-solo-1.mp4.small.mp4",       25,  96 * 13.8,      96 * 17.6),
    ("scaled/solo/scaled_TimJ_Solo_2.mp4.small.mp4",       25,  96 * 17.6,      96 * 21.8),
    ("scaled/solo/scaled_Katherine_Solo.mp4.small.mp4",    55,  96 * 21.8,      96 * 25 + 48),
    ("scaled/solo/scaled_TimJ_Solo_1.mp4.small.mp4",       30,  96 * 25 + 48,   96 * 29.9),
    ("scaled/solo/scaled_Kelly-Solo-1.mp4.small.mp4",      115, 96 * 29.9,      96 * 100),
]

# solo_test = cv2.VideoCapture(solos[1][0])
# solo_test.set(cv2.CAP_PROP_POS_FRAMES, 5 + 0*96)
# print(solo_test)

part_captures = []
for video_name, offset in parts:
    cap = cv2.VideoCapture(video_name)
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(offset, 0))
    part_captures.append(cap)

solo_captures = [cv2.VideoCapture(video_name) for video_name, _, _, _ in solos]
prevframes = [None] * 8
prevsoloframe = None

VIDEO_LENGTH =  30 * 124 # 96 * 37

out = imageio.get_writer('out.mp4', fps=30)

slide1 = imageio.imread("Slide 1 - Title Card.png.resize.png")[:,:,:3]
slide2 = imageio.imread("Slide 2 - In memoriam.png.resize.png")[:,:,:3]

print(slide1.dtype)

for i in range(75):
    out.append_data(slide1)
for i in range(20):
    out.append_data(np.asarray(slide1 / 20 * (20-i) + slide2 / 20 * i, dtype=np.uint8))
for i in range(85):
    out.append_data(slide2)
slidefade = 60

def partframe(i):
    success, frame = part_captures[i].read()
    if not success:
        return prevframes[i]
    if parts[i][1] < 0:
        parts[i] = (parts[i][0], parts[i][1] + 1)
        # print(parts[i][1])
        part_captures[i].set(cv2.CAP_PROP_POS_FRAMES, 0)
    prevframes[i] = frame
    return frame

def soloframe(f):
    global prevsoloframe
    for i, source in enumerate(solos):
        if source[2] <= f <= source[3]:
            solo_captures[i].set(cv2.CAP_PROP_POS_FRAMES, source[1] + f)
            success, frame = solo_captures[i].read()
            if not success:
                return prevsoloframe
            prevsoloframe = frame
            return frame
    return prevsoloframe

try:
    for frame_num in range(VIDEO_LENGTH):
        if frame_num % 50 == 0:
            print(frame_num)
        # success, frame = part_captures[0].read()
        top = cv2.hconcat([partframe(0), partframe(1), partframe(2), partframe(3)])
        left = cv2.vconcat([partframe(4), partframe(5)])
        right = cv2.vconcat([partframe(6), partframe(7)])
        solo = soloframe(frame_num)
        bottom = cv2.hconcat([left, solo, right])
        frame = cv2.vconcat([bottom, top])
        # print(frame.shape)
        cvtframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if frame_num < 108:
            continue
        if slidefade > 0:
            cvtframe = slide2 / 60 * slidefade + cvtframe / 60 * (60 - slidefade)
            cvtframe = np.asarray(cvtframe, dtype=np.uint8)
            slidefade -= 1
        if frame_num > 120 * 30 and frame_num < 123 * 30:
            cvtframe = np.asarray(cvtframe / 90 * (123 * 30 - frame_num), dtype=np.uint8)
        if frame_num >= 123 * 30:
            cvtframe *= 0
        out.append_data(cvtframe)
except:
    for cap in part_captures:
        cap.release()
    for cap in solo_captures:
        cap.release()
    out.close()
    raise

# import cv2
# vidcap = cv2.VideoCapture(video_name)
# success,image = vidcap.read()
# count = 0
# while success:
#   success,image = part_captures[i].read()
#   count += 1

# for video in videos:
#     cv2.
