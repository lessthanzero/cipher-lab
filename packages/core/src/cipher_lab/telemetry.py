"""Darwin memory-safe telemetry, CPU stress guardrails, and token budget governance."""

from __future__ import annotations

import os
import subprocess
import time
from typing import Tuple


def get_darwin_available_memory_gb() -> float:
    """Calculate true available RAM on macOS accounting for cache reclaiming."""
    page_size = 16384  # 16 KB default on Apple Silicon Darwin
    try:
        vm = subprocess.check_output(["vm_stat"], text=True)
        free_p = inactive_p = purge_p = spec_p = 0
        for line in vm.splitlines():
            if "Pages free:" in line:
                free_p = int(line.split(":")[1].strip().rstrip("."))
            elif "Pages inactive:" in line:
                inactive_p = int(line.split(":")[1].strip().rstrip("."))
            elif "Pages purgeable:" in line:
                purge_p = int(line.split(":")[1].strip().rstrip("."))
            elif "Pages speculative:" in line:
                spec_p = int(line.split(":")[1].strip().rstrip("."))
        avail_bytes = (free_p + spec_p + inactive_p + purge_p) * page_size
        return avail_bytes / (1024 ** 3)
    except Exception:
        return 4.0


def get_normalized_cpu_load() -> float:
    """Return 1-minute load average normalized by CPU core count."""
    try:
        cores = os.cpu_count() or 1
        load = os.getloadavg()[0]
        return load / cores
    except Exception:
        return 0.5


class TelemetryGuard:
    """Monitors system resource pressure and enforces cooperative cooldown and token caps."""

    def __init__(
        self,
        min_available_ram_gb: float = 2.0,
        max_cpu_load: float = 1.20,
        cooldown_secs: float = 4.0,
        max_token_budget: int = 50000,
    ) -> None:
        self.min_ram_gb = min_available_ram_gb
        self.max_cpu_load = max_cpu_load
        self.cooldown_secs = cooldown_secs
        self.max_token_budget = max_token_budget
        self.accumulated_tokens = 0

    def check_health_and_cooldown(self) -> Tuple[bool, str]:
        """Check system state; sleeps cooperatively if CPU is high; halts if RAM is critical."""
        avail_ram = get_darwin_available_memory_gb()
        if avail_ram < self.min_ram_gb:
            return False, f"CRITICAL: Available RAM ({avail_ram:.2f} GB) < {self.min_ram_gb} GB. Throttling."

        norm_load = get_normalized_cpu_load()
        if norm_load > self.max_cpu_load:
            # Cooperative sleep to allow Mac to breathe
            time.sleep(self.cooldown_secs)
            return True, f"COOLDOWN: CPU load ({norm_load:.2f}) > {self.max_cpu_load:.2f}. Slept {self.cooldown_secs}s."

        return True, "HEALTHY"

    def can_invoke_model(self, estimated_tokens: int = 500) -> bool:
        """Check if model call stays within token and memory safety bounds."""
        if self.accumulated_tokens + estimated_tokens > self.max_token_budget:
            return False
        avail_ram = get_darwin_available_memory_gb()
        return avail_ram >= self.min_ram_gb

    def record_tokens(self, tokens: int) -> None:
        """Accumulate token count for the active run."""
        self.accumulated_tokens += tokens
