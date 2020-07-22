Feature: handling environment variables containing the vault tag

#  @fixture.with.vault
#  Scenario: render template
#    Given an installed e2j2 module
#    And I POST '{"data": {"secret": "topsecret"}}' to 'http://127.0.0.1:8200/v1/secret/data/foobar' with headers '{"X-Vault-Token": "aabbccddeeff"}'
#    When I set the environment MYVAULTVAR variable to vault:config={"url": "http://127.0.0.1:8200", "backend": "kv2", "token": "aabbccddeeff"}:secret/foobar
#    And I create a template /tmp/vault-example.j2 with the following content
#      """
#      the foobar secret: {{ MYVAULTVAR.secret }}
#      """
#    And I render the template with e2j2
#    Then rendered content is as follows
#      """
#      the foobar secret: topsecret
#      """
