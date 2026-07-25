# Pages deployment trigger execution check

## Intent

Ensure relevant `main` changes run the same accepted production pipeline as the scheduled daily workflow, so merged competitor and web changes do not remain invisible until the next schedule.

## Required checks

- workflow parses in GitHub Actions
- runtime-check
- mount-check
- web-check
- single-owner-check
- contract test confirms `main` push paths
- production report and AI gates remain unchanged
- rejected runs preserve the previous public site

## Post-merge verification

The merge commit must trigger `daily-intelligence` through the workflow-file path. Deployment is successful only if the intelligence job, production gate, Pages build and deploy job all succeed. The public competitors page must no longer show the old `台灣產品競品 Taiwan Products` heading.
