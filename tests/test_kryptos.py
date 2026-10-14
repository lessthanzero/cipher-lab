"""Test suite for Kryptos K4 under CipherLab Blind Cryptanalysis Protocol."""

from __future__ import annotations

import pytest

from projects.kryptos.manifests import (
    BLIND_PATH,
    CONTEXTUAL_PATH,
    GROUND_TRUTH_PATH,
    generate_datasets_manifest,
    load_dataset,
    sha256_of_file,
)
from projects.kryptos.tier1_blind.stats import (
    analyze_factorization_constraints,
    calculate_autocorrelation,
    compute_blind_profile,
)
from projects.kryptos.tier1_blind.unicity import (
    audit_scheidt_families,
    evaluate_cipher_family_unicity,
)
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    check_period_consistency,
    derive_keystream,
    extract_known_pairs,
    sweep_periods,
)
from projects.kryptos.tier3_verification.completion_audit import (
    CryptanalyticVerdict,
    evaluate_completion_standard,
)


def test_k4_dataset_manifest_integrity() -> None:
    """Verify SHA-256 digest consistency across all tier datasets."""
    manifest = generate_datasets_manifest()
    assert "blind" in manifest["datasets"]
    assert "contextual" in manifest["datasets"]
    assert "ground_truth" in manifest["datasets"]

    for tier_key, meta in manifest["datasets"].items():
        assert len(meta["sha256"]) == 64
        assert int(meta["sha256"], 16) > 0


def test_k4_tier_access_control() -> None:
    """Verify that Tier 1 agents are cryptographically blocked from higher tiers."""
    # Tier 1 agent can load blind dataset
    blind = load_dataset(BLIND_PATH, current_tier=1)
    assert blind["access_control"]["allowed_for_blind_search"] is True
    assert blind["access_control"]["contains_cribs"] is False

    # Tier 1 agent cannot load contextual dataset (Tier 2)
    with pytest.raises(PermissionError) as exc_info:
        load_dataset(CONTEXTUAL_PATH, current_tier=1)
    assert "Blind Protocol Violation" in str(exc_info.value)

    # Tier 1 agent cannot load ground truth dataset (Tier 3)
    with pytest.raises(PermissionError) as exc_info2:
        load_dataset(GROUND_TRUTH_PATH, current_tier=1)
    assert "Blind Protocol Violation" in str(exc_info2.value)


def test_k4_corpus_invariants() -> None:
    """Verify structural invariants of the 97-character K4 ciphertext."""
    blind = load_dataset(BLIND_PATH, current_tier=1)
    ct = blind["ciphertext"]

    assert len(ct) == 97
    assert ct.isupper()
    assert all(c in STANDARD_ALPHABET for c in ct)

    # Verify verified slices for public cribs
    assert ct[21:34] == "FLRVQQPRNGKSS"
    assert ct[63:74] == "NYPVTTMZFPK"


def test_k4_blind_statistics() -> None:
    """Verify blind statistical profiling of raw ciphertext."""
    blind = load_dataset(BLIND_PATH, current_tier=1)
    ct = blind["ciphertext"]
    profile = compute_blind_profile(ct)

    assert profile["text_length"] == 97
    assert profile["unique_characters"] == 26

    # Polyalphabetic IoC check: ~0.03608 (flat, far below English 0.0667)
    assert 0.034 <= profile["index_of_coincidence"] <= 0.038

    # Shannon entropy should be high (~4.55 bits)
    assert 4.4 <= profile["shannon_entropy_bits"] <= 4.7

    # Prime length confirmation
    factors = profile["factorization_constraints"]
    assert factors["is_prime"] is True

    # Autocorrelation harmonic at lag 7
    top_lags = profile["autocorrelation_top_lags"]
    assert any(item["lag"] == 7 and item["z_score"] > 2.5 for item in top_lags)


def test_unicity_distance_gates() -> None:
    """Verify Shannon unicity gating on candidate cipher families."""
    audit = audit_scheidt_families(corpus_length=97)
    families = {f["model_name"]: f for f in audit["families"]}

    # Bounded classical families must PASS
    assert families["Periodic Vigenère (Period 7)"]["is_determined"] is True
    assert families["Quagmire III (Keywords L1=8, L2=7)"]["is_determined"] is True
    assert families["Double Columnar Transposition (10x10)"]["is_determined"] is True

    # Unconstrained system must be REJECTED (U0 > 97)
    unconstrained = families["Unconstrained Arbitrary Substitution + Transposition"]
    assert unconstrained["is_determined"] is False
    assert unconstrained["unicity_distance_chars"] > 97


def test_kpa_algebraic_solver_synthetic_vector() -> None:
    """Verify algebraic solver correctly recovers a synthetic periodic Vigenère key."""
    # Synthetic test: Plaintext and Key of period 5
    synthetic_plain = "HELLOWORLDTHISISATESTFORCIPHERLABKRYPTOSINVESTIGATION"
    key = "CIPHR"
    alphabet = STANDARD_ALPHABET
    m = len(alphabet)

    ct_chars = []
    for i, p in enumerate(synthetic_plain):
        k = key[i % len(key)]
        c_val = (alphabet.index(p) + alphabet.index(k)) % m
        ct_chars.append(alphabet[c_val])
    synthetic_cipher = "".join(ct_chars)

    # Extract 10 pairs
    pairs = [
        (i, synthetic_cipher[i], synthetic_plain[i])
        for i in [0, 1, 2, 5, 6, 7, 10, 11, 12, 15]
    ]
    points = derive_keystream(pairs, alphabet=alphabet, cipher_type="vigenere")

    # Test period 5 consistency
    res5 = check_period_consistency(points, period=5, alphabet=alphabet)
    assert res5.is_consistent is True
    # The derived key letters should match the original key
    for idx, char in enumerate(res5.partial_key):
        if char != "?":
            assert char == key[idx]


