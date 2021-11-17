from e2j2.templates import recursive_iter


def test_recursive_iter_flat():
    data = {'test_key', 'test_value'}
    assert list(recursive_iter(data)) == [((), {'test_key', 'test_value'})]


def test_recursive_iter_nested_dict():
    data = {'nestedkey': {'test_key', 'test_value'}}
    assert list(recursive_iter(data)) == [(('nestedkey',), {'test_key', 'test_value'})]


def test_recursive_iter_list_of_dict():
    data = {'listofdict': [{'test_key', 'test_value'}]}
    assert list(recursive_iter(data)) == [(('listofdict', 0), {'test_key', 'test_value'})]
