[project]
name = openresty
version = 1.13.6.1
vendor = openresty.org
homepage = http://openresty.org/
groups = dev/sys-srv
description = Dynamic web platform based on NGINX and LuaJIT

%build

PREFIX="{{.project__prefix}}"

cd {{.inpack__pack_dir}}/deps

if [ ! -f "openresty-{{.project__version}}.tar.gz" ]; then
    wget https://openresty.org/download/openresty-{{.project__version}}.tar.gz
fi

if [ -d "openresty-{{.project__version}}" ]; then
    rm -rf openresty-{{.project__version}}
fi
tar -zxf openresty-{{.project__version}}.tar.gz


if [ ! -f "openssl-1.0.2k.tar.gz" ]; then
    wget https://www.openssl.org/source/openssl-1.0.2k.tar.gz
fi

if [ -d "openssl-1.0.2k" ]; then
    rm -rf openssl-1.0.2k
fi
tar -zxf openssl-1.0.2k.tar.gz
cd openssl-1.0.2k
patch -p1 < ../openresty-{{.project__version}}/patches/openssl-1.0.2h-sess_set_get_cb_yield.patch
cd ..


if [ ! -f "pcre-8.40.tar.gz" ]; then
    wget https://ftp.pcre.org/pub/pcre/pcre-8.40.tar.gz
fi

if [ -d "pcre-8.40" ]; then
    rm -rf pcre-8.40
fi
tar -zxf pcre-8.40.tar.gz


cd openresty-{{.project__version}}
./configure \
    --user=action \
    --group=action \
    --with-pcre-jit \
    --with-luajit \
    --with-stream \
    --with-stream_ssl_module \
    --with-http_v2_module \
    --without-mail_pop3_module \
    --without-mail_imap_module \
    --without-mail_smtp_module \
    --with-http_stub_status_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_auth_request_module \
    --with-http_secure_link_module \
    --with-http_random_index_module \
    --with-http_gzip_static_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-threads \
    --with-file-aio \
    --prefix=$PREFIX \
    --sbin-path=$PREFIX/bin/nginx \
    --conf-path=$PREFIX/conf/nginx.conf \
    --http-log-path=$PREFIX/var/log/openresty.access.log \
    --error-log-path=$PREFIX/var/log/openresty.error.log \
    --with-luajit-xcflags='-DLUAJIT_ENABLE_LUA52COMPAT' \
    --pid-path=$PREFIX/var/run.openresty.pid \
    --with-openssl=../openssl-1.0.2k \
    --with-pcre=../pcre-8.40 \
    -j2

make -j2

des_tmp=/tmp/openresty_build_tmp
mkdir -p $des_tmp

sed -i 's/\tln\ \-sf/#\tln\ \-sf/g' Makefile
make install DESTDIR=$des_tmp

rm -rf   {{.buildroot}}/*
mkdir -p {{.buildroot}}/{bin,conf/conf.d,var/log,luajit}
mkdir -p {{.buildroot}}/nginx/{html,client_body_temp,fastcgi_temp,proxy_temp,scgi_temp,uwsgi_temp}

install $des_tmp/$PREFIX/bin/nginx     {{.buildroot}}/bin/nginx
strip -s {{.buildroot}}/bin/nginx

mv     $des_tmp/$PREFIX/lualib         {{.buildroot}}/
mv     $des_tmp/$PREFIX/luajit/lib     {{.buildroot}}/luajit/
rm -f  {{.buildroot}}/luajit/lib/*.a
rm -rf {{.buildroot}}/luajit/lib/lua
rm -rf {{.buildroot}}/luajit/lib/pkgconfig

cp -rp $des_tmp/$PREFIX/conf/*         {{.buildroot}}/conf/
rm -f  {{.buildroot}}/conf/*.default


cd {{.inpack__pack_dir}}
cp -rp misc/nginx.conf.tpl             {{.buildroot}}/conf/nginx.conf

sed -i 's/{\[worker_processes\]}/1/g'             {{.buildroot}}/conf/nginx.conf
sed -i 's/{\[events_worker_connections\]}/8192/g' {{.buildroot}}/conf/nginx.conf
sed -i 's/{\[http_server_default_listen\]}/80/g'  {{.buildroot}}/conf/nginx.conf
install {{.buildroot}}/conf/nginx.conf            {{.buildroot}}/conf/nginx.conf.default

install misc/index.html {{.buildroot}}/nginx/html/index.html
install misc/50x.html   {{.buildroot}}/nginx/html/50x.html
install misc/404.html   {{.buildroot}}/nginx/html/404.html

cd {{.inpack__pack_dir}}/deps
rm -rf openresty-{{.project__version}}
rm -rf openssl-1.0.2k
rm -rf pcre-8.40

%files

