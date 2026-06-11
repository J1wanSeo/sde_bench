# Extending SDE-Bench

The current alpha keeps metric functions in `src/sde_bench/core.py` to make the
public API compact. New metrics should follow this contract:

```python
def my_axis(real, synthetic, source=None, target=None):
    return {
        "score": 0.0,      # bounded [0, 1]
        "metrics": {},     # raw interpretable values
    }
```

Rules:

1. Keep support counts in `metrics`, but do not include them in axis scores.
2. Emit skipped metrics when required inputs are unavailable.
3. Prefer raw metric reporting over a single summary claim.
4. Keep specialty-specific metrics optional unless they are part of
   `clinical_groundedness` or `clinical_validity`.

Planned modules:

- TSTR/TRTR clinical task utility
- membership inference risk
- attribute disclosure risk
- semantic evidence support via embeddings or judge models
- clinical rule packs by specialty
