"""Classical cryptanalysis solvers and permutation search engines."""

from __future__ import annotations

import math
import random
import string
from collections.abc import Callable, Sequence


class PolybiusCheckerboard:
    """5x5 or 6x6 Polybius checkerboard encoder/decoder."""

    def __init__(self, key_alphabet: str = "ABCDEFGHIKLMNOPQRSTUVWXYZ", size: int = 5) -> None:
        self.size = size
        self.alphabet = key_alphabet.upper()
        if len(self.alphabet) != size * size:
            raise ValueError(f"Alphabet length ({len(self.alphabet)}) must equal {size * size}")
        
        self.char_to_coord = {}
        self.coord_to_char = {}
        for idx, ch in enumerate(self.alphabet):
            r = (idx // size) + 1
            c = (idx % size) + 1
            self.char_to_coord[ch] = (r, c)
            self.coord_to_char[(r, c)] = ch

    def decode_pairs(self, digit_pairs: Sequence[tuple[int, int]]) -> str:
        """Convert a sequence of (row, col) coordinates to characters."""
        res = []
        for r, c in digit_pairs:
            res.append(self.coord_to_char.get((r, c), "?"))
        return "".join(res)

    def encode_text(self, text: str) -> list[tuple[int, int]]:
        """Convert text characters to (row, col) coordinates."""
        clean = text.upper().replace("J", "I")
        res = []
        for ch in clean:
            if ch in self.char_to_coord:
                res.append(self.char_to_coord[ch])
        return res


class ColumnarTransposition:
    """Columnar transposition cipher decoder and permutation solver."""

    @staticmethod
    def decrypt(ciphertext: str, key_order: Sequence[int]) -> str:
        """Decrypt text using columnar transposition key order (0-indexed permutation)."""
        num_cols = len(key_order)
        if num_cols == 0 or len(ciphertext) == 0:
            return ciphertext
        
        num_rows = math.ceil(len(ciphertext) / num_cols)
        num_short_cols = (num_cols * num_rows) - len(ciphertext)
        cutoff_col = num_cols - num_short_cols
        
        # Calculate lengths of each column in reading order
        col_lens = [num_rows if c < cutoff_col else num_rows - 1 for c in range(num_cols)]
        
        # Slice ciphertext into columns according to key_order
        cols: dict[int, list[str]] = {}
        curr_idx = 0
        for k in key_order:
            length = col_lens[k]
            cols[k] = list(ciphertext[curr_idx : curr_idx + length])
            curr_idx += length
        
        # Read out row by row
        plaintext = []
        for r in range(num_rows):
            for c in range(num_cols):
                if r < len(cols[c]):
                    plaintext.append(cols[c][r])
        return "".join(plaintext)


class SimulatedAnnealingSolver:
    """General simulated annealing optimizer for key permutations."""

    def __init__(
        self,
        fitness_fn: Callable[[str], float],
        temp_start: float = 10.0,
        temp_end: float = 0.01,
        cooling_rate: float = 0.995,
        steps_per_temp: int = 50,
        seed: int = 42,
    ) -> None:
        self.fitness_fn = fitness_fn
        self.t_start = temp_start
        self.t_end = temp_end
        self.cooling = cooling_rate
        self.steps_per_temp = steps_per_temp
        self.rng = random.Random(seed)

    def solve_monoalphabetic(
        self,
        ciphertext: str,
        initial_key: str | None = None,
    ) -> tuple[str, str, float]:
        """Solve monoalphabetic substitution on ciphertext using simulated annealing."""
        alphabet = list(string.ascii_uppercase)
        if initial_key:
            current_key = list(initial_key.upper())
        else:
            current_key = alphabet[:]
            self.rng.shuffle(current_key)
        
        def decrypt_with_key(key: list[str]) -> str:
            trans = str.maketrans("".join(key), string.ascii_uppercase)
            return ciphertext.upper().translate(trans)

        best_key = current_key[:]
        current_text = decrypt_with_key(current_key)
        best_score = self.fitness_fn(current_text)
        current_score = best_score
        
        t = self.t_start
        while t > self.t_end:
            for _ in range(self.steps_per_temp):
                # Propose neighbour: swap two letters in key
                i, j = self.rng.sample(range(len(current_key)), 2)
                candidate_key = current_key[:]
                candidate_key[i], candidate_key[j] = candidate_key[j], candidate_key[i]
                
                candidate_text = decrypt_with_key(candidate_key)
                candidate_score = self.fitness_fn(candidate_text)
                
                delta = candidate_score - current_score
                if delta > 0 or math.exp(delta / max(t, 1e-6)) > self.rng.random():
                    current_key = candidate_key
                    current_score = candidate_score
                    if candidate_score > best_score:
                        best_score = candidate_score
                        best_key = candidate_key[:]
            t *= self.cooling
            
        final_pt = decrypt_with_key(best_key)
        return "".join(best_key), final_pt, best_score
