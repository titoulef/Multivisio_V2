import multivisio
import cv2

def main():
    # Set the video scale
    videoScale = 0.5
    # Set the video path and keypoints

    #différents types de inputs
    #caméra IP
    input_stream_path = ('http://172.20.10.12/stream')
    input_stream_path2 = ('http://172.20.10.14:81/stream')

    #vidéos de test
    videoTestHall1 = ('input_videos/hall1.mp4')
    keypointsHall1 = [int(k * videoScale) for k in [282, 244, 543, 251, 641, 388, 159, 369]]
    videoTestHall2 = ('input_videos/hall2.mp4')
    keypointsHall2 = [int(k * videoScale) for k in [275, 205, 545, 205, 640, 335, 180, 320]]
    videoTestHall3 = ('input_videos/hall3.mp4')
    keypointsHall3 = [int(k * videoScale) for k in [225, 252, 447, 184, 561, 265, 261, 390]]

    DeuxZonesCam1 = ('input_videos/2zonesCam1carré.mp4')
    keypointsDeuxZonesCam1 = [int(k * videoScale) for k in [217, 346, 555, 364, 543, 627, 59, 580]]
    DeuxZonesCam2 = ('input_videos/2zonesCam2carré.mp4')
    keypointsDeuxZonesCam2 = [int(k * videoScale) for k in [188, 340, 532, 332, 632, 602, 104, 598]]

    DeuxVueCam1 = ('input_videos/2vueCam1.mp4')
    keypointsDeuxVueCam1 = [int(k * videoScale) for k in [486, 346, 828, 328, 925, 617, 442, 631]]  # 2VueCam1
    DeuxVueCam2 = ('input_videos/2vueCam2.mp4')
    keypointsDeuxVueCam2 = [int(k * videoScale) for k in [328, 372, 502, 173, 804, 260, 662, 499]]  # 2VueCam2

    #loop pour une vidéo
    #multivisio.loop(videoTestHall2, keypointsHall2, fpsDivider=5, videoScale=videoScale)
    #multi-caméra
    #scénario 1 : deux cams qui filment deux zones
    multivisio.loop2(DeuxZonesCam1, DeuxZonesCam2, keypointsDeuxZonesCam1, keypointsDeuxZonesCam2, fpsDivider=5, videoScale=videoScale)

    #scénario 2 : deux cams filment une meme zone sous 2 angles différents
    #multivisio.loop2_masked(DeuxVueCam1, DeuxVueCam2, keypointsDeuxVueCam1, keypointsDeuxVueCam2, fpsDivider=5, videoScale=videoScale)

if __name__ == '__main__':
    main()