def test_kpa_algebraic_solver_k4_falsification() -> None:
    """Verify that pure periodic substitution across periods 2..26 is falsified on K4."""
    # On actual K4 cribs, direct periodic Vigenere must have ZERO consistent periods
    vig_results = sweep_periods(max_period=26, alphabet=STANDARD_ALPHABET, cipher_type="vigenere")
    assert all(not res.is_consistent for res in vig_results)

    # On actual K4 cribs, Quagmire III on Kryptos alphabet must also have ZERO consistent periods
    q3_results = sweep_periods(max_period=26, alphabet=KRYPTOS_ALPHABET, cipher_type="vigenere")
    assert all(not res.is_consistent for res in q3_results)


def test_completion_standard_logic() -> None:
    """Verify completion audit states adhere to the Blind Cryptanalysis Protocol."""
    # Case A: Plaintext known from archives, method unverified
    audit_curr = evaluate_completion_standard(
        has_specified_method=False,
        plaintext_known_from_archives=True,
    )
    assert audit_curr.verdict == CryptanalyticVerdict.PLAINTEXT_KNOWN_METHOD_UNVERIFIED

    # Case B: Nothing known
    audit_unsolved = evaluate_completion_standard(
        has_specified_method=False,
        plaintext_known_from_archives=False,
    )
    assert audit_unsolved.verdict == CryptanalyticVerdict.UNSOLVED

    # Case C: All criteria met
    audit_full = evaluate_completion_standard(
        has_specified_method=True,
        has_specified_key=True,
        is_reproducible=True,
        explains_full_corpus=True,
        zero_ad_hoc_errata=True,
        independent_reproduced=True,
        beats_negative_controls=True,
        plaintext_known_from_archives=True,
    )
    assert audit_full.verdict == CryptanalyticVerdict.CRYPTOGRAPHICALLY_RECOVERED


def test_14x7_matrix_structure_and_anchors() -> None:
    """Verify 14x7 matrix coordinates and anchor cell populating."""
    from projects.kryptos.tier2_contextual.matrix_solver import KeystreamMatrix14x7

    matrix = KeystreamMatrix14x7(null_placement="trailing")
    # Verify grid dimensions
    assert len(matrix.grid) == 14
    assert all(len(row) == 7 for row in matrix.grid)

    # Verify Crib 1 starts at Row 3, Col 0
    cell_c1_start = matrix.grid[3][0]
    assert cell_c1_start is not None
    assert cell_c1_start.is_anchor is True
    assert cell_c1_start.linear_idx == 21
    assert cell_c1_start.plain_char == "E"
    assert cell_c1_start.cipher_char == "F"

    # Verify Crib 2 starts at Row 9, Col 0
    cell_c2_start = matrix.grid[9][0]
    assert cell_c2_start is not None
    assert cell_c2_start.is_anchor is True
    assert cell_c2_start.linear_idx == 63
    assert cell_c2_start.plain_char == "B"
    assert cell_c2_start.cipher_char == "N"

    # Verify differentials can be analyzed
    diffs = matrix.analyze_differentials(key_type="kry_vig_shift")
    assert len(diffs["row_differentials"]) > 0
    assert len(diffs["col_differentials"]) > 0


def test_running_key_evaluation_logic() -> None:
    """Verify running key evaluation on synthetic matching and non-matching texts."""
    from projects.kryptos.tier2_contextual.running_key_sweep import evaluate_running_key_offset

    anchors = [(0, "K", "A"), (1, "R", "B")]  # Key = K, Q => Vig: (0+10)%26=10('K'), (1+16)%26=17('R')
    # Perfect key is "KQ"
    perfect_corpus = "KQ"
    matches, total, rate = evaluate_running_key_offset(
        corpus=perfect_corpus,
        offset=0,
        anchor_pairs=anchors,
        alphabet=STANDARD_ALPHABET,
        cipher_type="vigenere",
        grid_mode="linear",
    )
    assert matches == 2
    assert rate == 1.0


def test_constrained_matrix_annealer_preserves_anchors() -> None:
    """Verify simulated annealer preserves 100% of the 24 anchor cells."""
    from projects.kryptos.tier2_contextual.matrix_annealer import MatrixAnnealer

    annealer = MatrixAnnealer()
    res = annealer.anneal(duration_secs=0.2, seed=123)

    # Plaintext must contain exact cribs at their exact positions
    assert res.plaintext_sample[21:34] == "EASTNORTHEAST"
    assert res.plaintext_sample[63:74] == "BERLINCLOCK"


def test_route_mask_sweeper_logic() -> None:
    """Verify route_mask_sweeper generates valid permutations and runs without errors."""
    from projects.kryptos.tier2_contextual.route_mask_sweeper import (
        get_standard_routes,
        test_route_period_consistency,
    )

    routes = get_standard_routes()
    assert len(routes) >= 8
    for rname, pi in routes.items():
        assert len(pi) == 97
        # Ensure it is a valid permutation of indices 0..96
        assert sorted(pi) == list(range(97))

    # Synthetic test: perfect periodic key
    # If route is identity, and anchor keys repeat with period 3:
    synthetic_anchors = {0: 5, 3: 5, 6: 5, 1: 2, 4: 2}
    ok, n_res, confs = test_route_period_consistency(list(range(97)), period=3, anchor_keys=synthetic_anchors)
    assert ok is True
    assert confs == 0


def test_bifid_period7_algebraic_impossibility() -> None:
    """Verify that Bifid period 7 on a 5x5 Polybius square is algebraically UNSAT."""
    from z3 import Solver, Int, Distinct, sat

    s = Solver()
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    rows = {ch: Int(f"r_{ch}") for ch in alphabet}
    cols = {ch: Int(f"c_{ch}") for ch in alphabet}

    for ch in alphabet:
        s.add(rows[ch] >= 0, rows[ch] < 5)
        s.add(cols[ch] >= 0, cols[ch] < 5)

    cell_ids = [rows[ch] * 5 + cols[ch] for ch in alphabet]
    s.add(Distinct(*cell_ids))

    # Essential pigeonhole constraints from Block 3 & Block 9
    s.add(rows["R"] == rows["N"], cols["R"] == rows["O"])
    s.add(rows["V"] == rows["R"], cols["V"] == cols["E"])
    s.add(rows["N"] == rows["B"], cols["N"] == rows["E"])
    s.add(rows["Y"] == rows["R"], cols["Y"] == rows["L"])
    s.add(rows["V"] == rows["C"], cols["V"] == cols["B"])

    # Forces 6 letters into the same row in a 5-wide grid -> UNSAT
    assert s.check() != sat


