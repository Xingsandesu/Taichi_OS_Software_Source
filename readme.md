## TaiChi OS 软件源管理软件

## 官方源

app.kookoo.top

## 手动部署

mkdir /root/taichisource &&
mkdir /root/taichisource/app &&
touch /root/taichisource/app.json &&
docker run -itd \
--name taichi_os_software_source \
-p 10010:10010 \
-v /root/taichisource/app:/app/app \
-v /root/taichisource/app.json:/app/app.json \
--restart=always \
fushin/taichi_os_software_source

## TaiChi OS 手动API部署

[POST] http://{host}:{ip}/api/containers/software_source/create

## TaiChi OS 软件商店部署

左上角-软件商店-TaiChi OS软件源-安装