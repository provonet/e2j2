e2j2
====

What is e2j2?
-------------

e2j2 (environment to jinja2 variables) is a commandline tool which will
render jinja2 templates to textfiles. all environment variables can be
used in the jinja2 templates, within the environment variables you can
use special tags which give you the option to insert json, json file
paths, base64 hashes, consul kv keys.

e2j2 is intended to be used within docker containers, you can simply add
the j2 extention to a configuration file and then run e2j2 before you're
starting the actual executable.

Example:
--------

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

if you then set the NGINX environment variable, running e2j2 will render
the jinja2 template and place it in the same folder:

.. code:: bash

    ~> export NGINX=export NGINX='json:
    {
    "server_name": "www.myweb.com",
    "index_page": "index.php",
    "web_root": "/usr/local/www/myweb",
    "fcgi_params": "/usr/local/etc/nginx/myweb-fcgi-params",
    "fpm_socket": "/var/run/php-fpm/myweb.socket"
    }'
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

Environment variable examples:
------------------------------

Plain environment variable:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

setting:

::

    MYENVVAR='plain environment variable'

will render envvar-example.j2 to:

::

    This is a plain environment variable

Tag json:
~~~~~~~~~

Example:

setting:

::

    MYJSONVAR='json:{"key": "json-example"}'

will render json-example.j2 to:

::

    This is a json-example

Tag jsonfile:
~~~~~~~~~~~~~

Example:

setting:

::

    MYJSONFILEVAR='jsonfile:jsonfile-example.json'

will render jsonfile-example.j2 to:

::

    This is a jsonfile example with subkey

Tag base64:
~~~~~~~~~~~

Example:

Setting:

::

    export MYBASE64VAR='base64:YmFzZTY0IGV4YW1wbGU='

will render base64-example.j2 to:

::

    This is a base64 example

Tag consul:
~~~~~~~~~~~

Configuration:

You can configure the consul tag by setting the CONSUL\_CONFIG
environment variable. The following config items are supported:

+----------+----------------------------+-------------+
| Item     | Explanation                | Default     |
+==========+============================+=============+
| scheme   | url scheme http or https   | http        |
+----------+----------------------------+-------------+
| host     | consul host                | localhost   |
+----------+----------------------------+-------------+
| port     | consul http(s) port        | 8500        |
+----------+----------------------------+-------------+
| token    | consul token               | none        |
+----------+----------------------------+-------------+

Config example:

::

    $ read -d '' CONSUL_CONFIG << EOF
    > {
    >   "scheme": "https",
    >   "host": "consul.foobar.tld",
    >   "port": 443,
    >   "token": "abcdef01-0123-abcd-1234-0123456789ab"
    > }
    > EOF

Example:

Setting:

key: consulvar in consul to value: consul example

and

::

    export MYCONSULVAR='consul:consulvar'

will render consul-example.j2 to:

::

    This is a consul example
