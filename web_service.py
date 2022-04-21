import gc
import multiprocessing
import re
import time
from glob import glob
from os import listdir, remove, system
from os.path import abspath, isfile, join

import cv2
import numpy as np
import neopixel
import board
from flask import Flask, render_template, request
from joblib import Parallel, delayed

width = 1280
height = 720

neopixel_pin = board.D10

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('tl_form.html')


@app.route('/data', methods=['POST', 'GET'])
def data():
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
        # remove previous video files
        to_remove = glob(join(output_path, "*.mp4")) + \
            glob(join(output_path, "*.avi"))
        for f in to_remove:
            remove(f)

        start_time = time.time()

        # split into threads
        num_cores = multiprocessing.cpu_count()
        thread_list = np.array_split(np.array(image_names), num_cores)
        Parallel(n_jobs=num_cores, prefer="threads")(
            delayed(video_thread)(thread_image_names, output_path, n, num_cores) for n, thread_image_names in enumerate(thread_list))

        # encode split videos into one mp4
        thread_names = sorted(glob(join(output_path, "*.avi")))
        render_name = f"render{int(time.time())}.avi"
        ffmpeg_in = f"\"concat:{'|'.join([f'{abspath(name)}' for name in thread_names])}\""
        ffmpeg_out = render_name.replace(
            "render", "web_render").replace("avi", "mp4")
        system(
            f"ffmpeg -y -i {ffmpeg_in} {abspath(join(output_path,ffmpeg_out))}")

        print(f"Took {time.time()-start_time}s to render")
        return ffmpeg_out

    def video_thread(image_names, output_path, n, threads):
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        file_name = f"thread_{n}.avi"
        video = cv2.VideoWriter(
            join(output_path, file_name),
            fourcc,
            frameSize=(width, height),
            fps=len(image_names)/(60/threads)
        )

        for image_name in image_names:
            img = cv2.imread(image_name)
            video.write(img)

        cv2.destroyAllWindows()
        video.release()
        return file_name

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


@app.route('/light')
def light():
    return render_template('light_form.html')


@app.route('/set_light', methods=['POST', 'GET'])
def set_light():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/' to submit form"
    if request.method == 'POST':
        field_names = ['R', 'G', 'B']
        form_data = request.form
        colors = tuple([int(form_data.get(name)) for name in field_names])
        neopixel.NeoPixel(neopixel_pin, 12).fill(colors)
        return light()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8000)
