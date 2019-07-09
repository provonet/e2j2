Feature: handling included template

  Scenario: render template
    Given an installed e2j2 module
    When I set the environment MYENVVAR variable to included stuff
    And I create a template /tmp/include-me.j2 with the following content
      """
      {{ MYENVVAR }}
      """
    And I create a template /tmp/include.j2 with the following content
      """
      {% include "/tmp/include-me.j2" %}
      """
    And I render the template with e2j2
    Then the content of the is as follows
      """
      included stuff
      """
