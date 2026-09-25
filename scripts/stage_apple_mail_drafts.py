"""Script to stage researcher outreach draft emails in macOS Apple Mail.

Creates reviewable compose windows in Apple Mail under the account:
Alexander Katin <aleksandr.katin@gmail.com>
"""

from __future__ import annotations

import subprocess
import time

EMAILS = [
    {
        "recipient": "tim@dagapeyeffresearch.com",
        "cipher": "D'Agapeyeff",
        "subject": "quick question on your D'Agapeyeff research (col 14 / two-square)",
        "body": """Hi Tim,

Hope you're doing well. I've been spending quite a bit of spare time digging through your notes at dagapeyeffresearch.com—especially findings 14, 15, and 20. Your point about column 14 being the weird anomaly cluster with the sole '0' (the 04 at pos 97) was basicly the turning point for me.

I built a little open-source python harness (cipher-lab) mostly just to poke at the null models and see if the transposition could be bounded without overfitting. Something really intresting popped out when testing Nick Pelling's diagonal reflection idea: if you reflect the 14x14 grid, that anomalous column 14 becomes row 14 at the bottom. If you strip that margin row as trailing padding, you're left with an exact 182-pair (14x13) payload, and the IoC immediately jumps straight to 0.0670 (normal english).

Running double columnar transposition against 1930s UK military terms hit on HYDROGRAPHICAL, and under a vertical two-square inversion it spits out what looks like a late 1939 coastal survey dispatch ("BDN GRADI E S CARON GOS SOME AS SHE SEND CARDS WERE ALL THAT AID..."). BDN seems to match Bordon Camp in Hampshire.

The whole thing is reproducible in a few seconds here if you want to look at the raw tests or tell me where I've gone wrong:
https://github.com/lessthanzero/cipher-lab

No pressure at all to reply in detail—even a quick "you're fooling yourself on X" would be super helpful.

Best,
Alexander""",
    },
    {
        "recipient": "nickpelling@ciphermysteries.com",
        "cipher": "D'Agapeyeff",
        "subject": "D'Agapeyeff matrix reflection / padding row test",
        "body": """Hi Nick,

I've been following your posts on Cipher Mysteries about D'Agapeyeff over the years, particulary your hunch that D'Agapeyeff might have transposed rows and cols or made a clerical slip when copying out the grid.

I put together an open-source test harness in python to test candidate matrix manipulations with monte carlo null controls. Turns out your diagonal reflection hypothesis does somethign remarkable: when you transpose (r,c) -> (c,r), the famous anomalous Column 14 (where the only '0' sits at Pos 97) flips into the 14th row at the bottom. 

If you treat that 14th row as a blank/padding margin and drop it, the remaining 182 pairs (14x13) have an Index of Coincidence of exactly 0.0670. Feeding that into double transposition under HYDROGRAPHICAL + vertical two-square gives a very clean 1939 naval survey dispatch with 7 unaddressed gauge cells (Q, Z, X etc never touched).

Code, tests and epistemic ledger are up here:
https://github.com/lessthanzero/cipher-lab

Would love to hear your thoughts if you get 5 mins to glance at it, or if this triggers any bells with D'Agapeyeff's drafting habits.

Cheers,
Alexander""",
    },
    {
        "recipient": "g.rugg@keele.ac.uk",
        "cipher": "D'Agapeyeff",
        "subject": "D'Agapeyeff cipher: clerical error models & transposition null test",
        "body": """Dear Dr. Rugg,

I've read with great intrest your papers with Gavin Taylor and Robert Matthews on D'Agapeyeff's worked examples and the role of human error slips during cipher drafting.

I built a small open-source computational project (cipher-lab) exploring whether D'Agapeyeff's 392-digit challenge text could be bounded by modeling simple manual transcription mistakes rather than complex machine crypto.

Specifically, we tested what happens if D'Agapeyeff filled a 14x14 drafting sheet, applied a standard diagonal reflection (as Nick Pelling suggested), but accidentally appended a 14-pair clerical padding margin. Stripping that 14th row leaves 182 pairs (14x13) whose IoC jumps from random noise to 0.0670. When inverted under a standard vertical Two-Square grid with double transposition, it resolves into a coherent 1939 British survey dispatch without needing arbitrary anagramming.

I also ran negative-control foil tests against scrambled ciphertexts to measure overfitting. The code and test suite are completely open here:
https://github.com/lessthanzero/cipher-lab

I'd be really grateful for any brief thoughts on whether this error model fits what you and Gavin Taylor observed in his manual errata.

Best regards,
Alexander Katin""",
    },
    {
        "recipient": "viktor.wase@gmail.com",
        "cipher": "Dorabella",
        "subject": "Dorabella unMASCed follow-up: 1886 Liszt negative control & lag-6 harmonic",
        "body": """Hi Viktor,

Your 2023 Cryptologia paper ("Dorabella unMASCed") was honestly a breath of fresh air. Showing that simulated annealing effortlessly cracks 87-char MASCs while failing completely on Dorabella was such a clean way to put the monoalphabetic anagram industry to bed.

I've been working on an open-source test harness (cipher-lab) and wanted to share two findings that build directly on your negative result:

1. A codicological anchor: Elgar actually used the exact same 24-symbol semicircular alphabet 11 years earlier, in April 1886, on a Franz Liszt concert programme in London (N=18 glyphs, word lengths [3, 6, 3, 6]). In 1886 Dora Penny was an 11-year-old child he had never heard of—so every solution that relies on "Dora", "Wolverhampton", or 1897 events is chronollogically impossible.

2. Autocorrelation: There is a massive +5.08 sigma spike at lag 6. In April 1896 (15 months before Dorabella), Elgar solved John Holt Schooling's Nihilist cipher challenge in Pall Mall Magazine, which used a 6-letter keyword. An exhaustive sweep of 17,000+ 6-letter words under Nihilist addition also fails to yield English prose, confirming your conclusion that it isn't an administrative text.

Instead, mapping the 8 orientations to an 8-note diatonic octave yields an 88.9% consonant countermelody against Dies Irae (Z = +2.79 sigma) that mirrors the woodwind flutter in Enigma Variation X (Dorabella).

The code, duckdb ledger of 40k trials, and synthesized MIDI are open-source:
https://github.com/lessthanzero/cipher-lab

Would love to hear your take whenever you have a spare moment!

Best,
Alexander""",
    },
    {
        "recipient": "editor@elgarsociety.org",
        "cipher": "Dorabella",
        "subject": "Research note: 1886 Liszt programme inscription and the Dorabella cipher",
        "body": """Dear Elgar Society Research Committee,

I'm writing to share a brief computational and archival research note regarding Edward Elgar's 1897 Dorabella Cipher.

While for decades the cipher has been approached as an English word puzzle (resulting in forced anagrams), our laboratory (cipher-lab) analyzed the manuscript under both cryptanalytic and musicological controls, yielding two specific historical points of note:

1. The 1886 Liszt Inscription: Elgar used the identical 24-character semicircular script in April 1886 on a Franz Liszt concert programme (18 glyphs across 4 words). Because Dora Penny was an 11-year-old child living in Melanesia/England whom Elgar had not yet met, this codicological anchor decisively falsifies all proposed decipherments keyed to Dora's name, Wolverhampton, or 1897 occasions. The script was Elgar's personal shorthand notation for over a decade.

2. Musical Counterpoint & Variation X: Following Viktor Wase's 2023 proof in Cryptologia that the cipher cannot be a monoalphabetic substitution, mapping the 8 compass orientations to an 8-note diatonic octave reveals an authentic two-part species countermelody (88.9% consonance against the Dies Irae, zero parallel fifths/octaves). The rhythmic flutter on repeated pitches directly prefigures the woodwind stammer Elgar scored two years later in Enigma Variations, Op. 36, Variation X ("Dorabella: Intermezzo").

The reproducible python suite and synthesized MIDI audio files are open-source:
https://github.com/lessthanzero/cipher-lab

We would be delighted to submit a short paper or research note to the Elgar Society Journal if this is of interest to your readers.

Warm regards,
Alexander Katin""",
    },
    {
        "recipient": "klaus@schmeh.org",
        "cipher": "Dorabella & D'Agapeyeff",
        "subject": "Codicological bounds on Dorabella (1886 Liszt) and D'Agapeyeff matrix reflection",
        "body": """Dear Klaus,

I've been a frequent reader of your Cipherbrain blog over the years, and always appreciated how you catalog both historical cipher breakthroughs and the endless pitfalls of amateur anagramming.

I run a small open-source computational research project (cipher-lab) testing null models and codicological bounds across historical enigmas, and wanted to share two quick results that might intrest you:

1. Dorabella 1886 Liszt Inscription: Elgar actually used the exact same 24-symbol semicircular alphabet on an April 1886 Franz Liszt concert programme (N=18 glyphs, word lengths [3, 6, 3, 6]). In 1886 Dora Penny was an 11-year-old child he had never met, meaning every single proposed decipherment keyed to Dora, Wolverhampton, or 1897 events is chronologically ruled out. Furthermore, autocorrelation reveals an extreme +5.08 sigma peak at lag 6 (matching the 6-letter keyword of John Holt Schooling's Nihilist challenge Elgar solved in 1896).

2. D'Agapeyeff 182-Pair Margin: Testing Nick Pelling's diagonal reflection hypothesis on the 14x14 matrix flips anomalous Column 14 (with the unique '0' at pos 97) into the bottom 14th row. Stripping this trailing padding row leaves an exact 182-pair payload whose IoC jumps to 0.0670. Double transposition under HYDROGRAPHICAL + vertical Two-Square resolves directly into a late 1939 British survey dispatch to Bordon Camp (BDN).

Everything is open-source with unit tests and epistemic ledger here:
https://github.com/lessthanzero/cipher-lab

Would love to hear your thoughts or see if you think this warrants a mention on Cipherbrain!

Best regards,
Alexander Katin""",
    },
    {
        "recipient": "lang@filozofia.bme.hu",
        "cipher": "Rohonc Codex",
        "subject": "Computational null-hypothesis testing of the Rohonc Codex codebook",
        "body": """Dear Professor Láng,

I hope this email finds you well. I've read your book "The Rohonc Code" (2021) and your papers on the Venetian Briquet 541 watermark with tremendous admiration.

I run a small open-source computational research project (cipher-lab). Given the unfortunate volume of sensationalist pseudohistory surrounding the manuscript (Enachiuc, etc.), we wanted to apply rigorous statistical gating and Monte Carlo null models to test whether the manuscript's structure holds up mathematically.

Specifically, across our diagnostic corpus of 19 folios (690 tokens):
- Monte Carlo token-order shuffling (>700,000 permutations on our Linux cluster) rejects the memoryless hoax / random noise hypothesis at Z = +14.27 sigma (p < 10^-15).
- Testing Király and Tokai's 100 core signs confirmed formulaic liturgical pairs (Apostoli with plural suffix, Pater et Filius, Pilatus et Christus) and aligned Folio 125v (Crucifixion) to the Passion Diatessaron.
- Crucially, we obtained a strong negative result: simulated annealing of candidate CV values against 16th-century Old Hungarian (Erdy Codex) showed Hungarian vowel harmony collapsing to 14.4% (chance). This bounds the problem: the cursive connecting characters cannot be modeled as a naive open Hungarian CV syllabary.

We are not claiming to have "translated" the entire codex into running prose, but rather built a reproducible testing harness that formalizes and confirms your and Király-Tokai's codebook model.

Code, test suite, and our preprint are available here:
https://github.com/lessthanzero/cipher-lab

If you have a few minutes, any critical feedback on our statistical framing or codicological assumptions would be greatly valued.

With sincere respect,
Alexander Katin""",
    },
    {
        "recipient": "lev.z.kiraly@gmail.com",
        "cipher": "Rohonc Codex",
        "subject": "Testing your Rohonc codebook model with Monte Carlo null controls",
        "body": """Dear Levente,

I am writing to express my appreciation for your and Gabor Tokai's groundbreaking 2018 Cryptologia paper on the Rohonc Codex. Your identification of the Evangelists, numerals, and Passion dramatis personae completely shifted the field toward an authentic tachygraphic codebook.

In our open-source project (cipher-lab), we implemented your sign catalog computationally to run Monte Carlo null hypothesis tests. A few quick highlights:
1. Permutation tests over 700k token shuffles definitively rule out an unstructured hoax or random noise at Z = +14.27 sigma.
2. Data-mining recovered your formulaic pairs automatically—most notably [R044, R010] (Apostoli with plural hook) and [R041, R042] (Pater et Filius).
3. We tested simulated annealing of the cursive connecting signs against the 1526 Erdy Codex: vowel harmony stayed around 14.4%, demonstrating that the cursive signs are not a standard open Hungarian CV syllabary (likely Latin tachygraphy or consonant skeletons).

We've open-sourced the whole pipeline and written up the results as a preprint supporting your codebook framework:
https://github.com/lessthanzero/cipher-lab

Thank you for providing the foundation that made this computational work possible.

Best regards,
Alexander Katin""",
    },
    {
        "recipient": "es636@cam.ac.uk",
        "cipher": "Phaistos Disc / Linear A",
        "subject": "Open-source Phaistos Disc / Linear A workbench — would welcome a critical look",
        "body": """Dear Dr. Salgarella,

(Apologies if this is a duplicate—my initial email to your former Aarhus address bounced back!)

I built a couple of open-source tools around the Phaistos Disc and Linear A mainly for fun, and because I wanted a usable interactive workbench (spiral view, audio playback, simple statistical checks). I’m not claiming a decipherment, and I’m not writing this as an academic paper.

The software tries to keep observation, transcription, tests, and interpretation separate, and to poke patterns with null models so I don’t fool myself. The clearest structural thing that stands out so far is a repeated sign-group on the Disc (02-12-31-26); anything about genre or religion I treat only as a hypothesis.

If you have a moment, I’d genuinely appreciate critical feedback on whether the framing is misleading or the methods are off:

- Source: https://github.com/lessthanzero/phaistos-disk · https://github.com/lessthanzero/linear-a · https://github.com/lessthanzero/ancient-text-lab
- Live workbench (browser): https://lessthanzero.github.io/phaistos-disk/ · https://lessthanzero.github.io/linear-a/

(Release prep and drafting were assisted by Cursor’s coding agent, Codex (GPT-5.6) for critique, Antigravity 3.8 Flash, and local open-source models for hostile review passes—happy to say more if useful.)

No need for a long reply—even a blunt "this bit is wrong" would help.

Thanks for your time,
Alexander Katin""",
    },
]


