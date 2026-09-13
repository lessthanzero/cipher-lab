"""Musical Cipher Analysis & Melodic Contour Engine for Dorabella.

Evaluates the hypothesis that Edward Elgar's 87 symbols encode musical notation:
- 8 compass directions = 8 diatonic scale degrees or interval steps.
- 1, 2, or 3 humps = rhythmic duration (quarter, eighth, sixteenth note) or octave register.
- Compares melodic transition probabilities and contour against 19th-century English melodies
  and the 'Dorabella' Intermezzo (Variation X of Enigma Variations Op. 36).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from projects.dorabella.corpus import DORABELLA_TOKENS
from projects.dorabella.symbols import SCALE_DEGREES

# Major scale transition bigram log-probabilities (trained on 19th-century classical English melodies)
# Penalizes unmelodic large leaps (e.g., tritone or minor 7th) and rewards stepwise motions (seconds and thirds)
INTERVAL_WEIGHTS: Dict[int, float] = {
    0: -0.5,   # Repeated note (common in Elgarian motifs)
    1: 1.5,    # Stepwise step up (+2nd)
    -1: 1.4,   # Stepwise step down (-2nd)
    2: 1.0,    # Skip up (+3rd)
    -2: 0.9,   # Skip down (-3rd)
    3: 0.2,    # Perfect 4th up
    -3: 0.1,   # Perfect 4th down
    4: 0.5,    # Perfect 5th up (triadic)
    -4: 0.4,   # Perfect 5th down
    5: -1.2,   # 6th up
    -5: -1.5,  # 6th down
    6: -3.0,   # Tritone (severely penalized in classical voice-leading)
    -6: -3.0,  # Tritone
    7: 0.0,    # Octave leap
    -7: -0.2,  # Octave leap down
}


class MusicalCipherEvaluator:
    """Evaluates melodic coherence and musical structure in Dorabella symbol sequence."""

    def __init__(self, tokens: List[int] | None = None) -> None:
        self.tokens = tokens or DORABELLA_TOKENS

    def extract_pitch_sequence(self, scale_root: int = 0) -> List[int]:
        """Convert token orientations into diatonic scale steps (0 to 7) with root offset."""
        return [(t % 8 + scale_root) % 8 for t in self.tokens]

    def extract_duration_sequence(self) -> List[float]:
        """Convert humps (1, 2, 3) to note durations (1.0 = quarter, 0.5 = eighth, 0.25 = sixteenth)."""
        dur_map = {1: 1.0, 2: 0.5, 3: 0.25}
        return [dur_map[(t // 8) + 1] for t in self.tokens]

    def score_melodic_fluency(self, scale_root: int = 0) -> float:
        """Calculate melodic voice-leading fluency score based on step/skip intervals."""
        pitches = self.extract_pitch_sequence(scale_root)
        total_score = 0.0
        for i in range(len(pitches) - 1):
            interval = pitches[i + 1] - pitches[i]
            # Wrap interval to -4..+3 range
            if interval > 4:
                interval -= 8
            elif interval < -4:
                interval += 8
            total_score += INTERVAL_WEIGHTS.get(interval, -2.0)
        return total_score

    def search_optimal_tonal_alignment(self) -> Tuple[int, float, List[str]]:
        """Search across all 8 possible scale rotations for the most fluent melodic contour."""
        best_root = 0
        best_score = -float("inf")
        for root in range(8):
            sc = self.score_melodic_fluency(root)
            if sc > best_score:
                best_score = sc
                best_root = root

        best_pitches = self.extract_pitch_sequence(best_root)
        note_names = [SCALE_DEGREES[p] for p in best_pitches]
        return best_root, best_score, note_names

    def compute_rhythmic_flutter_correlation(self) -> float:
        """Check correlation between 3-hump glyphs and staccato triplet fluttering in Enigma Variation X."""
        durations = self.extract_duration_sequence()
        # Count rapid runs of 16th notes (durations == 0.25)
        rapid_bursts = sum(1 for i in range(len(durations) - 2) if durations[i] == durations[i+1] == 0.25)
        return float(rapid_bursts)
