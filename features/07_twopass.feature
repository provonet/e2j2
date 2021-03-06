Feature: handling environment variables containing the json tag and the twopass flag set

  Scenario: render nested template
    Given an installed e2j2 module
    When I set the environment WORDPRESS variable to json:{"database": {"name": "mydb", "user": "mydb_user", "password": "{{ DBSECRET }}", "host": "localhost"}}
    And I set the environment DBSECRET variable to file:/tmp/twopass-secret.txt
    And I create a file /tmp/twopass-secret.txt with the following content
      """
      top-secret
      """
    And I create a template /tmp/twopass-example.j2 with the following content
      """
        // ** MySQL settings - You can get this info from your web host ** //
        /** The name of the database for WordPress */
        define( 'DB_NAME', '{{ WORDPRESS.database.name }}' );

        /** MySQL database username */
        define( 'DB_USER', '{{ WORDPRESS.database.user }}' );

        /** MySQL database password */
        define( 'DB_PASSWORD', '{{ WORDPRESS.database.password }}' );

        /** MySQL hostname */
        define( 'DB_HOST', '{{ WORDPRESS.database.host }}' );
      """
    And I render the template with e2j2 with additional flag --twopass
    Then rendered content is as follows
      """
        // ** MySQL settings - You can get this info from your web host ** //
        /** The name of the database for WordPress */
        define( 'DB_NAME', 'mydb' );

        /** MySQL database username */
        define( 'DB_USER', 'mydb_user' );

        /** MySQL database password */
        define( 'DB_PASSWORD', 'top-secret' );

        /** MySQL hostname */
        define( 'DB_HOST', 'localhost' );
      """

  Scenario: render template with nested var
    Given an installed e2j2 module
    When I set the environment WORDPRESS variable to json:{"database": {"name": "mydb", "user": "mydb_user", "password": "file:/tmp/twopass-secret.txt", "host": "localhost"}}
    And I create a file /tmp/twopass-secret.txt with the following content
      """
      top-secret2
      """
    And I create a template /tmp/twopass-example.j2 with the following content
      """
        // ** MySQL settings - You can get this info from your web host ** //
        /** The name of the database for WordPress */
        define( 'DB_NAME', '{{ WORDPRESS.database.name }}' );

        /** MySQL database username */
        define( 'DB_USER', '{{ WORDPRESS.database.user }}' );

        /** MySQL database password */
        define( 'DB_PASSWORD', '{{ WORDPRESS.database.password }}' );

        /** MySQL hostname */
        define( 'DB_HOST', '{{ WORDPRESS.database.host }}' );
      """
    And I render the template with e2j2 with additional flag --twopass --nested-tags
    Then rendered content is as follows
      """
        // ** MySQL settings - You can get this info from your web host ** //
        /** The name of the database for WordPress */
        define( 'DB_NAME', 'mydb' );

        /** MySQL database username */
        define( 'DB_USER', 'mydb_user' );

        /** MySQL database password */
        define( 'DB_PASSWORD', 'top-secret2' );

        /** MySQL hostname */
        define( 'DB_HOST', 'localhost' );
      """

  Scenario: render template with escaped tag
    Given an installed e2j2 module
    When I set the environment ESCAPED_TAG variable to json:{"path": "escape:file:/foobar.txt"}
    And I create a template /tmp/twopass-with-escape.j2 with the following content
      """
      {{ ESCAPED_TAG.path }}
      """
    And I render the template with e2j2 with additional flag --twopass --nested-tags
    Then rendered content is as follows
      """
      file:/foobar.txt
      """