def test_cardan_stencil_sweeper_symmetries() -> None:
    """Verify Cardan stencil sweeper correctly enumerates pairs under 14x7 symmetries."""
    from projects.kryptos.tier2_contextual.cardan_stencil_sweeper import (
        get_symmetry_pairs,
        sweep_fixed_geometric_stencils,
    )

    rot_pairs = get_symmetry_pairs("rot180")
    assert len(rot_pairs) == 49
    # Each pair must be symmetric
    for c1, c2 in rot_pairs:
        assert c2 == (13 - c1[0], 6 - c1[1])

    flip_v_pairs = get_symmetry_pairs("flip_v")
    assert len(flip_v_pairs) == 49
    for c1, c2 in flip_v_pairs:
        assert c2 == (13 - c1[0], c1[1])

    # Run fixed stencil sweep
    fixed_hits = sweep_fixed_geometric_stencils()
    assert isinstance(fixed_hits, list)


def test_cross_section_mask_engine() -> None:
    """Verify cross-section 'LAYER TWO' coupling sweeper runs and evaluates matches."""
    from projects.kryptos.tier2_contextual.cross_section_mask import (
        evaluate_cross_section_offset,
        load_k1_k2_k3_plaintexts,
    )

    texts = load_k1_k2_k3_plaintexts()
    assert len(texts) > 0

    anchors = [(0, "K", "A"), (1, "R", "B")]
    m, t, r = evaluate_cross_section_offset(
        k4_anchors=anchors,
        source_text="KQ",
        offset=0,
        alphabet=STANDARD_ALPHABET,
        cipher_type="vigenere",
    )
    assert m == 2
    assert r == 1.0


def test_compass_weltzeituhr_engine() -> None:
    """Verify compass bearings and Weltzeituhr 24-cylinder projection engine."""
    from projects.kryptos.tier2_contextual.compass_weltzeituhr_sweeper import (
        COMPASS_16_POINTS,
        WELTZEITUHR_CITIES,
        run_compass_weltzeituhr_campaign,
    )

    assert len(COMPASS_16_POINTS) == 16
    assert len(WELTZEITUHR_CITIES) >= 24
    assert "BERLIN" in WELTZEITUHR_CITIES
    assert "EASTNORTHEAST" in COMPASS_16_POINTS

    res = run_compass_weltzeituhr_campaign()
    assert "total_hits_above_25pct" in res


def test_formal_math_models_rank1_and_rank2_falsification() -> None:
    """Verify Rank-1 and Rank-2 Bilinear falsifications on K4, with synthetic positive control."""
    from projects.kryptos.tier2_contextual.formal_math_models import (
        load_keystream_matrices,
        run_formal_math_audit,
        solve_rank1_additive_smt,
        solve_rank2_bilinear_algebraic,
    )

    # 1. Negative control on K4: Must be UNSAT across all modes and moduli
    audit = run_formal_math_audit()
    for mname, data in audit.items():
        for mod_str, rdata in data["rank1_additive"].items():
            assert rdata["satisfiable"] is False, f"Rank-1 should be UNSAT for {mname} at {mod_str}"
        for mod_str, rdata in data["rank2_bilinear"].items():
            assert rdata["satisfiable"] is False, f"Rank-2 should be UNSAT for {mname} at {mod_str}"
        for mod_str, recs in data["recurrence_2d"].items():
            assert len(recs) == 0, f"Recurrence should have 0 solutions for {mname} at {mod_str}"

    # 2. Positive control: synthetic rank-1 additive matrix must be SATISFIABLE
    u_true = [i % 26 for i in range(14)]
    v_true = [(3 * j) % 26 for j in range(7)]
    synth_mat = {
        (r, c): (u_true[r] + v_true[c]) % 26
        for r in [3, 4, 9, 10]
        for c in range(7)
    }
    sat_ok, sol = solve_rank1_additive_smt(synth_mat, modulus=26)
    assert sat_ok is True
    assert sol is not None


def test_column_strip_graph_engine() -> None:
    """Verify column strip graph transitions and candidate master strip alignment."""
    from projects.kryptos.tier2_contextual.column_strip_graph import (
        analyze_column_transition_graphs,
        sweep_master_strips_all_columns,
    )

    transitions = analyze_column_transition_graphs()
    assert "standard_vigenere" in transitions
    # In standard Vigenere, cols 0, 4, 5 share delta = 23 (-3 mod 26) from row 3 to row 4
    col4_t = transitions["standard_vigenere"]["col_4"]
    assert col4_t["3_to_4"]["delta"] == 23

    col5_t = transitions["standard_vigenere"]["col_5"]
    assert col5_t["3_to_4"]["delta"] == 23

    strip_res = sweep_master_strips_all_columns()
    assert "kryptos_vigenere" in strip_res
    assert len(strip_res["kryptos_vigenere"]) == 7


def test_fleissner_grille_orbit_mechanics() -> None:
    """Verify 7x7 Fleissner Turning Grille 12-orbit geometry and permutation generation."""
    from projects.kryptos.tier2_contextual.fleissner_grille_sweeper import (
        compute_7x7_orbits,
        generate_fleissner_permutation,
        run_parallel_fleissner_sweep,
    )

    orbits, center = compute_7x7_orbits()
    assert len(orbits) == 12
    assert center == (3, 3)

    # Each orbit must have exactly 4 cells
    all_cells = set()
    for orb in orbits:
        assert len(orb) == 4
        for cell in orb:
            assert cell not in all_cells
            all_cells.add(cell)

    assert len(all_cells) == 48

    # Test permutation generation
    holes = (0,) * 12
    pi = generate_fleissner_permutation(holes, orbits, clockwise=True, readout_by_rows=True)
    assert len(pi) == 48
    assert sorted(pi) == list(range(48))

    # Fast sweep verification
    res = run_parallel_fleissner_sweep(num_processes=2, max_eval=100)
    assert res["total_evaluated"] == 100


