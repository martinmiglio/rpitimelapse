import gc
import re
import time
from glob import glob
from os import listdir, remove, system
from os.path import abspath, isfile, join

import cv2
from flask import Flask, render_template, request
from PIL import Image, UnidentifiedImageError

width = 1280
height = 720

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('form.html')


@app.route('/data', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        form_data = request.form
        number_of_hours = data_to_hours(form_data.get('duration'))
        images_since = get_images(number_of_hours)
        video_name = generate_video(images_since)
        del images_since
        gc.collect()
        return render_template('data.html', filename=video_name, width=width, height=height)


def data_to_hours(button_string):
    if not button_string:
        return 0
    value = int(re.search('[0-9]+', button_string).group())
    return value*24 if "Day" in button_string else value


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
    file_name = f"render{int(time.time())}.mp4"
    file_list = glob(join(output_path, "*.mp4"))
    for f in file_list:
        remove(f)
    start_time = time.time()
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
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
    system(f"ffmpeg -i {join(output_path,file_name)} -vcodec h264 -preset ultrafast {join(output_path,file_name)}")
    print(f"Took {time.time()-start_time}s to render gif")
    return file_name


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8000)
