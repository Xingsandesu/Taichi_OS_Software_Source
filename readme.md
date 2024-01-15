## TaiChi OS 软件源管理软件

mkdir /root/taichisource && mkdir /root/taichisource/app && touch /root/taichisource/app.json

docker run -itd \
--name taichi_os_software_source \
-p 10010:10010 \
-v /root/taichisource/app:/app/app \
-v /root/taichisource/app.json:/app/app.json \
--restart=always \
fushin/taichi_os_software_source