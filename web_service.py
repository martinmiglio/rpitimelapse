from glob import glob
import re
import time
from os import listdir, remove
from os.path import abspath, isfile, join

from flask import Flask, render_template, request
from PIL import Image

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
        return render_template('data.html', filename=generate_gif(images_since))


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
    for f in listdir(IMAGE_DIRECTORY):
        full_path = abspath(join(IMAGE_DIRECTORY, f))
        if isfile(full_path):
            match = re.search('img(.*).jpg', f)
            if match is not None:
                photo_time = int(match.group(1))
                if photo_time > start_time and photo_time < current_time - 120:
                    files.append(Image.open(full_path, mode='r'))
    return files


def generate_gif(images):
    output_path = "static/"
    file_name = f"render{int(time.time())}.gif"
    file_list = glob(join(output_path, "*.gif"))
    for f in file_list:
        remove(f)
    start_time = time.time()
    images[0].save(
        join(output_path, file_name),
        save_all=True,
        optimize=False,
        append_images=images[1:],
        loop=0
    )
    print(f"Took {time.time()-start_time}s to render gif")
    return output_path


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=80)
