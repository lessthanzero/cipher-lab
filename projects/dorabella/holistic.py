"""Holistic Multi-Disciplinary Knowledge Base for the Dorabella Cipher (1897).

Unifies historical, bibliographical, geographical, biological, political,
and musicological constraints surrounding Edward Elgar and Dora Penny in July 1897.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class HistoricalChronology:
    """Historical timeline and biographical records for July 1897."""
    date_sent: str = "1897-07-14"
    sender: str = "Edward William Elgar (b. 1857-06-02, aged 40)"
    recipient: str = "Dora Penny (b. 1874-02-09, aged 23)"
    residence_sender: str = "'Forli', Alexandra Road, Malvern Link, Worcestershire"
    residence_recipient: str = "The Rectory, St Peter's Collegiate Church, Wolverhampton, Staffordshire"
    visitation_window: str = "1897-07-09 to 1897-07-14 (Elgars stayed at Wolverhampton Rectory)"
    delivery_mechanism: str = "Pencilled 'Miss Penny' on reverse, inserted into Alice Elgar's thank-you letter"
    public_emergence: str = "Published in Dora Penny's 1937 memoir 'Edward Elgar: Memories of a Variation'"
    provenance_fate: str = "Original manuscript note lost after 1937 publication"


@dataclass(frozen=True)
class BibliographicalRecord:
    """Bibliographical citations, related Elgar cryptograms, and past scholarly claims."""
    # Related primary manuscripts by Elgar
    liszt_fragment_1886: str = (
        "1886-04 concert program annotated by Elgar with 18 semicircular glyphs + underscore. "
        "Establishes that the 24-symbol semicircular alphabet was a preexisting personal shorthand."
    )
    pall_mall_solution_1896: str = (
        "1896-04 solution to John Holt Schooling's cryptographic challenge in The Pall Mall Magazine. "
        "Preserved in Elgar's 'Cryptogram card'; demonstrates mastery of polyalphabetic, grille, and transposition methods."
    )
    clock_face_notebook_1920s: str = (
        "1920s notebook containing semicircular glyphs plotted around 8-point clock-face / compass diagrams."
    )
    # Peer-reviewed & historical cryptanalytic literature
    sams_1970: str = "Eric Sams (1970). 'Elgar's cipher solved'. The Musical Times (phonetic shorthand; 109 letters from 87 glyphs)."
    bauer_2017: str = "Craig Bauer (2017). 'Unsolved! The History and Mystery of the World's Greatest Ciphers', Princeton Univ Press."
    roberts_2011: str = "Tim S. Roberts (2011). 'Solving the Dorabella Cipher' (simple substitution with bizarre nonsense words)."
    henderson_2011: str = "Richard Henderson (2011). 'Dorabella Solved' (claimed romantic poem via arbitrary nulls)."
    packwood_2020: str = "Wayne Packwood (2020). 'Elgar as cryptographer – Tuning and Turing'. Musical Opinion."
    wase_2023: str = (
        "Viktor Wase (2023). 'Dorabella unMASCed – the Dorabella Cipher is not an English or Latin "
        "Mono-Alphabetical Substitution Cipher'. Cryptologia, 49(1), 15-24. "
        "Rigorous algorithmic proof that automated MASC solvers solve authentic 87-char ciphers but fail on Dorabella."
    )


@dataclass(frozen=True)
class GeographicalGazetteer:
    """Topographical and geographical locations intimately associated with the cipher."""
    locations: Dict[str, str] = field(default_factory=lambda: {
        "Wolverhampton": "Staffordshire industrial Black Country; location of Rev. Penny's St Peter's Rectory.",
        "Malvern": "Spa town at the foot of the Malvern Hills, Worcestershire; home of Elgar at 'Forli'.",
        "Severn Valley": "River Severn and River Teme valley where Elgar cycled and fished.",
        "Hasfield Court": "Gloucestershire country estate of William Meath Baker (Variation IV 'W.M.B.'), Alice's cousin.",
        "Birchwood Lodge": "Rural cottage near Storridge, Herefordshire; Elgar's woodland composing hideaway.",
        "Worcester": "Elgar's birthplace (Broadheath) and father's music shop on High Street.",
        "Powick": "Worcester County Lunatic Asylum where Elgar was bandmaster (1879-1884).",
    })


@dataclass(frozen=True)
class BiologicalAndNaturalContext:
    """Elgar's deep engagement with biology, animal behavior, speech physiology, and natural sciences."""
    # Animal & behavioral biology
    dan_the_bulldog: str = (
        "George Robertson Sinclair's bulldog 'Dan' (Variation XI of Enigma). Commemorates Dan paddling "
        "in the River Wye, barking in rejoice upon climbing the bank. Elgar: 'Set that to music!'."
    )
    malvern_bioacoustics: str = (
        "Elgar was an obsessive naturalist, transcribing birdsong (curlews, blackbirds, robins) into musical staves. "
        "Pioneered box-kite aerodynamics along Malvern Ridge."
    )
    # Dora Penny's physiological traits
    dorabella_stammer: str = (
        "Dora Penny had a slight, charming speech stammer. Elgar mimicked this physiological trait in "
        "Variation X ('Dorabella - Intermezzo') with dancing, fluttering woodwind triplets (strings & oboe staccato)."
    )
    # The Ark chemistry lab
    the_ark_laboratory: str = (
        "Elgar maintained a chemistry lab in his garden shed ('The Ark'), inventing the 'Elgar Sulphuretted "
        "Hydrogen Apparatus', synthesizing organic compounds, inks, and pyrotechnics."
    )


