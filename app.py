import json
import os
import platform
import re
import shlex

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
    # 移除命令中的引号
    command = command.replace('"', '')
    args = shlex.split(command, posix=False)

    try:
        name = None
        for i, arg in enumerate(args):
            if arg.startswith('--name='):
                name = arg.split('=')[1]
                break
            elif arg == '--name':
                name = args[i + 1]
                break

        if name is None:
            return jsonify('错误: 命令中没有找到 --name 参数'), 200

        ports = [args[i + 1] for i, x in enumerate(args) if x == '-p']
        volumes = [args[i + 1] for i, x in enumerate(args) if x == '-v']
        envs = [args[i + 1] for i, x in enumerate(args) if x == '-e']
    except (ValueError, IndexError) as e:
        return jsonify(f'解析错误,请检查命令{e}'), 200

    # 获取镜像名
    image = None
    for arg in reversed(args):
        if '/' in arg:
            image = arg
            break

    if image is None:
        return jsonify('错误: 命令中没有找到镜像名'), 200

    ports_dict = {p.split(':')[1]: int(p.split(':')[0]) for p in ports if ':' in p}
    volumes_dict = {f"{name}_{v.split(':')[1].split('/')[-1]}_volume": {"bind": v.split(':')[1], "mode": "rw"} for v in
                    volumes}
    envs_dict = {e.split('=')[0]: e.split('=')[1] for e in envs if '=' in e}

    container_config = {
        'image': image,
        'name': name,
        'ports': ports_dict,
        'restart_policy': {'Name': 'always'}
    }

    if volumes_dict:
        container_config['volumes'] = volumes_dict
    if envs_dict:
        container_config['env'] = envs_dict

    return jsonify(container_config), 200


@app.route('/confirm', methods=['POST'])
def confirm():
    container_config = request.json.get('container_config')
    description = request.json.get('description')  # 获取软件简介
    try:
        name = container_config['name']
    except TypeError:
        return jsonify('json格式错误')

    if os.path.exists('app.json') and os.path.getsize('app.json') > 0:
        with open('app.json', 'r') as f:
            app_data = json.load(f)
    else:
        app_data = {}

    app_data[name] = {
        "url": request.url_root + f"app/{name}/run.json",
        "description": description  # 保存软件简介
    }

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
def run_json(app_name):
    return send_from_directory(f'app/{app_name}', 'run.json')


@app.route('/app.json', methods=['GET'])
def app_json():
    return send_from_directory('.', 'app.json')


@app.route('/delete/<app_name>', methods=['DELETE'])
def delete_app(app_name):
    try:
        # 删除 run.json 文件
        run_json_path = f'app/{app_name}/run.json'
        if os.path.exists(run_json_path):
            os.remove(run_json_path)

        # 删除应用目录
        app_dir_path = f'app/{app_name}'
        if os.path.exists(app_dir_path):
            os.rmdir(app_dir_path)

        # 从 app.json 中删除应用条目
        with open('app.json', 'r') as f:
            app_data = json.load(f)
        if app_name in app_data:
            del app_data[app_name]

        # 将更新后的内容写回 app.json
        with open('app.json', 'w') as f:
            json.dump(app_data, f, indent=4)

        return jsonify({"message": "Success"}), 200
    except OSError as e:
        return jsonify({"message": f"文件操作错误: {str(e)}"}), 500
    except json.JSONDecodeError as e:
        return jsonify({"message": f"JSON操作错误: {str(e)}"}), 500

if __name__ == '__main__':
    s = HTTPServer(WSGIContainer(app))
    port = 10010
    s.listen(port=port, address='0.0.0.0')
    print(f"Taichi_OS_Software_Source启动在0.0.0.0:{port}")
    IOLoop.current().start()
