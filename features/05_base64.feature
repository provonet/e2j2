Feature: handling environment variables containing the base64 tag

  Scenario: render template
    Given an installed e2j2 module
    When I set the environment MYBASE64VAR variable to base64:YmFzZTY0IGV4YW1wbGU=
    And I create a template /tmp/base64-example.j2 with the following content
      """
      This is a {{ MYBASE64VAR }}
      """
    And I render the template with e2j2
    Then the content of the is as follows
      """
      This is a base64 example
      """
