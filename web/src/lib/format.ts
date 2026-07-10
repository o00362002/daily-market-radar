// Evidence-quality and provenance badges. Every badge pairs a text label with a
// symbol so meaning never relies on colour alone (accessibility requirement).

export interface Badge {
  label: string;
  symbol: string;
  kind: string;
}

export const EVIDENCE_BADGES: Record<string, Badge> = {
  fact: { label: '事實 Fact', symbol: '◆', kind: 'fact' },
  inference: { label: '推論 Inference', symbol: '≈', kind: 'inference' },
  counterevidence: { label: '反證 Counterevidence', symbol: '⚑', kind: 'counter' },
  uncertainty: { label: '不確定 Uncertainty', symbol: '?', kind: 'uncertainty' },
  gap: { label: '缺口 Gap', symbol: '▽', kind: 'gap' },
};

export function evaluationBadge(mode: string): Badge {
  switch (mode) {
    case 'api-assisted':
      return { label: 'API 加強 API-assisted', symbol: '⚙', kind: 'api' };
    case 'chat-assisted':
      return { label: '對話加強 Chat-assisted', symbol: '✎', kind: 'chat' };
    case 'auto':
      return { label: '自動 Auto', symbol: '⟳', kind: 'auto' };
    default:
      return { label: '確定性 Deterministic', symbol: '=', kind: 'deterministic' };
  }
}

export function statusBadge(status: string): Badge {
  switch (status) {
    case 'complete':
      return { label: '完整 Complete', symbol: '●', kind: 'complete' };
    case 'failed':
      return { label: '失敗 Failed', symbol: '✕', kind: 'failed' };
    default:
      return { label: '部分 Partial', symbol: '◐', kind: 'partial' };
  }
}

export function fixtureBadge(isFixture: boolean): Badge | null {
  return isFixture ? { label: '示例資料 Fixture', symbol: '⚠', kind: 'fixture' } : null;
}

export function sparklinePath(values: number[], width = 120, height = 28): string {
  if (values.length === 0) return '';
  const max = Math.max(...values, 1);
  const step = values.length > 1 ? width / (values.length - 1) : 0;
  return values
    .map((value, index) => {
      const x = Math.round(index * step);
      const y = Math.round(height - (value / max) * height);
      return `${index === 0 ? 'M' : 'L'}${x},${y}`;
    })
    .join(' ');
}