def test_dual_panel_sweeper_logic() -> None:
    """Verify Two-Panel anchor partitioning and keyword alignment evaluation."""
    from projects.kryptos.tier2_contextual.dual_panel_sweeper import (
        evaluate_keyword_on_panel,
        load_panel_anchor_datasets,
        sweep_dual_panel_keywords,
    )

    panels = load_panel_anchor_datasets()
    assert len(panels["panel_a"]["row_major"]) == 10
    assert len(panels["panel_b"]["row_major"]) == 14

    # Synthetic test on Panel B
    anchors_b = panels["panel_b"]["row_major"]
    m, tot, rate = evaluate_keyword_on_panel("OCTOBER", anchors_b, "standard", "beaufort")
    assert tot == 14
    assert m >= 0

    res = sweep_dual_panel_keywords(keywords=["KRYPTOS", "BERLIN", "CLOCK"], threshold=0.30)
    assert "panel_a_candidates" in res
    assert "panel_b_candidates" in res


def test_optical_tableau_sweeper_logic() -> None:
    """Verify right-panel tableau structure, extraction, and sliding window evaluation."""
    from projects.kryptos.tier2_contextual.optical_tableau_sweeper import (
        extract_linear_tableau_stream,
        extract_opposite_k4_tableau_chars,
        sweep_optical_tableau_configurations,
    )

    tableau = extract_linear_tableau_stream()
    assert len(tableau) >= 860
    assert "KRYPTOS" in tableau[:70]

    opp = extract_opposite_k4_tableau_chars()
    assert "direct_spatial" in opp
    assert "flipped_horizontal" in opp
    assert "linear_end_97" in opp

    res = sweep_optical_tableau_configurations()
    assert "spatial_alignments" in res
    assert len(res["spatial_alignments"]) > 0


def test_errata_stencil_engine_logic() -> None:
    """Verify intentional errata coordinates, phase dislocation sweep, and mask evaluation."""
    from projects.kryptos.tier2_contextual.errata_stencil_engine import (
        evaluate_errata_stencil_mask,
        test_phase_dislocation,
    )

    mask_info = evaluate_errata_stencil_mask()
    assert len(mask_info["errata_cell_indices"]) > 0

    hits = test_phase_dislocation(max_delta=2, max_period=5)
    assert isinstance(hits, list)


def test_berlin_clock_state_machine_logic() -> None:
    """Verify Mengenlehreuhr lamp state mapping, keystream generator, and sweep logic."""
    from projects.kryptos.tier2_contextual.berlin_clock_state_machine import (
        generate_clock_keystream,
        get_berlin_clock_state,
        sweep_berlin_clock_states,
    )

    r1, r2, r3, r4, total = get_berlin_clock_state(18, 53)
    assert r1 == 3  # 3 * 5 = 15h
    assert r2 == 3  # 3 * 1 = 3h -> 18h
    assert r3 == 10 # 10 * 5 = 50m
    assert r4 == 3  # 3 * 1 = 3m -> 53m
    assert total == 19

    ks = generate_clock_keystream(18, 53, step_minutes=1, length=97)
    assert len(ks) == 97
    assert all(0 <= v < 26 for v in ks)

    res = sweep_berlin_clock_states()
    assert "total_hits_above_25pct" in res


def test_strip_jigsaw_engine_logic() -> None:
    """Verify 7-strip extraction from 14x7 grid and permutation sweep execution."""
    from projects.kryptos.tier2_contextual.strip_jigsaw_engine import (
        load_raw_columns,
        run_parallel_strip_jigsaw_sweep,
    )

    cols = load_raw_columns()
    assert len(cols) == 7
    assert len(cols[0]) == 14
    assert len(cols[6]) == 13

    res = run_parallel_strip_jigsaw_sweep(num_processes=2)
    assert res["total_permutations_tested"] == 5040


def test_m138_strip_dislocation_logic() -> None:
    """Verify M-138 strip physical impossibility proofs and substitution model sweeps."""
    from projects.kryptos.tier2_contextual.m138_strip_dislocation import (
        check_physical_strip_transposition_feasibility,
        evaluate_m138_strip_substitution,
    )

    trans = check_physical_strip_transposition_feasibility()
    assert trans["is_feasible"] is False
    assert trans["impossible_pairs_count"] >= 5

    res = evaluate_m138_strip_substitution()
    assert res["tested_strips_count"] >= 15
    assert isinstance(res["direct_displacement_matches"], list)
    assert isinstance(res["progressive_sliding_matches"], list)


def test_viterbi_periodic_beam_search_logic() -> None:
    """Verify phase collision pigeonhole proofs and periodic search space metrics."""
    from projects.kryptos.tier2_contextual.viterbi_periodic_beam_search import (
        prove_phase_collisions,
    )

    collisions = prove_phase_collisions(max_period=10)
    for mode, data in collisions.items():
        for L in range(1, 11):
            assert data[L]["has_collision"] is True


def test_extended_running_key_sweeper_logic() -> None:
    """Verify loading of historical corpora and running key alignment evaluation."""
    from projects.kryptos.tier2_contextual.extended_running_key_sweeper import (
        load_corpora,
        sweep_historical_running_keys,
    )

    corpora = load_corpora()
    assert len(corpora) >= 4
    assert "reagan_berlin_wall_1987" in corpora

    res = sweep_historical_running_keys(min_matches_threshold=10)
    assert res["corpora_count"] >= 4
    assert res["total_offsets_tested"] > 1000
    assert res["best_matches"] < 12  # Below 50% random chance threshold


def test_two_panel_independent_solver_logic() -> None:
    """Verify Two-Panel partition and independent keyword sweep logic."""
    from projects.kryptos.tier2_contextual.two_panel_independent_solver import (
        load_panel_data,
        sweep_two_panel_keywords,
    )

    ct_a, ct_b, cribs_a, cribs_b = load_panel_data()
    assert len(ct_a) == 49
    assert len(ct_b) == 48
    assert len(cribs_a) == 13
    assert len(cribs_b) == 11

    res = sweep_two_panel_keywords(keywords=["KRYPTOS", "BERLIN", "CLOCK"])
    assert res["keywords_tested"] == 3
    assert res["total_evaluations"] == 12


