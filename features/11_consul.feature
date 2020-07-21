@fixture.with.consul
Feature: handling environment variables containing the consul tag

  Scenario: render template
    Given an installed e2j2 module
    And I PUT 'consul example' to 'http://127.0.0.1:8500/v1/kv/foobar' with headers '{"Content-type": "application/text"}'
    When I set the environment MYCONSULVAR variable to consul:config={"url": "http://127.0.0.1:8500"}:foobar
    And I create a template /tmp/consul-example.j2 with the following content
      """
      this is a {{ MYCONSULVAR }}
      """
    And I render the template with e2j2
    Then rendered content is as follows
      """
      this is a consul example
      """
