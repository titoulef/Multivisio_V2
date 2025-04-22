import multivisio
import cv2

def main():
    input_video_path1 = ('input_videos/hall3.mp4')
    input_video_path = ('http://172.20.10.12/stream')
    input_video_path2 = ('http://172.20.10.14:81/stream')

    cam1 = ('input_videos/cam1.mp4')
    cam2 = ('input_videos/cam2.mp4')

    vue1 = ('input_videos/vue1.mp4')
    vue2 = ('input_videos/vue2.mp4')

    #show
    multivisio.loopRec(input_video_path1, fpsDivider=5, videoScale=0.5)
    #multivisio.loop2(cam1, cam2, fpsDivider=10, videoScale=0.5)
    #multivisio.loop2(vue1, vue2, fpsDivider=1, videoScale=0.5)



if __name__ == '__main__':
    main()