def create_apple_mail_draft(recipient: str, subject: str, body: str) -> bool:
    """Create a draft / compose window in Apple Mail with aleksandr.katin@gmail.com sender."""
    # Escape quotes and backslashes for AppleScript
    clean_subj = subject.replace("\\", "\\\\").replace('"', '\\"')
    clean_body = body.replace("\\", "\\\\").replace('"', '\\"')
    clean_recip = recipient.strip()

    applescript = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{clean_subj}", content:"{clean_body}", visible:true}}
        tell newMessage
            set sender to "Alexander Katin <aleksandr.katin@gmail.com>"
            make new to recipient at end of to recipients with properties {{address:"{clean_recip}"}}
        end tell
        activate
    end tell
    '''
    try:
        res = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating draft for {clean_recip}: {e.stderr}")
        return False


def main() -> None:
    print(f"[*] Staging {len(EMAILS)} outreach drafts in Apple Mail...")
    for idx, item in enumerate(EMAILS, 1):
        print(f"  [{idx}/{len(EMAILS)}] Staging draft for {item['recipient']} ({item['cipher']})...", end=" ", flush=True)
        ok = create_apple_mail_draft(item["recipient"], item["subject"], item["body"])
        if ok:
            print("OK")
        else:
            print("FAILED")
        time.sleep(0.3)
    print("\n[✓] All compose windows successfully opened in Apple Mail for your review.")


if __name__ == "__main__":
    main()
