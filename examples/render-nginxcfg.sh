#!/bin/bash -x
export NGINX='json:{"server_name": "www.myweb.com", "index_page": "index.php", "web_root": "/usr/local/www/myweb", "fcgi_params": "/usr/local/etc/nginx/myweb-fcgi-params", "fpm_socket": "/var/run/php-fpm/myweb.socket"}'
e2j2 -f nginx_vhost_config.conf.j2
unset NGINX