def test_transposed_key_schedule_engine_logic() -> None:
    """Verify transposed keystream matrix formulation and permutation sweep execution."""
    from projects.kryptos.tier2_contextual.transposed_key_schedule_engine import (
        run_transposed_key_sweep,
    )

    res = run_transposed_key_sweep(num_processes=2, keywords=["KRYPTOS", "CLOCK"])
    assert res["keywords_tested"] == 2
    assert res["total_permutations_tested"] == 5040
    assert res["total_anchors"] == 24


def test_desynchronization_audit_engine_logic() -> None:
    """Verify exhaustive null insertion and deletion desynchronization audit."""
    from projects.kryptos.tier2_contextual.desynchronization_audit_engine import (
        run_desynchronization_audit,
    )

    res = run_desynchronization_audit()
    assert res["total_configs_tested"] > 100000
    assert res["total_hits"] == 0  # Proven zero periodic keys L in 1..14


def test_physical_transcriptor_engine_logic() -> None:
    """Verify physical 4x31 inscription routes and tableau row sweep logic."""
    from projects.kryptos.tier2_contextual.physical_transcriptor_engine import (
        analyze_transcription_routes,
        extract_physical_k4_grid,
        sweep_tableau_rows_against_crib1,
    )

    grid = extract_physical_k4_grid()
    assert len(grid["linear"]) == 97
    assert len(grid["columnar"]) == 97

    routes = analyze_transcription_routes()
    assert "linear_standard" in routes
    assert routes["linear_standard"]["lag7_sigma"] > 2.5
    assert routes["columnar_31cols"]["lag7_sigma"] < 1.0  # Lag-7 vanishes under column read

    tab_res = sweep_tableau_rows_against_crib1()
    assert tab_res["total_evaluations"] > 3000
    assert tab_res["best_matches"] < 6


def test_tableau_stencil_engine_logic() -> None:
    """Verify 31-wide tableau geometric trajectory stencil sweep execution."""
    from projects.kryptos.tier2_contextual.tableau_stencil_engine import (
        build_clean_tableau,
        sweep_geometric_slope_stencils,
    )

    tab = build_clean_tableau()
    assert len(tab) == 28
    assert all(len(r) == 31 for r in tab)

    res = sweep_geometric_slope_stencils()
    assert res["total_trajectories_tested"] > 1000000
    assert res["held_out_verified_rules"] == 0


def test_keyword_stencil_engine_logic() -> None:
    """Verify keyword-guided tableau window stencil engine execution."""
    from projects.kryptos.tier2_contextual.keyword_stencil_engine import (
        build_clean_tableau,
        sweep_keyword_stencils,
    )

    tab = build_clean_tableau()
    assert len(tab) == 28
    assert all(len(r) == 31 for r in tab)

    res = sweep_keyword_stencils()
    assert res["total_evaluated"] > 1000000
    assert res["held_out_verified_rules"] == 0


def test_scrambled_strip_reassembly_logic() -> None:
    """Verify scrambled paper strip reassembly engine execution."""
    from projects.kryptos.tier2_contextual.scrambled_strip_reassembly import (
        get_cipher_strips,
        sweep_tableau_strip_permutations,
        sweep_7strip_sliding_displacements,
    )

    strips = get_cipher_strips()
    assert len(strips) == 7
    assert len(strips[0]) == 14
    assert len(strips[6]) == 13

    res_perm = sweep_tableau_strip_permutations()
    assert res_perm["total_permutations_tested"] > 100000
    assert res_perm["held_out_verified"] == 0

    res_slide = sweep_7strip_sliding_displacements()
    assert res_slide["can_form_eastnor_from_strips"] is True


def test_seven_track_autokey_engine_logic() -> None:
    """Verify 7-track dynamic autokey and track progression audit execution."""
    from projects.kryptos.tier2_contextual.seven_track_autokey_engine import (
        run_7track_autokey_audit,
    )

    res = run_7track_autokey_audit()
    assert res["total_evaluated"] > 1000
    assert res["held_out_verified"] == 0


def test_irregular_scheidt_transposition_logic() -> None:
    """Verify 14x7 irregular columnar keystream transposition formulation."""
    from projects.kryptos.tier2_contextual.irregular_scheidt_transposition import (
        generate_14x7_columnar_transposition,
        make_keystream_candidates,
    )

    candidates = make_keystream_candidates()
    assert len(candidates) >= 38
    # Test transposition on identity permutation
    stream = "A" * 97
    trans = generate_14x7_columnar_transposition(stream, tuple(range(7)), null_pos=97, readout_direction="top_down")
    assert len(trans) == 97
    assert trans == "A" * 97


def test_quagmire_dual_keyed_engine_logic() -> None:
    """Verify Quagmire dual-keyed indicator slide engine execution."""
    from projects.kryptos.tier2_contextual.quagmire_dual_keyed_engine import (
        build_alphabet_bank,
        sweep_quagmire_family,
    )

    bank = build_alphabet_bank()
    assert len(bank) >= 38
    res = sweep_quagmire_family()
    assert res["total_evaluated"] > 1000000
    assert res["total_held_out_verified"] == 0


def test_quasigroup_tableau_inverter_logic() -> None:
    """Verify quasigroup / affine ring inversion and columnar injectivity proof."""
    from projects.kryptos.tier2_contextual.quasigroup_tableau_inverter import (
        check_columnar_monoalphabetic_injectivity,
        sweep_affine_ring_models,
    )

    inj = check_columnar_monoalphabetic_injectivity()
    assert inj["is_monoalphabetic_columnar_possible"] is False
    assert inj["num_injectivity_collisions"] >= 2

    aff = sweep_affine_ring_models()
    assert aff["total_evaluated"] > 10000
    assert aff["total_held_out_verified"] == 0


def test_two_key_alternating_engine_logic() -> None:
    """Verify two-key alternating block and track inversion engine execution."""
    from projects.kryptos.tier2_contextual.two_key_alternating_engine import (
        derive_required_key_ints,
        sweep_two_key_alternating_systems,
    )

    req = derive_required_key_ints("standard_vigenere")
    assert len(req) == 24
    res = sweep_two_key_alternating_systems()
    assert res["total_evaluated"] > 10000000
    assert res["held_out_verified"] == 0


