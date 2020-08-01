Feature: handling environment variables containing the json tag and alternative markers set

  Scenario: render template with alternative block marker
    Given an installed e2j2 module
    When I set the environment MYJSONVAR variable to json:{"key": "marker"}
    And I create a template /tmp/blockmarker-example.j2 with the following content
      """
      Lets check if the alternative block marker is set
      <% if MYJSONVAR.key == 'marker' -%>
      Yep
      <%- endif %>
      """
    And I render the template with e2j2 with additional flag --marker-set <=
    Then rendered content is as follows
      """
      Lets check if the alternative block marker is set
      Yep
      """
    And I render the template with e2j2 with additional flag --block_start <% --block_end %>
    Then rendered content is as follows
      """
      Lets check if the alternative block marker is set
      Yep
      """

  Scenario: render template with the alternative variable marker {=
    Given an installed e2j2 module
    When I set the environment MYJSONVAR variable to json:{"key": "json example"}
    And I create a template /tmp/variablemarker-example.j2 with the following content
      """
      This is a {= MYJSONVAR.key =} with alternative variable marker
      """
    And I render the template with e2j2 with additional flag --marker-set {=
    Then rendered content is as follows
      """
      This is a json example with alternative variable marker
      """

  Scenario: render template with the alternative variable marker <=
    Given an installed e2j2 module
    When I set the environment MYJSONVAR variable to json:{"key": "json example"}
    And I create a template /tmp/variablemarker-example.j2 with the following content
      """
      This is a <= MYJSONVAR.key => with alternative variable marker
      """
    And I render the template with e2j2 with additional flag --marker-set <=
    Then rendered content is as follows
      """
      This is a json example with alternative variable marker
      """

  Scenario: render template with the alternative variable marker [=
    Given an installed e2j2 module
    When I set the environment MYJSONVAR variable to json:{"key": "json example"}
    And I create a template /tmp/variablemarker-example.j2 with the following content
      """
      This is a [= MYJSONVAR.key =] with alternative variable marker
      """
    And I render the template with e2j2 with additional flag --marker-set [=
    Then rendered content is as follows
      """
      This is a json example with alternative variable marker
      """

  Scenario: render template with the alternative variable marker (=
    Given an installed e2j2 module
    When I set the environment MYJSONVAR variable to json:{"key": "json example"}
    And I create a template /tmp/variablemarker-example.j2 with the following content
      """
      This is a (= MYJSONVAR.key =) with alternative variable marker
      """
    And I render the template with e2j2 with additional flag --marker-set (=
    Then rendered content is as follows
      """
      This is a json example with alternative variable marker
      """

 Scenario: render template with alternative comment marker
    Given an installed e2j2 module
    When I set the environment MYJSONVAR variable to json:{"key": "json example"}
    And I create a template /tmp/commentmarker-example.j2 with the following content
      """
      [# lets try to render with an alternative comment marker set -#]
      This is a [= MYJSONVAR.key =] with alternative comment marker
      [#- THIS LINE SHOULD NOT BE RENDERED #]
      """
    And I render the template with e2j2 with additional flag --comment_start [# --comment_end #]
    Then rendered content is as follows
      """
      This is a [= MYJSONVAR.key =] with alternative comment marker
      """
    And I render the template with e2j2 with additional flag --marker-set [=
    Then rendered content is as follows
      """
      This is a json example with alternative comment marker
      """
