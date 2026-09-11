from cipher_lab.telemetry import (
    TelemetryGuard,
    get_darwin_available_memory_gb,
    get_normalized_cpu_load,
)


def test_darwin_memory_calculation():
    avail_gb = get_darwin_available_memory_gb()
    # On macOS Apple Silicon with 16GB+ RAM, true available should comfortably exceed 2 GB
    assert avail_gb >= 1.0

def test_normalized_cpu_load():
    norm_load = get_normalized_cpu_load()
    assert norm_load >= 0.0

def test_telemetry_token_budget():
    guard = TelemetryGuard(max_token_budget=1000)
    assert guard.can_invoke_model(500) is True
    guard.record_tokens(800)
    assert guard.can_invoke_model(500) is False
