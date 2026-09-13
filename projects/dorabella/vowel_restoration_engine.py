"""Vowel Restoration & Shorthand Skeleton Decoder.

Models 19th-century British stenography (Taylor / Pitman / Gurney):
1. Semicircular glyphs encode consonant skeletons.
2. Vowels (A, E, I, O, U) and silent letters are omitted in fast cursive drafting.
3. Physical dot (Line 3, char 5) marks an explicit vocalic indicator.
4. Uses dynamic programming / beam search over English lexicon to find maximum
   likelihood vowel-expanded sentences from candidate consonant streams.
"""

from __future__ import annotations

import heapq
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from cipher_lab.stats import QuadgramScorer

# Consonant skeleton extraction helper
VOWELS = set("AEIOU")


def to_skeleton(word: str) -> str:
    """Extract consonant skeleton from an uppercase word."""
    return "".join(c for c in word.upper() if c.isalpha() and c not in VOWELS)


class ShorthandVowelRestorer:
    """Restores full words and sentences from consonant skeleton sequences."""

    def __init__(self, scorer: Optional[QuadgramScorer] = None) -> None:
        self.scorer = scorer or QuadgramScorer(language="english")
        self.skeleton_to_words: Dict[str, List[str]] = {}
        self.word_freqs: Dict[str, float] = {}
        self._load_lexicon()

    def _load_lexicon(self) -> None:
        """Load dictionary and index by consonant skeleton."""
        dict_path = Path("/usr/share/dict/words")
        if not dict_path.exists():
            return

        with open(dict_path) as f:
            for line in f:
                w = line.strip().upper()
                if not w.isalpha() or len(w) < 2 or len(w) > 12:
                    continue
                skel = to_skeleton(w)
                if not skel:
                    continue
                if skel not in self.skeleton_to_words:
                    self.skeleton_to_words[skel] = []
                self.skeleton_to_words[skel].append(w)

        # Add Elgarian domain terms explicitly
        elgar_terms = [
            "DORABELLA", "ELGAR", "EDWARD", "MALVERN", "WOLVERHAMPTON",
            "PENNY", "ENIGMA", "VARIATION", "POWICK", "FORLI", "SEVERN",
            "AMDG", "LDS", "BCOS", "ALLITE", "XCUSE", "WOT", "BRAUT", "NIMROD",
            "VIOLIN", "ORGAN", "LISZT", "CHORAL", "PRELUDE", "PASTORAL",
        ]
        for w in elgar_terms:
            skel = to_skeleton(w)
            if skel not in self.skeleton_to_words:
                self.skeleton_to_words[skel] = []
            if w not in self.skeleton_to_words[skel]:
                self.skeleton_to_words[skel].insert(0, w)

    def restore_sentence_beam_search(
        self,
        consonant_stream: str,
        beam_width: int = 25,
        max_skel_len: int = 5,
    ) -> List[Tuple[float, str]]:
        """Find optimal word sequence from continuous consonant stream using beam search."""
        clean_stream = "".join(c for c in consonant_stream.upper() if c.isalpha() and c not in VOWELS)
        n = len(clean_stream)
        if n == 0:
            return []

        # Beam state: (score, idx, list_of_words)
        # We use a min-heap for pruning, but want to maximize score
        beam = [(0.0, 0, [])]

        for step in range(n):
            new_candidates = []
            seen = set()

            for score, idx, words in beam:
                if idx >= n:
                    # Already consumed stream
                    new_candidates.append((score, idx, words))
                    continue

                # Try word skeleton lengths from 1 to max_skel_len
                for l in range(1, min(max_skel_len + 1, n - idx + 1)):
                    sub_skel = clean_stream[idx : idx + l]
                    matches = self.skeleton_to_words.get(sub_skel, [])
                    for w in matches[:6]:  # top 6 words per skeleton
                        cand_words = words + [w]
                        cand_text = "".join(cand_words)
                        # Incremental quadgram log-likelihood
                        cand_score = self.scorer.score_total(cand_text)

                        state_key = (idx + l, " ".join(cand_words[-2:]))
                        if state_key in seen:
                            continue
                        seen.add(state_key)
                        new_candidates.append((cand_score, idx + l, cand_words))

            # Prune beam
            new_candidates.sort(key=lambda x: x[0], reverse=True)
            beam = new_candidates[:beam_width]

        # Return results that consumed all consonants
        completed = [
            (score, " ".join(words))
            for score, idx, words in beam
            if idx == n
        ]
        completed.sort(key=lambda x: x[0], reverse=True)
        return completed