def test_strip_sliding_jigsaw_solver_logic() -> None:
    """Verify physical 7-strip plaintext sliding jigsaw solver execution."""
    from projects.kryptos.tier2_contextual.strip_sliding_jigsaw_solver import (
        extract_raw_cipher_strips,
        solve_sliding_strip_jigsaw,
    )

    strips = extract_raw_cipher_strips()
    assert len(strips) == 7
    res = solve_sliding_strip_jigsaw()
    assert res["total_permutations_tested"] == 5040
    assert res["held_out_target2_verified"] == 0


def test_constrained_keystream_annealer_fabric_logic() -> None:
    """Verify multi-core keystream annealer execution on compute fabric."""
    from projects.kryptos.tier2_contextual.constrained_keystream_annealer import (
        run_distributed_keystream_anneal,
    )

    res = run_distributed_keystream_anneal(cores=2, iterations_per_worker=200, duration_per_worker=1.0)
    assert res["total_workers"] >= 2
    assert res["best_q_score"] > -10.0
    # Must preserve exact cribs
    assert res["best_plaintext_sample"][21:34] == "EASTNORTHEAST"
    assert res["best_plaintext_sample"][63:74] == "BERLINCLOCK"


def test_dual_square_superposition_logic() -> None:
    """Verify dual square digraph SMT impossibility and four-square sweep."""
    from projects.kryptos.tier2_contextual.dual_square_superposition_engine import (
        evaluate_dual_square_superposition,
        prove_two_square_impossibility,
    )

    s_res = prove_two_square_impossibility()
    assert s_res["5x5_horizontal"] is False
    assert s_res["7x7_horizontal"] is False
    assert s_res["5x5_vertical"] is False
    assert s_res["7x7_vertical"] is False

    res = evaluate_dual_square_superposition()
    assert res.two_square_sat_5x5 is False
    assert res.two_square_sat_7x7 is False
    assert res.total_four_square_tested > 1000
    assert res.four_square_consistent_keys == 0


def test_keystone_incomplete_grid_logic() -> None:
    """Verify keystone 7x14 column-major grid formulation and sweep execution."""
    from projects.kryptos.tier2_contextual.keystone_incomplete_grid_engine import (
        build_column_major_grid,
        get_column_lengths,
        sweep_keystone_grid,
    )

    lens = get_column_lengths()
    assert len(lens) == 7
    assert sum(lens) == 97

    cols = build_column_major_grid("A" * 97)
    assert len(cols) == 7
    assert len(cols[0]) == 14
    assert len(cols[6]) == 13

    res = sweep_keystone_grid(num_workers=2)
    assert res.total_configs_evaluated > 100000
    assert res.held_out_crib2_hits == 0


def test_paired_sheet_cut_logic() -> None:
    """Verify paired 7x7 sheet route generation and multi-core sweep execution."""
    from projects.kryptos.tier2_contextual.paired_sheet_cut_engine import (
        generate_7x7_routes,
        sweep_paired_sheet_system,
    )

    routes = generate_7x7_routes()
    assert len(routes) >= 8
    assert len(routes["row_major"]) == 49
    assert len(routes["spiral_clockwise"]) == 49

    res = sweep_paired_sheet_system(num_workers=2)
    assert res.total_permutations_tested == 324
    assert res.total_evaluations > 20000
    assert res.held_out_crib2_matches == 0


def test_irregular_mask_grille_logic() -> None:
    """Verify irregular scissors cuts, S-curve contours, and Cardan grille sweep."""
    from projects.kryptos.tier2_contextual.irregular_mask_grille_engine import (
        generate_block_partitions,
        generate_keyed_cardan_grilles,
        generate_sculpture_s_curve_cuts,
        generate_staircase_cuts,
        sweep_irregular_mask_system,
    )

    stair = generate_staircase_cuts()
    assert len(stair) > 10
    assert len(stair[0]) == 49

    sculpt = generate_sculpture_s_curve_cuts()
    assert len(sculpt) > 10

    cardan = generate_keyed_cardan_grilles()
    assert len(cardan) > 10

    res = sweep_irregular_mask_system(num_workers=2)
    assert res.total_permutations_tested > 100
    assert res.total_evaluations > 10000
    assert res.held_out_crib2_matches == 0


def test_solar_shadow_running_key_logic() -> None:
    """Verify solar shadow vector keystreams and expanded running key sweep."""
    from projects.kryptos.tier2_contextual.solar_shadow_running_key_engine import (
        compute_solar_angles,
        generate_solar_keystreams,
        load_all_historical_corpora,
        sweep_solar_shadow_and_running_keys,
    )

    el, az = compute_solar_angles(38.9518, -77.1456, 172, 720)
    assert -90.0 <= el <= 90.0
    assert 0.0 <= az <= 360.0

    streams = generate_solar_keystreams()
    assert len(streams) >= 10
    assert len(streams[0][1]) == 97

    corpora = load_all_historical_corpora()
    assert "tutankhamun_carter_extended" in corpora
    assert "reagan_berlin_wall_1987" in corpora

    res = sweep_solar_shadow_and_running_keys(num_workers=2)
    assert res.total_solar_configs_tested >= 10
    assert res.total_running_key_offsets_tested > 50000
    assert res.held_out_crib2_matches == 0


def test_hill_affine_polygraphic_logic() -> None:
    """Verify 2x2 Hill affine algebra and 7x7 circulant matrix solver."""
    from projects.kryptos.tier2_contextual.hill_affine_polygraphic_engine import (
        solve_2x2_hill_exact,
        solve_7x7_circulant_exact,
        sweep_polygraphic_matrix_engine,
    )

    t_2x2, c1_2x2, c2_2x2 = solve_2x2_hill_exact()
    assert t_2x2 > 50000
    assert c2_2x2 == 0

    t_circ, c1_circ, c2_circ = solve_7x7_circulant_exact()
    assert t_circ >= 4
    assert c2_circ == 0

    res = sweep_polygraphic_matrix_engine()
    assert res.total_evaluations > 50000
    assert res.held_out_crib2_matches == 0


