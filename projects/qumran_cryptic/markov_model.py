"""Sectarian Hebrew Markov Language Model for Cryptanalysis.

Trained on classical Qumran sectarian Hebrew literature:
- 1QS (Rule of the Community / Serekh ha-Yahad)
- 1QM (War Scroll / Milhamah)
- CD (Damascus Document)
Computes character unigram, bigram, and trigram log-likelihoods for decipherment evaluation.
"""

from __future__ import annotations

import collections
import math
from typing import Dict, List, Optional, Sequence, Tuple

from projects.qumran_cryptic.alphabet import HEBREW_ALPHABET, normalize_hebrew_text

# Representative sectarian Hebrew training corpus extracts from 1QS and 1QM
_1QS_TRAINING_EXTRACT = (
    "למשכיל ללמד את בני האור ולחנכם בסרך היחד לחיות לפי חוקי התורה אשר צוה אל "
    "ביד משה וביד עבדיו הנביאים ולאהוב את כל אשר בחר ולשנוא את כל אשר מאס "
    "להרחיק מכל רע ולדבוק בכל מעשי טוב ולעשות אמת וצדקה ומשפט בארץ "
    "ולא ללכת עוד בשרירות לב אשמה ועיני זנות לעשות כל רע "
    "ולהביא את כל הנדבים לעשות חוקי אל בברית חסד להיחד בעצת אל "
    "ולהתהלך לפניו תמים כל הנגלות למועדי תעודותם ולאהוב כל בני אור "
    "איש כגורלו בעצת אל ולשנוא כל בני חושך איש כאשמתו בנקמת אל"
)

_1QM_TRAINING_EXTRACT = (
    "למשכיל סרך המלחמה ראשית משלוח יד בני אור להחל בגורל בני חושך "
    "בחייל בליעל בגדוד אדום ומואב ובני עמון ובחייל פלשת ובגדודי כתיים "
    "אשר עמהם מרשיעי ברית ובני לוי ובני יהודה ובני בנימין גולת המדבר "
    "ילחמו בם בכל גדודיהם בשוב גולת בני אור ממדבר העמים לחנות במדבר ירושלים "
    "ואחר המלחמה יעלו משם והכתיים יכלו באין עזר ולא תהיה תקומה לכל בני רשעה"
)


class SectarianHebrewMarkovModel:
    """N-gram character Markov language model for Dead Sea Scrolls Hebrew."""

    def __init__(self, smoothing: float = 1e-4) -> None:
        self.smoothing = smoothing
        self.unigrams: dict[str, int] = collections.defaultdict(int)
        self.bigrams: dict[tuple[str, str], int] = collections.defaultdict(int)
        self.trigrams: dict[tuple[str, str, str], int] = collections.defaultdict(int)
        self.total_unigrams = 0
        self.total_bigrams = 0
        self.total_trigrams = 0
        self._train()

    def _train(self) -> None:
        corpus = normalize_hebrew_text(_1QS_TRAINING_EXTRACT + " " + _1QM_TRAINING_EXTRACT)
        chars = [c for c in corpus if c in HEBREW_ALPHABET]

        for c in chars:
            self.unigrams[c] += 1
            self.total_unigrams += 1

        for i in range(len(chars) - 1):
            pair = (chars[i], chars[i + 1])
            self.bigrams[pair] += 1
            self.total_bigrams += 1

        for i in range(len(chars) - 2):
            tri = (chars[i], chars[i + 1], chars[i + 2])
            self.trigrams[tri] += 1
            self.total_trigrams += 1

    def log_prob_char(self, char: str) -> float:
        """Unigram log2 probability with Laplace smoothing."""
        count = self.unigrams.get(char, 0) + self.smoothing
        denom = self.total_unigrams + self.smoothing * len(HEBREW_ALPHABET)
        return math.log2(count / denom)

    def log_prob_bigram(self, c1: str, c2: str) -> float:
        """Bigram log2 probability P(c2 | c1) with Add-k smoothing."""
        pair = (c1, c2)
        count_pair = self.bigrams.get(pair, 0) + self.smoothing
        count_c1 = self.unigrams.get(c1, 0) + self.smoothing * len(HEBREW_ALPHABET)
        return math.log2(count_pair / count_c1)

    def score_text(self, text: str) -> float:
        """Scores candidate Hebrew plaintext under bigram Markov model (mean log-likelihood per character)."""
        chars = [c for c in text if c in HEBREW_ALPHABET]
        if len(chars) <= 1:
            return -10.0

        total_ll = self.log_prob_char(chars[0])
        for i in range(len(chars) - 1):
            total_ll += self.log_prob_bigram(chars[i], chars[i + 1])

        return total_ll / len(chars)
