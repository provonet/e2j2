e2j2
====

e2j2 (environment to jinja2 variables) is a commandline tool which will
render jinja2 templates to textfiles. all environment variables can be
used in the jinja2 templates, within the environment variables you can
use special tags which give you the option to insert json, json file
paths, base64 hashes, consul kv keys.

e2j2 is intended to be used within docker containers, you can simply add
the j2 extention to a configuration file and then run e2j2 before you're
starting the actual executable.

lets assume we want to render the following server block in nginx, if we
place the server configuration in a nginx include directory for example
/etc/nginx/conf.d

.. code:: bash

    server {
      server_name {{ NGINX.server_name }};
      listen 80;
      listen [::]:80;
      error_page 500 502 503 504 /50x.html;

      location / {
        index {{ NGINX.index_page }};
        root {{ NGINX.web_root }};
      }

      location ~ \.php$ {
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME  $document_root$fastcgi_script_name;
        fastcgi_pass unix:{{ NGINX.fpm_socket }};
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        include {{ NGINX.fcgi_params }};
        root {{ NGINX.web_root }};
        try_files $uri =404;
      }
    }

if you then set the NGINX environment variable within you're container,
running e2j2 will render the jinja2 template and place it in the same
folder.

.. code:: bash

    ~> set | grep NGINX
    NGINX='json:{"server_name": "www.myweb.com", "index_page": "index.php", "web_root": "/usr/local/www/myweb", "fcgi_params": "/usr/local/etc/nginx/myweb-fcgi-params", "fpm_socket": "/var/run/php-fpm/myweb.socket"}'
    ~> e2j2

    In: .
        rendering: nginx_vhost_config.conf.j2=>done => writing: nginx_vhost_config.conf=>done

    ~> cat nginx_vhost_config.conf
    server {
      server_name www.myweb.com;
      listen 80;
      listen [::]:80;
      error_page 500 502 503 504 /50x.html;

      location / {
        index index.php;
        root /usr/local/www/myweb;
      }

      location ~ \.php$ {
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME  $document_root$fastcgi_script_name;
        fastcgi_pass unix:/var/run/php-fpm/myweb.socket;
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        include /usr/local/etc/nginx/myweb-fcgi-params;
        root /usr/local/www/roundcube;
        try_files $uri =404;
      }
    }

you can also point to a json file by using the jsonfile: tag or place
you're configuration in a consul key/value store.
