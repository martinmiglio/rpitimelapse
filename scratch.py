import re
import time
import cv2
from glob import glob
from os import listdir, remove
from os.path import abspath, isfile, join

# choose codec according to format needed
width = 1280
height = 720


def get_images(hours_ago):
    IMAGE_DIRECTORY = "images"
    current_time = int(time.time())
    start_time = int(current_time - 3600 * hours_ago)
    files = []
    for f in sorted(listdir(IMAGE_DIRECTORY)):
        full_path = abspath(join(IMAGE_DIRECTORY, f))
        if isfile(full_path):
            match = re.search('img(.*).jpg', f)
            if match is not None:
                photo_time = int(match.group(1))
                if photo_time > start_time and photo_time < current_time - 120:
                    files.append(full_path)
    return files


def generate_video(image_names):
    output_path = "static/"
    file_name = f"render{int(time.time())}.avi"
    file_list = glob(join(output_path, "*.avi"))
    for f in file_list:
        remove(f)
    start_time = time.time()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(
        join(output_path, file_name),
        fourcc,
        frameSize=(width, height),
        fps=len(image_names)/30
    )

    for image_name in image_names:
        img = cv2.imread(image_name)
        video.write(img)

    cv2.destroyAllWindows()
    video.release()
    print(f"Took {time.time()-start_time}s to render gif")
    return file_name


generate_video(get_images(10))