def test_lag7_feedback_recurrence_logic() -> None:
    """Verify lag-7 feedback recurrence and column-stepper evaluation."""
    from projects.kryptos.tier2_contextual.lag7_feedback_recurrence_engine import (
        sweep_lag7_recurrence_system,
    )

    res = sweep_lag7_recurrence_system()
    assert res.total_lfsr_configs_tested > 10000
    assert res.total_evaluations > 10000
    assert res.held_out_crib2_matches == 0


def test_twin_strip_lock_logic() -> None:
    """Verify twin-column strip lock and differential stepper engine."""
    from projects.kryptos.tier2_contextual.twin_strip_lock_engine import (
        sweep_twin_strip_steppers,
    )

    res = sweep_twin_strip_steppers()
    assert res.total_configs_tested > 10000
    assert res.total_evaluations > 10000
    assert res.held_out_crib2_matches == 0


def test_dual_independent_sheet_logic() -> None:
    """Verify dual independent sheet displacement engine."""
    from projects.kryptos.tier2_contextual.dual_independent_sheet_engine import (
        sweep_dual_independent_sheets,
    )

    res = sweep_dual_independent_sheets()
    assert res.total_configs_tested > 10000
    assert res.total_evaluations > 10000
    assert res.held_out_crib2_matches == 0


def test_physical_fold_block_shift_logic() -> None:
    """Verify physical folding and stencil block shift engine."""
    from projects.kryptos.tier2_contextual.physical_fold_block_shift_engine import (
        sweep_physical_folds_and_block_shifts,
    )

    res = sweep_physical_folds_and_block_shifts()
    assert res.total_configs_tested > 10000
    assert res.total_evaluations > 10000
    assert res.held_out_crib2_matches == 0


def test_interlocking_aperture_mask_logic() -> None:
    """Verify 2-phase interlocking aperture mask engine."""
    from projects.kryptos.tier2_contextual.interlocking_aperture_mask_engine import (
        sweep_interlocking_aperture_masks,
    )

    res = sweep_interlocking_aperture_masks()
    assert res.total_configs_tested > 10000
    assert res.total_evaluations > 10000
    assert res.held_out_crib2_matches == 0


def test_keyed_coordinate_selection_logic() -> None:
    """Verify keyed coordinate selection and irregular transposition masking engine."""
    from projects.kryptos.tier2_contextual.keyed_coordinate_selection_engine import (
        sweep_keyed_coordinate_selection,
    )

    res = sweep_keyed_coordinate_selection()
    assert res.total_configs_tested > 10000
    assert res.total_evaluations > 10000
    assert res.held_out_crib2_matches == 0


def test_compound_double_transposition_logic() -> None:
    """Verify compound double-transposition and key schedule inversion engine."""
    from projects.kryptos.tier2_contextual.compound_double_transposition_engine import (
        build_incomplete_col_perm,
        compose_perms,
        invert_perm,
        keyword_to_col_order,
        sweep_compound_double_transposition,
    )

    # 1. Permutation arithmetic verification
    order = keyword_to_col_order("CIPHER")
    assert order == [0, 4, 3, 1, 2, 5]
    perm = build_incomplete_col_perm(97, 6, order)
    assert len(perm) == 97
    assert sorted(perm) == list(range(97))
    inv = invert_perm(perm)
    assert compose_perms(perm, inv) == list(range(97))

    # 2. Sweep execution verification
    res = sweep_compound_double_transposition(max_kw_pairs=10, include_s7_sweep=True, s7_sample_step=5)
    assert res.total_configs_tested > 1000
    assert res.total_evaluations > 10000
    assert res.held_out_crib2_matches == 0


def test_additive_vernier_mask_logic() -> None:
    """Verify additive vernier and dual-layer key mask decomposition engine."""
    from projects.kryptos.tier2_contextual.additive_vernier_mask_engine import (
        sweep_additive_vernier_masks,
    )

    res = sweep_additive_vernier_masks(max_kw_pairs=10)
    assert res.total_configs_tested > 1000
    assert res.total_evaluations > 1000
    assert res.held_out_crib2_matches == 0


def test_vic_straddling_checkerboard_logic() -> None:
    """Verify Cold War VIC cipher and disrupted transposition engine."""
    from projects.kryptos.tier2_contextual.vic_straddling_checkerboard_engine import (
        build_vic_disrupted_perm,
        invert_perm,
        keyword_to_ranks,
        sweep_vic_disrupted_transposition,
    )

    ranks = keyword_to_ranks("KRYPTOS")
    assert ranks == [0, 3, 6, 2, 5, 1, 4]
    perm = build_vic_disrupted_perm(97, 14, 7, ranks, "stepped_triangle")
    assert len(perm) == 97
    assert sorted(perm) == list(range(97))
    inv = invert_perm(perm)
    assert len(inv) == 97

    res = sweep_vic_disrupted_transposition(max_kws=5)
    assert res.total_configs_tested > 100
    assert res.total_evaluations > 1000
    assert res.held_out_crib2_matches == 0


def test_lodestone_geodetic_projection_logic() -> None:
    """Verify Sculpture Lodestone and geodetic bearing vector projection engine."""
    from projects.kryptos.tier2_contextual.lodestone_geodetic_projection_engine import (
        build_ray_trajectory_perm,
        sweep_lodestone_geodetic_engine,
    )

    perm = build_ray_trajectory_perm(14, 7, 67.5)
    assert len(perm) == 98
    assert sorted(perm) == list(range(98))

    res = sweep_lodestone_geodetic_engine(max_kws=5)
    assert res.total_configs_tested > 50
    assert res.total_evaluations > 500
    assert res.held_out_crib2_matches == 0


