# Structured measurements

`config/source_registry.json` owns daily news/discovery collection. `config/measurement_sources.json` owns fixed structured datasets used by deterministic matrices and structural indicators.

Measurement adapters emit canonical `Document` objects with `lane=indicator_only`. These events remain available to fixed matrices and structural indicators, but cannot become Major/Potential news cards or Potential signals merely because a metric changed. They use the normal event-resolution and delta machinery and do not create a separate report or state pipeline.

Current formal measurement sources:

- BLS nonfarm-business productivity, real hourly compensation, and labor-share year-over-year series. The aligned series are emitted as one event so one release cannot fan out into several independent structural votes.
- DefiLlama Hyperliquid TVL, 24-hour fees, and 24-hour revenue. These fill `crypto_matrix.tvl_fees_revenue`; Perp OI/funding remains a separate gap and is not inferred.

A failed dataset is disclosed through source audit, coverage gaps, and remaining gaps. Missing measurements are never estimated.
