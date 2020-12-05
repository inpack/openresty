
worker_processes auto;
worker_cpu_affinity auto;

error_log /opt/openresty/openresty/var/log/openresty.error.log;

events {
    worker_connections {[events_worker_connections]};
}

http {
    include           /opt/openresty/openresty/conf/mime.types;
    default_type      application/octet-stream;    
    sendfile          on;
    keepalive_timeout 65;
    fastcgi_buffers   8 128k;
    send_timeout      300;
    server_tokens     off;

    gzip on;
    gzip_types text/plain;
    gzip_types text/css;
    gzip_types text/javascript application/javascript application/x-javascript;
    gzip_types application/json;
    gzip_types text/xml application/xml application/xml+rss;
    gzip_types image/jpeg image/gif image/png image/svg+xml;

    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    server {
        listen      8080;
        server_name localhost;

        location / {
            root  /opt/openresty/openresty/nginx/html;
            index index.html index.htm;
        }

        error_page 404             /404.html;
        error_page 500 502 503 504 /50x.html;
        
        location = /50x.html {
            root /opt/openresty/openresty/nginx/html;
        }
    }

    include /opt/openresty/openresty/conf/conf.d/*.conf;
}
