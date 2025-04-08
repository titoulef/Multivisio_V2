import multivisio
import cv2

def main():
    input_video_path1 = ('input_videos/hall2.mp4')
    input_video_path = ('http://172.20.10.12:81/stream')
    photo1 = ('input_videos/vue1.mp4')
    photo2 = ('input_videos/vue2.mp4')

    #show
    multivisio.loop(input_video_path1, fpsDivider=5, videoScale=0.5)
    #multivisio.loop2(photo1, photo2, fpsDivider=1, videoScale=0.5)



if __name__ == '__main__':
    main()