def test_errata_mixed_alphabet_logic() -> None:
    """Verify K1-K3 errata and mixed-alphabet running key engine."""
    from projects.kryptos.tier2_contextual.errata_mixed_alphabet_engine import (
        build_alphabet_bank,
        make_keyed_alphabet,
        sweep_errata_mixed_alphabet_engine,
    )

    # 1. Keyed alphabet verification
    alpha_iq = make_keyed_alphabet("IQLUSION")
    assert len(alpha_iq) == 26
    assert alpha_iq.startswith("IQLUSON")
    assert sorted(alpha_iq) == sorted("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    bank = build_alphabet_bank()
    assert len(bank) >= 10
    assert "iqlusion" in bank
    assert "desparatly" in bank

    # 2. Fast sweep verification
    res = sweep_errata_mixed_alphabet_engine(max_tokens=3, max_corpora_offsets=10)
    assert res.total_configs_tested > 100
    assert res.total_evaluations > 100
    assert res.held_out_crib2_matches == 0


def test_polygraphic_fractionation_logic() -> None:
    """Verify polygraphic fractionation (Trifid / Bifid) SMT engine and positive control."""
    from projects.kryptos.tier2_contextual.polygraphic_fractionation_engine import (
        run_positive_control,
        sweep_polygraphic_fractionation_engine,
    )

    # 1. Positive control verification: known synthetic Trifid must solve to SAT
    assert run_positive_control() is True

    # 2. Fast sweep verification on K4
    res = sweep_polygraphic_fractionation_engine(max_trifid_l=5, max_bifid_l=4, include_sheet_pairs=False)
    assert res.total_configs_tested > 10
    assert res.held_out_crib2_sat_instances == 0


def test_two_sheet_piecewise_quagmire_logic() -> None:
    """Verify Two-Sheet Piecewise Quagmire engine, positive control, and negative control."""
    from projects.kryptos.tier2_contextual.two_sheet_piecewise_quagmire_engine import (
        run_negative_control,
        run_positive_control,
        sweep_two_sheet_piecewise_quagmire,
    )

    # 1. Positive control: synthetic known two-sheet Quagmire must be recovered
    assert run_positive_control() is True

    # 2. Negative control: scrambled ciphertext must have 0 false alarms
    assert run_negative_control() is True

    # 3. Fast sweep verification on K4
    res = sweep_two_sheet_piecewise_quagmire(max_null_positions=3, max_kws=3)
    assert res.total_configs_tested > 100
    assert res.held_out_crib_matches == 0


def test_restricted_coordinate_transposition_logic() -> None:
    """Verify Restricted Coordinate Transposition engine, K3 synthetic positive control, and negative control."""
    from projects.kryptos.tier2_contextual.restricted_coordinate_transposition_engine import (
        run_negative_control,
        run_positive_control,
        sweep_restricted_coordinate_transposition,
    )

    # 1. Positive control: synthetic known K3 coordinate transposition must be recovered
    assert run_positive_control() is True

    # 2. Negative control: scrambled ciphertext must have 0 false alarms
    assert run_negative_control() is True

    # 3. Fast sweep verification on K4
    res = sweep_restricted_coordinate_transposition(max_null_positions=1, max_band_sample=2)
    assert res.total_configs_tested > 100
    assert res.held_out_crib_matches == 0


def test_unconstrained_s7_transposition_logic() -> None:
    """Verify Unconstrained S7 Columnar Transposition engine, positive control, and negative control."""
    from projects.kryptos.tier2_contextual.unconstrained_s7_transposition_engine import (
        run_negative_control,
        run_positive_control,
        sweep_unconstrained_s7_transposition,
    )

    # 1. Positive control: synthetic known unconstrained S7 transposition must be recovered
    assert run_positive_control() is True

    # 2. Negative control: scrambled ciphertext must have 0 false alarms
    assert run_negative_control() is True

    # 3. Fast sweep verification on K4
    res = sweep_unconstrained_s7_transposition(max_null_positions=1, max_perms=10, num_processes=1)
    assert res.total_configs_tested >= 10
    assert res.held_out_crib_matches == 0


def test_stateful_progressive_autokey_logic() -> None:
    """Verify 7-Channel Stateful Progressive Autokey engine, positive control, and negative control."""
    from projects.kryptos.tier2_contextual.stateful_progressive_autokey_engine import (
        run_negative_control,
        run_positive_control,
        sweep_stateful_progressive_autokey,
    )

    # 1. Positive control: synthetic known 7-channel CTAK must be recovered 100%
    assert run_positive_control() is True

    # 2. Negative control: scrambled ciphertext must produce 0 false alarms
    assert run_negative_control() is True

    # 3. Fast sweep verification on K4
    res = sweep_stateful_progressive_autokey(max_null_positions=1, num_processes=1, routes=["row_major"])
    assert res.total_configs_tested > 100
    assert res.held_out_crib_matches == 0


def test_multi_null_defect_topology_logic() -> None:
    """Verify Multi-Null Defect Topology engine, positive control, and negative control."""
    from projects.kryptos.tier2_contextual.multi_null_defect_topology_engine import (
        run_negative_control,
        run_positive_control,
        sweep_multi_null_defect_topology,
    )

    # 1. Positive control: synthetic known 10x10 3-null cipher must be recovered 100%
    assert run_positive_control() is True

    # 2. Negative control: scrambled ciphertext must produce 0 false alarms
    assert run_negative_control() is True

    # 3. Fast sweep verification on K4
    res = sweep_multi_null_defect_topology(max_10x10_triplets=5, max_14x7_pairs=5, num_processes=1)
    assert res.total_configs_tested > 10
    assert res.held_out_crib_matches == 0


def test_error_tolerant_artisanal_smt_logic() -> None:
    """Verify Error-Tolerant Artisanal SMT engine, positive control, and negative control."""
    from projects.kryptos.tier2_contextual.error_tolerant_artisanal_smt_engine import (
        run_negative_control,
        run_positive_control,
        sweep_error_tolerant_artisanal_smt,
    )

    # 1. Positive control: synthetic 2-stage cipher with 1 defect recovered with >= 16/18 and 6/6 held-out
    assert run_positive_control() is True

    # 2. Negative control: scrambled ciphertext produces 0 false alarms (0 candidates with >= 16/18)
    assert run_negative_control() is True

    # 3. Fast sweep verification on K4
    res = sweep_error_tolerant_artisanal_smt(max_null_positions=1, max_perms=10, num_processes=1)
    assert res.total_configs_tested > 10
    assert res.held_out_crib_matches == 0





















