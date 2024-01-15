import json
import os
import platform
import re

from flask import Flask, request, jsonify, render_template, send_from_directory
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

if platform.system() == "Windows":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = Flask(__name__)


@app.route('/source', methods=['POST'])
def docker_run():
    command = request.json.get('command')
    try:
        image = re.search(r' ([\w./-]+)$', command).group(1)
        name = re.search(r'--name\s+(.*?)\s', command).group(1)
        ports = re.findall(r'-p\s+(.*?):(.*?)(/udp)?\s', command)
        volumes = re.findall(r'-v\s+(.*?):(.*?)(?=\s|$)', command)
    except AttributeError:
        return jsonify('解析错误,请检查命令'), 200

    ports_dict = {f"{p[1]}{p[2] if p[2] else '/tcp'}": int(p[0]) for p in ports}
    volumes_dict = {f"{name}_{v[1].split('/')[-1]}_volume": {"bind": v[1], "mode": "rw"} for v in volumes}

    container_config = {
        'image': image,
        'name': name,
        'ports': ports_dict,
        'restart_policy': {'Name': 'always'}
    }

    if volumes_dict:
        container_config['volumes'] = volumes_dict

    return jsonify(container_config), 200


@app.route('/confirm', methods=['POST'])
def confirm():
    container_config = request.json.get('container_config')
    try:
        name = container_config['name']
    except TypeError:
        return jsonify('json格式错误')

    if os.path.exists('app.json'):
        with open('app.json', 'r') as f:
            app_data = json.load(f)
    else:
        app_data = {}

    app_data[name] = request.url_root + f"app/{name}/run.json"

    with open('app.json', 'w') as f:
        json.dump(app_data, f, indent=4)

    os.makedirs(f'app/{name}', exist_ok=True)
    with open(f'app/{name}/run.json', 'w') as f:
        json.dump(container_config, f, indent=4)

    return jsonify({"message": "Success"}), 200


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/app/<path:app_name>/run.json', methods=['GET'])
def static_proxy(app_name):
    return send_from_directory(f'app/{app_name}', 'run.json')


@app.route('/app.json', methods=['GET'])
def app_json():
    return send_from_directory('.', 'app.json')


if __name__ == '__main__':
    s = HTTPServer(WSGIContainer(app))
    port = 10010
    s.listen(port=port, address='0.0.0.0')
    print(f"Taichi_OS_Software_Source启动在0.0.0.0:{port}")
    IOLoop.current().start()
