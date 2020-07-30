e2j2 [|Build Status| |Coverage Status|]
=======================================

.. contents:: Table of contents:

What is e2j2?
-------------

e2j2 (environment to jinja2 variables) is a commandline tool which will
render jinja2 templates to textfiles. all environment variables can be
used in the jinja2 templates, within the environment variables you can
use special tags which give you the option to insert json, json file
paths, base64 hashes, consul kv keys.

e2j2 can be used within docker containers, or for other simple configuration templating tasks. Within a docker container you can simply add the j2 extention to a configuration file, or to multiple files within one or more folder structures and then run e2j2 as part of your docker entrypoint script.

Command line switches and config file
-------------------------------------
Most flags can be set on either the command line or in a json formatted config file. The following flags / configuration keys are supported:

=========================== ==================== ======================================= ======= ==============================================================================
Switch                      Type                 Config key                              Type         Description
=========================== ==================== ======================================= ======= ==============================================================================
-h, --help                                                                                       Show help text and exit
-v, --version                                                                                    Show version number
-e, --ext, --extension      string               extension                               string  Jinja2 file extention (default: .j2)
-f, --filelist              comma separated list filelist                                array   List of jinja2 templates
-s, --searchlist            comma separated list searchlist                              array   List of directories to search for templates (default: current directory)
-N, --noop                                                                                       skip writing template to disk
-r, --recursive                                  recursive                               boolean Traverse recursively through the search list
--no-color, --nocolor                            no_color                                boolean Disable ANSI color
-2, --twopass                                    twopass                                 boolean Enable two pass rendering
--block_start               string               block_start                             string  Block marker start (default: '{%'}
--block_end                 string               block_end                               string  Block marker start (default: '%}'}
--variable_start            string               block_start                             string  Variable marker start (default: '{%'}
--variable_end              string               variable_end                            string  Variable marker end (default: '%}'}
--comment_start             string               comment_start                           string  Comment marker start (default: '{#'}
--comment_end               string               comment_end                             string  Comment marker start (default: '#}'}
-w, --env_whitelist         comma separated list env_whitelist                           array   List of envars to include
-b, --env_blacklist         comma separated list env_blacklist                           array   List of envars to exclude
-P, --copy_file_permissions                      copy_file_permissions                   boolean Copy file permissions and ownership from template to rendered file
-S, --stacktrace                                 stacktrace                              boolean Include stacktrace in error file
-c, --config                string                                                               Config file path
--watchlist                 comma separated list watchlist                               array   Watch listed envvars for changes and render template(s) on change
-R, --run                   string               run                                     array   Run command after rendering templates
--splay                     int                  splay                                   integer Random delay between 1 and X seconds between watchlist polls
--initial-run                                    render templates before starting watch
=========================== ==================== ======================================= ======= ==============================================================================

Jinja2 filter support
---------------------
By default only the jinja2 `builtin filters <https://jinja.palletsprojects.com/en/2.10.x/templates/#list-of-builtin-filters>`_ are supported this can be extended by installing the `jinja2-ansible-filters <https://pypi.org/project/jinja2-ansible-filters/>`_ module.

Example
-------

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

   ~> export NGINX='json:
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

Environment variable examples
-----------------------------

Plain environment variable
~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

setting:

::

   MYENVVAR='plain environment variable'

will render envvar-example.j2 to:

::

   This is a plain environment variable

Tag file
~~~~~~~~

Example:

setting:

::

   MYFILEVAR=file:./file-example.txt

will render file-example.j2 to:

::

   This is a file example

Tag json
~~~~~~~~

Example:

setting:

::

   MYJSONVAR='json:{"key": "json-example"}'

will render json-example.j2 to:

::

   This is a json-example

Tag jsonfile
~~~~~~~~~~~~

Example:

setting:

::

   MYJSONFILEVAR='jsonfile:jsonfile-example.json'

will render jsonfile-example.j2 to:

::

   This is a jsonfile example with subkey

Tag base64
~~~~~~~~~~

Example:

Setting:

::

   export MYBASE64VAR='base64:YmFzZTY0IGV4YW1wbGU='

will render base64-example.j2 to:

::

   This is a base64 example

Tag consul
~~~~~~~~~~

Configuration:

You can configure the consul tag by setting the CONSUL_CONFIG
environment variable. The following config items are supported:

============ =============================== =====================
Item         Explanation                     Default
============ =============================== =====================
url          consul url                      http://127.0.0.1:8500
scheme       consul url scheme http or https scheme from url
host         consul host                     hostname from url
port         consul http(s) port             port from url
token        consul token                    none
============ =============================== =====================

Global config example:

::

   read -d '' CONSUL_CONFIG << EOF
   {
      "url": "https://consul.foobar.tld",
      "token": "abcdef01-0123-abcd-1234-0123456789ab"
   }
   EOF

The ACL token can be configured by either the above configuration or by setting the CONSUL_TOKEN variable.

As an alternative for the global configuration it is also possible to configure / adjust the global configuration for each consul tag, by simply include the configuration when using the consul tag.

CONSUL_TOKEN and config key token can either contain the actual token or point to a file containing the token, use the **file:** tag to point to a file.

Tag config examples:

::

    export MYCONSULVAR='consul:config={"url": "https://consul2.foobar.tld", "token": "012345678-0123-abcd-1234-0123456789ab"}:consulvar"

::

    export MYCONSULVAR='consul:config={"url": "https://consul2.foobar.tld", "token": "file:/path/to/token"}:consulvar"

Consul example:

Setting:

key: consulvar in consul to value: consul example

and

::

   export MYCONSULVAR='consul:consulvar'

will render consul-example.j2 to:

::

   This is a consul example

Tag list
~~~~~~~~

Example:

Setting:

::

   export MYLIST='list:"first","second","third","fourth"'

will render list-example.j2 to:

::

   "first"
   "second"
   "third"
   "fourth"

Two pass rendering
~~~~~~~~~~~~~~~~~~

Starting from version 0.1.12 e2j2 supports embedding jinja2 macros in
environment variables.

Example:

Setting the following two environment variables:

::

    export WORDPRESS='json:{"database": {"name": "mydb", "user": "mydb_user", "password": "{{ DBSECRET }}", "host": "localhost"}}'
    export DBSECRET='file:./twopass-secret'

will render (by running: ``e2j2 -f twopass-example.j2 -2``) to:

::

   // ** MySQL settings - You can get this info from your web host ** //
   /** The name of the database for WordPress */
   define( 'DB_NAME', 'mydb' );

   /** MySQL database username */
   define( 'DB_USER', 'mydb_user' );

   /** MySQL database password */
   define( 'DB_PASSWORD', 'Db$ecr3t' );

   /** MySQL hostname */
   define( 'DB_HOST', 'localhost' );

In version 0.5.0 support was introduced for nested tag variables, so the above listed example can be simplified.
The DBSECRET variable is no longer needed, if the WORDPRESS variable is changed to:

::

    export WORDPRESS='json:{"database": {"name": "mydb", "user": "mydb_user", "password": "file:./twopass-secret", "host": "localhost"}}'

If needed you can escape e2j2 tags by using the escape tag

Tag vault
~~~~~~~~~

Configuration:

You can configure the vault tag by setting the VAULT_CONFIG
environment variable. The following config items are supported:

============ ============================== =====================
Item         Explanation                    Default
============ ============================== =====================
url          vault url                      http://127.0.0.1:8200
scheme       vault url scheme http or https scheme from url
host         vault host                     hostname from url
port         vault http(s) port             port from url
backend      vault secret backend           raw
token        vault token                    none
============ ============================== =====================

the following backends are supported:

======= =========================================
backend Description
======= =========================================
raw     use plain GET request to secret store API
kv1     key/value version 1
kv2     key/value version 2
======= =========================================

Global config example:

::

   read -d '' VAULT_CONFIG << EOF
    {
      "url": "https://vault.foobar.tld:8200",
      "token": "s.xxxxxxxxxxxxxxxxxxxxxxx",
      "backend: "kv2"
    }
   EOF

The Authentication token can be configured by either the above configuration or by setting the VAULT_TOKEN variable.

As an alternative for the global configuration it is also possible to configure / adjust the global configuration for each vault tag, by simply include the configuration when using the vault tag.

VAULT_TOKEN and config key token can either contain the actual token or point to a file containing the token, use the **file:** tag to point to a file.

Tag config example:

::

    export MYVAULTVAR='vault:config={"backend": "kv2", "token": "s.xxxxxxxxx"}:kv/my-secret"

::

    export MYVAULTVAR='vault:config={"backend": "kv2", "token": "file:/path/to/token"}:kv/my-secret"

Vault example:

Setting:

::

   vault kv put secret/my-secret secret=topsecret
   export MYVAULTVAR='vault:secret/my-secret'

will render vault-kv1-example.j2 (by running: ``e2j2 -f vault-example.j2``) to:

::

   ** topsecret **
   This is a vault example

Tag dns
~~~~~~~~~

Configuration:

You can configure the dns tag by setting the DNS_CONFIG
environment variable. The following config items are supported:

============ ============================== =====================
Item         Explanation                    Default
============ ============================== =====================
nameservers  overwrite nameservers          use system resolvers
port         overwrite dns port             53
type         record type (A, AAAA or SRV)   A
============ ============================== =====================

the supported record types will return a dict with the following keys:

======= ===============================
Type    Keys
======= ===============================
A       address
AAAA    address
SRV     target, port, weight, priority
======= ===============================

DNS example:

Assuming a consul node running on localhost with the default dns port 8600.

Setting the DNS_CONFIG variable:
::

   read -d '' DNS_CONFIG << EOF
    {
      "nameservers": ['127.0.0.1'],
      "port": 8600,
      "type": "SRV"
    }
   EOF

Setting:

::

   export MYDNSVAR='dns:consul.service.consul'

will render dns-example.j2 (by running: ``e2j2 -f dns-example.j2``) to:

::

    My consul node:
    node1.node.dc1.consul. listening on port 8300


.. |Build Status| image:: https://travis-ci.org/provonet/e2j2.svg?branch=master
   :target: https://travis-ci.org/provonet/e2j2
.. |Coverage Status| image:: https://coveralls.io/repos/github/provonet/e2j2/badge.svg
   :target: https://coveralls.io/github/provonet/e2j2
