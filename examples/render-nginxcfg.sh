#!/bin/bash -x
set -o allexport
SERVER_NAME=www.myweb.com
NGINX='json:{"server_name": "{{ SERVER_NAME }}", "index_page": "index.php", "web_root": "/usr/local/www/myweb", "fcgi_params": "/usr/local/etc/nginx/myweb-fcgi-params", "fpm_socket": "/var/run/php-fpm/myweb.socket"}'
set +o allexport
e2j2 -f nginx_vhost_config.conf.j2 -2
unset NGINX
