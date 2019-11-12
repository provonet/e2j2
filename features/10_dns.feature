Feature: handling environment variables containing the dns tag

  Scenario: render template
    Given an installed e2j2 module
    When I set the environment MYDNSVAR variable to dns:ns1.github.com
    And I create a template /tmp/dns-example.j2 with the following content
      """
      ns1.github.com has ip: {% for entry in MYDNSVAR %}{{ entry.address }}{% endfor %}
      """
    And I render the template with e2j2
    Then the content of the is as follows
      """
      ns1.github.com has ip: 192.0.2.1
      """
