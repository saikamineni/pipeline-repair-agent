# pipeline-repair-agent conventions
- Plain functions only. No classes, no config files, no logging frameworks.
- Entire pipeline (extract+transform+load) under ~100 lines total.
- Data generation MUST be seeded (np.random.default_rng(42)) — reproducibility is load-bearing.
- Schemas in pipeline/schema.py are the ground truth; build them first.
- Dirt lives in the data, never in the code.
- Never edit files under tests/ or evals/.