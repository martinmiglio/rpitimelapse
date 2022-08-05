import gc
import multiprocessing
import re
import time
from glob import glob
from os import listdir, remove, system
from os.path import abspath, isfile, join

import cv2
import numpy as np
from flask import Flask, render_template, request
from joblib import Parallel, delayed

width = 1280
height = 720

app = Flask(__name__)

try:
    import board
    import neopixel
except ModuleNotFoundError:
    print("not running on raspberry pi!")
else:
    neopixel_pin = board.D12
    neopixel_count = 12
    lights = neopixel.NeoPixel(neopixel_pin, neopixel_count, auto_write=False)

    @app.route('/light', methods=['POST', 'GET'])
    def set_light():

        def rgb_from_hex(hex_color):
            return tuple([
                int(hex_color.replace("#", '')[i:i + 2], 16) for i in (0, 2, 4)
            ])

        if request.method == 'POST':
            form_data = request.form
            color = rgb_from_hex(form_data.get('color'))
            app.logger.info(f"Setting LED to {color}")
            for i in range(neopixel_count):
                lights[i] = color
            lights.show()
        return render_template('light_form.html')


@app.route('/')
def index():
    return render_template('tl_form.html')


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
    if button_string == 'Now' or not button_string:
        return 0
    value = re.search(r'\d+', button_string)
    value = 0 if value is None else int(value.group())
    return value*24 if "Day" in button_string else value


def get_images(hours_ago):
    IMAGE_DIRECTORY = "images"
    current_time = int(time.time())
    start_time = int(current_time - 3600 * hours_ago)
    app.logger.info(f'Getting images starting at {start_time}')
    files = sorted(filter(re.compile('img(.*).jpg').match,
                   listdir(IMAGE_DIRECTORY)), reverse=True)
    if hours_ago == 0:
        return [files[0]]
    else:
        return [abspath(join(IMAGE_DIRECTORY, file)) for file in files if current_time - 120 > int(file) > start_time]


def generate_video(image_names):
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
            img = cv2.imread(join(input_path, image_name))
            video.write(img)
        cv2.destroyAllWindows()
        video.release()
        return file_name

    input_path = "images/"
    output_path = "static/"

    # remove previous video files
    to_remove = glob(join(output_path, "*.mp4")) + \
        glob(join(output_path, "*.avi"))
    for f in to_remove:
        remove(f)

    # track time
    start_time = time.time()
    app.logger.info(
        f'{start_time}: Converting {len(image_names)} images...')

    # split into threads
    num_cores = min(multiprocessing.cpu_count(), len(image_names))
    app.logger.info(f'{start_time}: Using {num_cores} cores.')
    thread_list = np.array_split(np.array(image_names), num_cores)
    Parallel(n_jobs=num_cores, prefer="threads")(
        delayed(video_thread)(thread_image_names, output_path, n, num_cores) for n, thread_image_names in enumerate(thread_list))

    # reset timing
    app.logger.info(f"Took {time.time()-start_time}s to render")
    start_time = time.time()

    # encode split videos into one mp4
    thread_names = sorted(glob(join(output_path, "*.avi")))
    app.logger.info(
        f'{start_time}: Encoding {len(thread_names)} videos ...')
    render_name = f"render{int(time.time())}.avi"
    ffmpeg_in = f"\"concat:{'|'.join([f'{abspath(name)}' for name in thread_names])}\""
    ffmpeg_out = render_name.replace(
        "render", "web_render").replace("avi", "mp4")
    system(
        f"ffmpeg -y -i {ffmpeg_in} {abspath(join(output_path,ffmpeg_out))}".replace(';', ''))
    app.logger.info(f"Took {time.time()-start_time}s to encode")

    return ffmpeg_out


if __name__ == '__main__':
    app.run(use_reloader=False, host='0.0.0.0', port=80)
