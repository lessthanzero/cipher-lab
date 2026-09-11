from projects.dorabella.corpus import get_dorabella_unicity
from projects.shugborough.corpus import get_shugborough_unicity


def test_shugborough_underdetermined():
    check = get_shugborough_unicity()
    assert check.payload_length == 8
    assert check.is_underdetermined is True
    assert "underdetermined" in check.warning.lower()

def test_dorabella_homophonic_gate():
    # If Dorabella is homophonic, it should fail unicity check
    check_homophonic = get_dorabella_unicity(key_type="homophonic")
    assert check_homophonic.is_underdetermined is True
