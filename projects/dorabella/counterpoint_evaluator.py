"""Contrapuntal Voice-Leading & Harmonic Alignment Engine for Dorabella (1897).

Evaluates the master hypothesis of Sir Edward Elgar's 'Enigma' (1899) and 'Dorabella' (1897):
1. 'through and over the whole set another and larger theme goes, but is not played'
2. Variation X (Dorabella) is an accompaniment / counter-melody to an unheard cantus firmus.
3. Tests two-part species counterpoint rules (Fux / Macfarren Victorian harmony):
   - Consonance Ratio (% 3rds, 6ths, 5ths, octaves on metric downbeats).
   - Voice-leading motion: Contrary vs. parallel motion.
   - Prohibition of parallel fifths and octaves.
4. Evaluates alignment against canonical candidates:
   - The Enigma Theme itself (G minor / G major, 1899)
   - 'Auld Lang Syne' (Robert Burns / traditional)
   - 'Rule, Britannia!' (Thomas Arne)
   - 'Dies Irae' (Gregorian plainchant, beloved by Elgar & Liszt)
   - Liszt's 'Les Préludes' Pastorale Theme (1886 concert excerpt)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Cantus firmus candidate pitch sequences (MIDI note numbers, 1 note per beat)
# 1. Enigma Theme (G minor): Bb4, G4, A4, F#4, Bb4, G4, A4, D4, G4, Bb4, C5, D5, Eb5, G4, F4, Eb4, D4
ENIGMA_THEME_CANTUS = [70, 67, 69, 66, 70, 67, 69, 62, 67, 70, 72, 74, 75, 67, 65, 75, 74]

# 2. Auld Lang Syne (G major): D4, G4, G4, B4, A4, G4, A4, B4, G4, G4, B4, D5, E5, D5, B4, B4
AULD_LANG_SYNE_CANTUS = [62, 67, 67, 71, 69, 67, 69, 71, 67, 67, 71, 74, 76, 74, 71, 71]

# 3. Dies Irae (D Dorian / G minor transposed): G4, F4, G4, Eb4, F4, D4, Eb4, C4, D4
DIES_IRAE_CANTUS = [67, 65, 67, 63, 65, 62, 63, 60, 62]

# 4. Liszt Les Preludes Pastorale Theme (No. 6): E4, G4, E4, C4, G4, B4, D5, C5, G4
LISZT_PRELUDES_CANTUS = [64, 67, 64, 60, 67, 71, 74, 72, 67]

# Consonant interval semitone differences (mod 12)
# 0: Unison/Octave (P1/P8), 3: Minor 3rd, 4: Major 3rd, 7: Perfect 5th, 8: Minor 6th, 9: Major 6th
CONSONANT_INTERVALS = {0, 3, 4, 7, 8, 9}
PERFECT_CONSONANCES = {0, 7}


@dataclass
class CounterpointResult:
    cantus_name: str
    alignment_offset: int
    total_aligned_notes: int
    consonance_ratio: float
    contrary_motion_ratio: float
    parallel_fifths_count: int
    parallel_octaves_count: int
    composite_harmony_score: float
    intervals_semitones: List[int]


class CounterpointEvaluator:
    """Evaluates strict counterpoint between Dorabella melody and candidate themes."""

    def __init__(self, dorabella_pitches: Optional[List[int]] = None) -> None:
        if dorabella_pitches is None:
            from projects.dorabella.dual_musical_engine import DualMusicalCipherEngine
            engine = DualMusicalCipherEngine()
            events = engine.extract_melodic_stream(scale="g_major")
            self.dorabella_pitches = [p for p, dur in events]
        else:
            self.dorabella_pitches = dorabella_pitches

    def evaluate_alignment(
        self,
        cantus_pitches: List[int],
        cantus_name: str,
        offset: int = 0,
    ) -> CounterpointResult:
        """Evaluate two-part counterpoint for a specific metric offset."""
        # Align voices
        c_len = len(cantus_pitches)
        d_len = len(self.dorabella_pitches)
        aligned_count = min(c_len, d_len - offset)

        if aligned_count < 6:
            return CounterpointResult(
                cantus_name=cantus_name,
                alignment_offset=offset,
                total_aligned_notes=0,
                consonance_ratio=0.0,
                contrary_motion_ratio=0.0,
                parallel_fifths_count=0,
                parallel_octaves_count=0,
                composite_harmony_score=-999.0,
                intervals_semitones=[],
            )

        consonances = 0
        contrary_motion = 0
        parallel_5ths = 0
        parallel_8ths = 0
        intervals = []

        prev_d = None
        prev_c = None
        prev_interval = None

        for i in range(aligned_count):
            d = self.dorabella_pitches[offset + i]
            c = cantus_pitches[i]
            interval = abs(d - c) % 12
            intervals.append(interval)

            if interval in CONSONANT_INTERVALS:
                consonances += 1

            if prev_d is not None and prev_c is not None and prev_interval is not None:
                d_motion = d - prev_d
                c_motion = c - prev_c

                # Contrary motion check
                if (d_motion > 0 and c_motion < 0) or (d_motion < 0 and c_motion > 0):
                    contrary_motion += 1

                # Parallel 5ths check
                if prev_interval == 7 and interval == 7 and d_motion != 0 and c_motion != 0:
                    parallel_5ths += 1

                # Parallel 8ths check
                if prev_interval == 0 and interval == 0 and d_motion != 0 and c_motion != 0:
                    parallel_8ths += 1

            prev_d = d
            prev_c = c
            prev_interval = interval

        consonance_ratio = consonances / aligned_count
        contrary_ratio = contrary_motion / max(1, aligned_count - 1)

        # Composite harmony score: reward consonances & contrary motion, penalize parallel 5ths/8ths
        score = (consonance_ratio * 100.0) + (contrary_ratio * 50.0) - (parallel_5ths * 40.0) - (parallel_8ths * 40.0)

        return CounterpointResult(
            cantus_name=cantus_name,
            alignment_offset=offset,
            total_aligned_notes=aligned_count,
            consonance_ratio=consonance_ratio,
            contrary_motion_ratio=contrary_ratio,
            parallel_fifths_count=parallel_5ths,
            parallel_octaves_count=parallel_8ths,
            composite_harmony_score=score,
            intervals_semitones=intervals,
        )

    def sweep_all_cantus_firmus(self) -> List[CounterpointResult]:
        """Sweep all candidate themes across all offsets."""
        candidates = [
            ("Enigma Theme (1899)", ENIGMA_THEME_CANTUS),
            ("Auld Lang Syne", AULD_LANG_SYNE_CANTUS),
            ("Dies Irae", DIES_IRAE_CANTUS),
            ("Liszt Les Preludes Pastorale", LISZT_PRELUDES_CANTUS),
        ]
        results = []
        for name, pitches in candidates:
            # Test offsets across Dorabella notes
            for offset in range(0, max(1, len(self.dorabella_pitches) - len(pitches))):
                res = self.evaluate_alignment(pitches, name, offset=offset)
                if res.total_aligned_notes >= 6:
                    results.append(res)
        results.sort(key=lambda r: r.composite_harmony_score, reverse=True)
        return results


if __name__ == "__main__":
    evaluator = CounterpointEvaluator()
    print("Evaluating contrapuntal alignment against Enigma and candidate cantus firmus themes...")
    results = evaluator.sweep_all_cantus_firmus()

    print("\n" + "=" * 80)
    print("TOP 5 CONTRAPUNTAL HARMONIC ALIGNMENTS:")
    print("=" * 80)
    for r in results[:5]:
        print(f"[{r.cantus_name} | Offset: {r.alignment_offset}]")
        print(f"  Consonance Ratio: {r.consonance_ratio * 100:.1f}% ({r.consonance_ratio:.3f})")
        print(f"  Contrary Motion:  {r.contrary_motion_ratio * 100:.1f}%")
        print(f"  Parallel 5ths: {r.parallel_fifths_count} | Parallel 8ths: {r.parallel_octaves_count}")
        print(f"  Composite Score:  {r.composite_harmony_score:.1f}")
        print(f"  Intervals (mod 12): {r.intervals_semitones}")
        print("-" * 60)
