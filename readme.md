## TaiChi OS 软件源管理软件

## 官方源

[taichi](https://taichi.evautocar.com/)

## 手动部署

            1. 创建目录
            mkdir /root/taichisource
            mkdir /root/taichisource/app
            touch /root/taichisource/app.json
            2. 运行镜像
            docker run -itd \
            --name software_source \
            -p 10010:10010 \
            -v /root/taichisource/app:/app/app \
            -v /root/taichisource/app.json:/app/app.json \
            --restart=always \
            fushin/taichi_os_software_source

## TaiChi OS 手动API部署

[POST] http://{host}:{ip}/api/containers/software_source/create

## TaiChi OS 软件商店部署

左上角-软件商店-TaiChi OS软件源-安装
