import re
import time
from multiprocessing import Process
from os import listdir
from os.path import isfile, join, abspath

import imageio
from flask import Flask, render_template, request

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
        output_gif = generate_gif(images_since)
        return render_template('data.html', filename="render.gif")


def data_to_hours(button_string):
    if not button_string:
        return 0
    value = int(re.search('[0-9]+', button_string).group())
    return value*24 if "Day" in button_string else value


def get_images(hours_ago):
    IMAGE_DIRECTORY = "images"
    current_time = time.time()
    start_time = int(current_time - 3600 * hours_ago)
    files = []
    for f in listdir(IMAGE_DIRECTORY):
        if isfile(abspath(join(IMAGE_DIRECTORY, f))):
            match = re.search('img(.*).jpg', f)
            if match is not None:
                if int(match.group(1)) > start_time:
                    files.append(f)
    return files


def generate_gif(image_names):
    output_path = "static/render.gif"
    with imageio.get_writer(output_path, mode='I') as writer:
        for image_name in image_names:
            image = imageio.imread(f"images/{image_name}")
            writer.append_data(image)


def make_page():
    pass


if __name__ == '__main__':
    plot_process = Process(target=make_page)
    plot_process.start()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8000)
    plot_process.join()
