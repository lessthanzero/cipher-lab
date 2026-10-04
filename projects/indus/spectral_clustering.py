"""Spectral graph decomposition and unsupervised functional clustering of the Indus signary."""

from __future__ import annotations

import collections
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Counter, Dict, List, Sequence, Tuple

import numpy as np
import scipy.cluster.vq as vq
import scipy.linalg as la

from projects.indus.concordance import IndusConcordance
from projects.indus.corpus import IndusCorpus


@dataclass(frozen=True, slots=True)
class FunctionalSignClass:
    class_id: int
    name: str
    description: str
    member_signs: tuple[str, ...]
    top_signs: tuple[str, ...]
    mean_position: float
    terminal_ratio: float
    initial_ratio: float


@dataclass(frozen=True, slots=True)
class SpectralDecompositionResult:
    n_signs: int
    n_classes: int
    eigenvalues: list[float]
    eigengap_index: int
    classes: list[FunctionalSignClass]
    sign_to_class: dict[str, int]
    class_transition_matrix: list[list[float]]
    dag_feedforward_ratio: float


class IndusSpectralClusterer:
    """Discovers latent functional sign categories using spectral graph theory and positional embeddings."""

    def __init__(self, corpus: IndusCorpus, target_catalog: str = "parpola") -> None:
        self.corpus = corpus
        self.catalog = target_catalog
        self.sequences = self.corpus.get_sequences(target_catalog=self.catalog)
        self.concordance = self.corpus.concordance

        # Extract unique signs sorted by frequency
        token_counts = collections.Counter(s for seq in self.sequences for s in seq)
        self.signs = [s for s, _ in token_counts.most_common()]
        self.sign_to_idx = {s: i for i, s in enumerate(self.signs)}
        self.n_signs = len(self.signs)

    def build_affinity_matrix(self) -> np.ndarray:
        """Construct symmetric affinity matrix W combining bigram transitions and positional overlap."""
        # 1. Bigram co-occurrence matrix
        bigram_counts = np.zeros((self.n_signs, self.n_signs), dtype=np.float64)
        for seq in self.sequences:
            for i in range(len(seq) - 1):
                idx1 = self.sign_to_idx[seq[i]]
                idx2 = self.sign_to_idx[seq[i + 1]]
                bigram_counts[idx1, idx2] += 1.0

        # Symmetrize bigrams: co-occurrence within 2-sign window
        cooccurrence = bigram_counts + bigram_counts.T

        # 2. Positional distribution profile matrix
        # Each sign gets a vector of its relative occurrence across slots 0..5+
        max_pos = 6
        pos_matrix = np.zeros((self.n_signs, max_pos), dtype=np.float64)
        for seq in self.sequences:
            for p, sign in enumerate(seq):
                idx = self.sign_to_idx[sign]
                slot = min(p, max_pos - 1)
                pos_matrix[idx, slot] += 1.0

        # Normalize positional vectors to unit length
        row_sums = pos_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        pos_norm = pos_matrix / row_sums

        # Positional cosine similarity
        pos_sim = np.dot(pos_norm, pos_norm.T)

        # 3. Combined affinity matrix with self-loops removed
        affinity = 0.5 * (cooccurrence / (cooccurrence.max() + 1e-6)) + 0.5 * pos_sim
        np.fill_diagonal(affinity, 0.0)

        # Ensure non-negative and symmetric
        affinity = np.maximum(affinity, 0.0)
        affinity = 0.5 * (affinity + affinity.T)
        return affinity

    def decompose(self, n_clusters: int = 5, seed: int = 42) -> SpectralDecompositionResult:
        """Execute normalized spectral clustering via the Shi-Malik symmetric graph Laplacian."""
        W = self.build_affinity_matrix()
        
        # Degree matrix D
        deg = W.sum(axis=1)
        # Avoid division by zero for isolated signs
        deg_inv_sqrt = np.zeros_like(deg)
        nonzero = deg > 0
        deg_inv_sqrt[nonzero] = 1.0 / np.sqrt(deg[nonzero])
        D_inv_sqrt = np.diag(deg_inv_sqrt)

        # Normalized symmetric Laplacian L_sym = I - D^{-1/2} W D^{-1/2}
        L_sym = np.eye(self.n_signs) - D_inv_sqrt @ W @ D_inv_sqrt

        # Solve generalized eigenvalue problem: find smallest eigenvalues of L_sym
        eigenvalues, eigenvectors = la.eigh(L_sym)

        # Sort ascending
        idx_sorted = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[idx_sorted]
        eigenvectors = eigenvectors[:, idx_sorted]

        # Calculate eigengaps: delta_k = lambda_{k+1} - lambda_k
        gaps = np.diff(eigenvalues[:12])
        best_gap_idx = int(np.argmax(gaps)) + 1 if len(gaps) > 0 else n_clusters

        # Select first k eigenvectors
        k = n_clusters
        U = eigenvectors[:, :k]

        # Row-normalize U to unit length
        U_norm = np.linalg.norm(U, axis=1, keepdims=True)
        U_norm[U_norm == 0] = 1.0
        T = U / U_norm

        # Cluster rows of T via k-means with multiple restarts
        np.random.seed(seed)
        best_centroids = None
        best_distortion = float("inf")
        for _ in range(20):
            try:
                centroids, dist = vq.kmeans(T, k, iter=30)
                if dist < best_distortion:
                    best_distortion = dist
                    best_centroids = centroids
            except Exception:
                continue

        if best_centroids is None:
            # Fallback
            best_centroids, _ = vq.kmeans(T, k, iter=30)

        labels, _ = vq.vq(T, best_centroids)
        sign_to_class = {self.signs[i]: int(labels[i]) for i in range(self.n_signs)}

        # Profile and label each cluster
        clusters_list: list[FunctionalSignClass] = []
        for c_id in range(k):
            member_signs = [self.signs[i] for i in range(self.n_signs) if labels[i] == c_id]
            
            # Compute positional statistics for this cluster
            all_positions = []
            init_count = 0
            term_count = 0
            total_occurrences = 0

            for seq in self.sequences:
                for p, s in enumerate(seq):
                    if s in member_signs:
                        all_positions.append(p)
                        total_occurrences += 1
                        if p == 0:
                            init_count += 1
                        if p == len(seq) - 1:
                            term_count += 1

            mean_pos = float(np.mean(all_positions)) if all_positions else 0.0
            init_ratio = (init_count / total_occurrences) if total_occurrences > 0 else 0.0
            term_ratio = (term_count / total_occurrences) if total_occurrences > 0 else 0.0

            # Rank member signs by corpus occurrence
            token_counts = collections.Counter(s for seq in self.sequences for s in seq)
            member_signs_ranked = sorted(member_signs, key=lambda s: token_counts[s], reverse=True)
            top_signs = tuple(member_signs_ranked[:8])

            # Functional naming heuristic
            if term_ratio > 0.40 or any(s in ("P324", "M342") for s in top_signs):
                name = "TERMINAL_SINK"
                desc = "Boundary terminal signs; concentrated in final slot (e.g. Classic Jar P324/M342)"
            elif init_ratio > 0.35:
                name = "INITIAL_PREFIX"
                desc = "Prefix and seal-owner identity markers; concentrated at inscription onset"
            elif any(s in ("P011", "P012", "P013", "M011", "M012", "M013") for s in top_signs):
                name = "NUMERAL_QUANTIFIER"
                desc = "Stroke numeral and tally markers; concentrated in penultimate slot"
            elif mean_pos > 2.5:
                name = "PRE_TERMINAL_MODIFIER"
                desc = "Pre-terminal connective signs binding commodities to terminal sinks"
            else:
                name = "COMMODITY_CORE"
                desc = "High-diversity medial signs; core commodity and lineage attributes"

            clusters_list.append(FunctionalSignClass(
                class_id=c_id,
                name=name,
                description=desc,
                member_signs=tuple(member_signs_ranked),
                top_signs=top_signs,
                mean_position=round(mean_pos, 2),
                terminal_ratio=round(term_ratio, 3),
                initial_ratio=round(init_ratio, 3),
            ))

        # Sort clusters by mean positional sequence
        clusters_list = sorted(clusters_list, key=lambda c: c.mean_position)

        # Re-index class IDs by chronological slot order
        reindexed_classes = []
        old_to_new_id = {}
        for new_id, c in enumerate(clusters_list):
            old_to_new_id[c.class_id] = new_id
            reindexed_classes.append(FunctionalSignClass(
                class_id=new_id,
                name=c.name,
                description=c.description,
                member_signs=c.member_signs,
                top_signs=c.top_signs,
                mean_position=c.mean_position,
                terminal_ratio=c.terminal_ratio,
                initial_ratio=c.initial_ratio,
            ))

        new_sign_to_class = {s: old_to_new_id[sign_to_class[s]] for s in self.signs}

        # Calculate class-to-class transition probability matrix
        trans_counts = np.zeros((k, k), dtype=np.float64)
        for seq in self.sequences:
            for i in range(len(seq) - 1):
                c1 = new_sign_to_class[seq[i]]
                c2 = new_sign_to_class[seq[i + 1]]
                trans_counts[c1, c2] += 1.0

        # Row-normalize to transition probabilities
        row_sums = trans_counts.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        class_trans_matrix = trans_counts / row_sums

        # Compute Directed Acyclic Graph (DAG) feed-forward ratio
        # A feed-forward syntax moves forward (c2 >= c1) rather than backward loops (c2 < c1)
        forward_transitions = np.sum(np.triu(trans_counts))
        total_transitions = np.sum(trans_counts)
        feedforward_ratio = float(forward_transitions / max(total_transitions, 1.0))

        return SpectralDecompositionResult(
            n_signs=self.n_signs,
            n_classes=k,
            eigenvalues=[round(float(e), 4) for e in eigenvalues[:12]],
            eigengap_index=best_gap_idx,
            classes=reindexed_classes,
            sign_to_class=new_sign_to_class,
            class_transition_matrix=[[round(float(v), 3) for v in row] for row in class_trans_matrix],
            dag_feedforward_ratio=round(feedforward_ratio, 3),
        )
