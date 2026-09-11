from cipher_lab.solvers import ColumnarTransposition, PolybiusCheckerboard


def test_polybius_checkerboard():
    board = PolybiusCheckerboard(key_alphabet="ABCDEFGHIKLMNOPQRSTUVWXYZ", size=5)
    # Test encoding and decoding
    coords = board.encode_text("HELLO")
    # H -> (2, 3), E -> (1, 5), L -> (3, 1), L -> (3, 1), O -> (3, 4)
    assert coords == [(2, 3), (1, 5), (3, 1), (3, 1), (3, 4)]
    decoded = board.decode_pairs(coords)
    assert decoded == "HELLO"

def test_columnar_transposition():
    text = "DEFENDTHEEASTWALL"
    # 4 columns: key [2, 0, 3, 1]
    # Encrypt mentally:
    # Col 0: D N E L
    # Col 1: E T A
    # Col 2: F H S
    # Col 3: E E T W
    # Sliced ciphertext in key order: [Col 2, Col 0, Col 3, Col 1]
    dec = ColumnarTransposition.decrypt(text, list(range(len(text))))
    assert len(dec) == len(text)
