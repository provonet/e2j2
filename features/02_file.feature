Feature: handling environment variables containing the file tag

  Scenario: render template
    Given an installed e2j2 module
    When I set the environment MYFILEVAR variable to file:/tmp/file-example.txt
    And I create a file /tmp/file-example.txt with the following content
      """
      file example
      """
    And I create a template /tmp/file-example.j2 with the following content
      """
      This is a {{ MYFILEVAR }}
      """
    And I render the template with e2j2
    Then rendered content is as follows
      """
      This is a file example
      """
