# 2026-08-17 Hyperliquid perpetual measurement adapter

Change type: Add official indicator-only perpetual DEX measurement source and shared POST-body transport support

Affected files: `config/measurement_sources.json`, shared HTTP transport, measurement schema/adapter, and tests.

Human confirmed: yes

Risk level: medium

Mother Brain activated: yes

Rollback note: Revert this change if POST-body support weakens URL/redirect policy, Hyperliquid response parsing drifts, or perpetual measurements appear in Major/Potential news slots. The adapter is isolated inside the existing measurement registry.

## Decision

The formal Crypto matrix still lacks Perp DEX volume, OI and funding. Hyperliquid's official public API documents `POST https://api.hyperliquid.xyz/info` and `metaAndAssetCtxs`, which provides current funding and open interest alongside market context. The shared HTTP transport gains a bounded POST body rather than bypassing the repository's SSRF and redirect validation. The resulting measurements remain `indicator_only`.
