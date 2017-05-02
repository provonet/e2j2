#!/bin/bash -x
export NGINX='json:{"server_name": "www.myweb.com", "index_page": "index.php", "web_root": "/usr/local/www/roundcube", "fcgi_params": "/usr/local/etc/nginx/myweb-fcgi-params", "fpm_socket": "/var/run/php-fpm/myweb.socket"}'
e2j2  --searchlist .
unset NGINX
