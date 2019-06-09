Feature: handling standard environment variables

  Scenario: render template
    Given an installed e2j2 module
    When I set the environment MYENVVAR variable to plain environment variable
    And I create a template /tmp/plain.j2 with the following content
      """
      This is a {{ MYENVVAR }}
      """
    And I render the template with e2j2
    Then the content of the is as follows
      """
      This is a plain environment variable
      """
