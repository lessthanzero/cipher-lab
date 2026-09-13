"""Dual-Cipher Musical Melodic Engine & Pure-Python MIDI Synthesizer.

Evaluates the dual-cipher hypothesis:
1. Semicircle orientations (0..7) = diatonic pitch degrees (e.g., G major / E minor).
2. Humps (1, 2, 3) = note durations (quarter, eighth, sixteenth notes).
3. Synthesizes genuine playable Standard MIDI (.mid) files with zero external dependencies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from projects.dorabella.corpus import DORABELLA_TOKENS

# Diatonic scale mappings (MIDI pitch numbers)
# G major: G4=67, A4=69, B4=71, C5=72, D5=74, E5=76, F#5=78, G5=79
G_MAJOR_PITCHES: List[int] = [67, 69, 71, 72, 74, 76, 78, 79]

# E minor (Elgar's favorite key - Cello Concerto, Enigma Theme):
# E4=64, F#4=66, G4=67, A4=69, B4=71, C5=72, D5=74, E5=76
E_MINOR_PITCHES: List[int] = [64, 66, 67, 69, 71, 72, 74, 76]

# Note durations in ticks (480 ticks = quarter note / crotchet)
# 1 hump: crotchet (480 ticks)
# 2 humps: quaver (240 ticks)
# 3 humps: semiquaver (120 ticks - matches Dorabella stutter flutter)
TICKS_PER_HUMP: Dict[int, int] = {
    1: 480,
    2: 240,
    3: 120,
}


def _encode_vlq(value: int) -> bytes:
    """Encode an integer as a MIDI variable-length quantity."""
    buf = [value & 0x7F]
    value >>= 7
    while value > 0:
        buf.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(buf))


class DualMusicalCipherEngine:
    """Extracts melodies and synthesizes MIDI from Dorabella symbols."""

    def __init__(self, tokens: List[int] | None = None) -> None:
        self.tokens = tokens or DORABELLA_TOKENS

    def extract_melodic_stream(
        self,
        scale: str = "g_major",
        orientation_offset: int = 0,
    ) -> List[Tuple[int, int]]:
        """Return list of (midi_pitch, duration_ticks) for each token."""
        scale_pitches = G_MAJOR_PITCHES if scale == "g_major" else E_MINOR_PITCHES
        events = []
        for t in self.tokens:
            humps = (t // 8) + 1
            ori = (t % 8 + orientation_offset) % 8
            pitch = scale_pitches[ori]
            duration = TICKS_PER_HUMP[humps]
            events.append((pitch, duration))
        return events

    def generate_midi_file(
        self,
        output_path: Path,
        scale: str = "g_major",
        orientation_offset: int = 0,
        instrument_program: int = 68,  # 68 = Oboe (fluttering Dorabella theme) or 40 = Violin
        tempo_bpm: int = 108,          # Allegretto tempo of Variation X
    ) -> Path:
        """Synthesize a standard Type 0 MIDI file from the extracted melody."""
        melody = self.extract_melodic_stream(scale=scale, orientation_offset=orientation_offset)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Calculate microseconds per beat for tempo (60,000,000 / BPM)
        us_per_beat = int(60_000_000 / tempo_bpm)
        tempo_bytes = us_per_beat.to_bytes(3, "big")

        track_events = bytearray()

        # Event: Set Tempo
        track_events.extend(_encode_vlq(0))
        track_events.extend(b"\xFF\x51\x03" + tempo_bytes)

        # Event: Program Change (Instrument)
        track_events.extend(_encode_vlq(0))
        track_events.extend(bytes([0xC0, instrument_program]))

        # Notes
        velocity = 85
        for pitch, duration in melody:
            # Note On (delta 0)
            track_events.extend(_encode_vlq(0))
            track_events.extend(bytes([0x90, pitch, velocity]))

            # Note Off (delta = duration)
            track_events.extend(_encode_vlq(duration))
            track_events.extend(bytes([0x80, pitch, 0]))

        # End of Track
        track_events.extend(_encode_vlq(0))
        track_events.extend(b"\xFF\x2F\x00")

        # MIDI Header: 'MThd', length 6, format 0, 1 track, 480 ticks/beat
        header = b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x01\xE0"
        # Track Header: 'MTrk' + length of track events
        track_header = b"MTrk" + len(track_events).to_bytes(4, "big")

        with open(output_path, "wb") as f:
            f.write(header + track_header + track_events)

        return output_path

    def generate_wav_file(
        self,
        output_path: Path,
        scale: str = "g_major",
        orientation_offset: int = 0,
        sample_rate: int = 44100,
        tempo_bpm: int = 108,
        timbre: str = "woodwind",
    ) -> Path:
        """Synthesize a pristine 16-bit 44.1kHz mono WAV file from the extracted melody."""
        import math
        import struct
        import wave

        melody = self.extract_melodic_stream(scale=scale, orientation_offset=orientation_offset)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        samples = []
        for pitch, duration_ticks in melody:
            freq = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
            duration_sec = (duration_ticks / 480.0) * (60.0 / tempo_bpm)
            num_samples = int(sample_rate * duration_sec)

            attack_len = min(int(sample_rate * 0.015), max(1, num_samples // 4))
            release_len = min(int(sample_rate * 0.025), max(1, num_samples // 4))
            sustain_len = max(0, num_samples - attack_len - release_len)

            for i in range(num_samples):
                if i < attack_len:
                    env = i / attack_len
                elif i < attack_len + sustain_len:
                    env = 1.0 - 0.15 * ((i - attack_len) / max(1, sustain_len))
                else:
                    rel_pos = i - (attack_len + sustain_len)
                    env = 0.85 * (1.0 - rel_pos / max(1, release_len))

                t = i / sample_rate
                if timbre == "woodwind":
                    val = (
                        0.55 * math.sin(2.0 * math.pi * freq * t)
                        + 0.25 * math.sin(2.0 * math.pi * 2.0 * freq * t)
                        + 0.15 * math.sin(2.0 * math.pi * 3.0 * freq * t)
                        + 0.05 * math.sin(2.0 * math.pi * 4.0 * freq * t)
                    )
                else:
                    val = (
                        0.80 * math.sin(2.0 * math.pi * freq * t)
                        + 0.15 * math.sin(2.0 * math.pi * 2.0 * freq * t)
                        + 0.05 * math.sin(2.0 * math.pi * 3.0 * freq * t)
                    )

                sample = int(32767.0 * 0.70 * env * val)
                samples.append(max(-32768, min(32767, sample)))

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(struct.pack(f"<{len(samples)}h", *samples))

        return output_path

    @staticmethod
    def convert_wav_to_mp3(wav_path: Path, mp3_path: Path) -> Path:
        """Convert WAV to MP3 using ffmpeg if available."""
        import shutil
        import subprocess

        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            subprocess.run(
                [ffmpeg, "-y", "-i", str(wav_path), "-b:a", "192k", str(mp3_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        return mp3_path


if __name__ == "__main__":
    from projects.dorabella.corpus import DORABELLA_TOKENS
    from projects.dorabella.liszt_corpus import LISZT_1886_WORDS

    derived_dir = Path("data/derived")
    derived_dir.mkdir(parents=True, exist_ok=True)

    # 1. Synthesize Dorabella Melody (Allegretto 108 BPM, G major, Oboe/Woodwind)
    d_engine = DualMusicalCipherEngine(tokens=DORABELLA_TOKENS)
    d_mid = derived_dir / "dorabella_melody.mid"
    d_wav = derived_dir / "dorabella_melody.wav"
    d_mp3 = derived_dir / "dorabella_melody.mp3"

    d_engine.generate_midi_file(d_mid, scale="g_major", orientation_offset=0, instrument_program=68, tempo_bpm=108)
    d_engine.generate_wav_file(d_wav, scale="g_major", orientation_offset=0, tempo_bpm=108, timbre="woodwind")
    d_engine.convert_wav_to_mp3(d_wav, d_mp3)
    print(f"[+] Dorabella synthesized: {d_mid.name} ({d_mid.stat().st_size} B), {d_wav.name} ({d_wav.stat().st_size} B), {d_mp3.name} ({d_mp3.stat().st_size} B)")

    # 2. Synthesize Liszt Fragment Melody (Andante 96 BPM, E minor, Flute)
    liszt_tokens = [
        # Word 1 (3): [BMK]
        1, 12, 10,
        # Word 2 (6): [GKKOIM]
        6, 10, 10, 14, 8, 12,
        # Word 3 (3): [MCG]
        12, 2, 6,
        # Word 4 (6): [KMBKCC]
        10, 12, 1, 10, 2, 2,
    ]
    l_engine = DualMusicalCipherEngine(tokens=liszt_tokens)
    l_mid = derived_dir / "liszt_fragment_melody.mid"
    l_wav = derived_dir / "liszt_fragment_melody.wav"
    l_mp3 = derived_dir / "liszt_fragment_melody.mp3"

    l_engine.generate_midi_file(l_mid, scale="e_minor", orientation_offset=0, instrument_program=73, tempo_bpm=96)
    l_engine.generate_wav_file(l_wav, scale="e_minor", orientation_offset=0, tempo_bpm=96, timbre="flute")
    l_engine.convert_wav_to_mp3(l_wav, l_mp3)
    print(f"[+] Liszt fragment synthesized: {l_mid.name} ({l_mid.stat().st_size} B), {l_wav.name} ({l_wav.stat().st_size} B), {l_mp3.name} ({l_mp3.stat().st_size} B)")