@dataclass(frozen=True)
class PoliticalAndSociologicalContext:
    """Class tensions, religious status, and Imperial politics of 1897."""
    religious_outsider: str = (
        "Elgar was a devout Roman Catholic and the son of a tradesman (piano tuner). In late-Victorian "
        "society, this placed him at a severe disadvantage against the Anglican establishment (such as Rev. Penny)."
    )
    marriage_disinheritance: str = (
        "Alice Roberts was the daughter of Major-General Sir Henry Gee Roberts. Her aristocratic family "
        "disinherited her for marrying Elgar, an impoverished Catholic music teacher."
    )
    diamond_jubilee_1897: str = (
        "June 1897 was Queen Victoria's Diamond Jubilee. Elgar's 'Imperial March' was performed in London, "
        "giving him his first taste of national visibility just weeks before the Dorabella note was penned."
    )
    melanesian_mission: str = (
        "Rev. Alfred Penny (Dora's father) served 1876-1886 as an Anglican missionary in the Solomon Islands "
        "and Norfolk Island. He brought back Melanesian talismans, shells, and carved glyphs, frequently "
        "discussed at the rectory as linguistic curiosities."
    )


class HolisticDorabellaContext:
    """Unified holistic multi-disciplinary query provider."""

    def __init__(self) -> None:
        self.chronology = HistoricalChronology()
        self.bibliography = BibliographicalRecord()
        self.geography = GeographicalGazetteer()
        self.biology = BiologicalAndNaturalContext()
        self.politics = PoliticalAndSociologicalContext()

    def get_summary(self) -> Dict[str, str]:
        return {
            "History": f"{self.chronology.date_sent}: Note from {self.chronology.sender} to {self.chronology.recipient}",
            "Bibliography": "Liszt Fragment (1886), Pall Mall (1896), Wase unMASCed (2023)",
            "Geography": f"{len(self.geography.locations)} key sites (Malvern, Wolverhampton, Severn, Hasfield)",
            "Biology": "Dan the bulldog, Malvern birdsong, 'The Ark' chemistry lab, Dora's stutter physiology",
            "Politics": "Catholic tradesman outsider, Diamond Jubilee 1897, Melanesian mission talismans",
        }

    def get_lexicon_cribs(self) -> List[str]:
        """Extract high-probability vocabulary cribs grounded in the holistic context."""
        return [
            # Personal names & pet names
            "DORA", "DORABELLA", "PENNY", "EDWARD", "ELGAR", "ALICE", "CARICE",
            # Geographic & familial
            "MALVERN", "FORLI", "WOLVERHAMPTON", "RECTORY", "HASFIELD", "BAKER",
            # Biological & domestic
            "DAN", "BULLDOG", "KITE", "BIRD", "STAMMER", "ARK",
            # Social & conversational
            "THANKS", "VISIT", "MUSIC", "VARIATION", "NOTE", "ENIGMA", "JUBILEE",
            # Missionary / Pacific
            "SOLOMON", "MISSION", "TALISMAN", "ISLAND",
        ]
