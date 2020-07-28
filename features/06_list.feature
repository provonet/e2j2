Feature: handling environment variables containing the list tag

  Scenario: render template
    Given an installed e2j2 module
    When I set the environment MYLISTVAR variable to list:first,second,third,fourth
    And I create a template /tmp/list-example.j2 with the following content
      """
      {% for entry in MYLISTVAR %}-{{ entry }}-{% endfor %}
      """
    And I render the template with e2j2
    Then rendered content is as follows
      """
      -first--second--third--fourth-
      """
