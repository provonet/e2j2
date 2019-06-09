Feature: handling environment variables containing the jsonfile tag

  Scenario: render template
    Given an installed e2j2 module
    When I set the environment MYJSONFILEVAR variable to jsonfile:/tmp/jsonfile-example.json
    And I create a file /tmp/jsonfile-example.json with the following content
      """
      {
        "key": {
          "subkey": "jsonfile example with subkey"
        }
      }
      """
    And I create a template /tmp/jsonfile-example.j2 with the following content
      """
      This is a {{ MYJSONFILEVAR.key.subkey }}
      """
    And I render the template with e2j2
    Then the content of the is as follows
      """
      This is a jsonfile example with subkey
      """
