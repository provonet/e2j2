import pytest
from mock import patch
from e2j2.templates import render
from e2j2.exceptions import E2j2Exception


@patch('builtins.open')
def test_render_template_one_pass(file_mocker, config):
    config['twopass'] = False
    file_mocker.return_value.__enter__.return_value.read.return_value = "The value of FOO={{FOO}}"
    assert render(config=config, j2file='/foo/file1.j2', j2vars={"FOO": "BAR"}) == "The value of FOO=BAR"
    file_mocker.assert_called_with('/foo/file1.j2', 'r')


@patch('builtins.open')
def test_render_template_two_passes(file_mocker, config):
    config['twopass'] = True
    file_mocker.return_value.__enter__.return_value.read.return_value = "The value of FOO={{FOO}}"
    assert render(config=config, j2file='/foo/file1.j2', j2vars={"FOO": "{{BAR}}", "BAR": "bar"}) == "The value of FOO=bar"


@patch('builtins.open')
def test_render_template_file_not_found(file_mocker, config):
    file_mocker.side_effect = FileNotFoundError('file1.j2')
    with pytest.raises(E2j2Exception) as err:
        render(config=config, j2file='/foo/file1.j2', j2vars={"FOO": "BAR"})

    assert "Template file1.j2 not found" in str(err)


@patch('builtins.open')
def test_render_template_undefined_variable(file_mocker, config):
    file_mocker.return_value.__enter__.return_value.read.return_value = "The value of FOO={{FOO}}"
    with pytest.raises(E2j2Exception) as err:
        render(config=config, j2file='/foo/file1.j2', j2vars={})

    assert "'FOO' is undefined" in str(err) and "at line: 1" in str(err)


@patch('builtins.open')
def test_render_template_syntax_error(file_mocker, config):
    file_mocker.return_value.__enter__.return_value.read.return_value = "{% if FOO %}FOO!{% endfi %}"
    with pytest.raises(E2j2Exception) as err:
        render(config=config, j2file='/foo/file1.j2', j2vars={})

    assert "unknown tag \'endfi\'" in str(err) and "at line: 1" in str(err)


@patch('builtins.open')
def test_render_template_other_exceptions(file_mocker, config):
    file_mocker.side_effect = IOError('An IO error')
    with pytest.raises(E2j2Exception) as err:
        render(config=config, j2file='/foo/file1.j2', j2vars={"FOO": "BAR"})

    assert "An IO error" in str(err)


