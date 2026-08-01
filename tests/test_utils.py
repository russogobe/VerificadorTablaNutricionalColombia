from core.utils import norm, parse_number


def test_norm():
    assert norm('áéíóú') == 'AEIOU'


def test_parse_number():
    assert parse_number('3.1') == 3.1
