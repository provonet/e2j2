Feature: handling environment variables containing the json tag

  Scenario: render template
    Given an installed e2j2 module
    When I set the environment MYJSONVAR variable to json:{"key": "json example"}
    And I create a template /tmp/json-example.j2 with the following content
      """
      This is a {{ MYJSONVAR.key }}
      """
    And I render the template with e2j2
    Then rendered content is as follows
      """
      This is a json example
      """

  Scenario: render template and flatten dict
    Given an installed e2j2 module
    When I set the environment MYJSONVAR variable to json:config={"flatten": true}:{"my_key": "flattened json example"}
    And I create a template /tmp/json-example.j2 with the following content
      """
      This is a {{ my_key }}
      """
    And I render the template with e2j2
    Then rendered content is as follows
      """
      This is a flattened json example
      """
