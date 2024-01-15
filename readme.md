## TaiChi OS 软件源管理软件

mkdir /root/taichisource

docker run -itd \
--name taichi_os_software_source \
-p 10010:10010 \
-v /root/taichisource:/app \
--restart=always \
fushin/taichi_os_software_source
