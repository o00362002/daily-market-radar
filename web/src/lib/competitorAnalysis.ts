export type CompetitorAnalysisProjection = {
  overlapLevel: 'high' | 'medium' | 'low';
  actionLoopOverlap: string[];
  affectedProductLayers: string[];
  threatTypes: string[];
  relevanceToRetailOps: string;
  currentDifferentiationStatus: string;
  recommendedAction: string;
  evidenceLinks: { sourceId: string; title: string; url: string }[];
};

type Lens = { id: string; label: string; terms: string[] };

const ACTION_LOOP_LENSES: Lens[] = [
  {
    id: 'operational_signal_or_instruction',
    label: '營運訊號／指令',
    terms: ['signal', 'data', 'forecast', 'instruction', 'message', 'predict', '營運訊號', '數據', '預測', '指令'],
  },
  {
    id: 'prioritized_action',
    label: '優先行動',
    terms: ['prioritized', 'action', 'mission', 'recommendation', 'coaching', 'task', '優先', '行動', '任務', '建議', '教練'],
  },
  {
    id: 'assignment_and_follow_up',
    label: '指派／追蹤',
    terms: ['assignment', 'follow-up', 'follow up', 'orchestration', 'reprioritization', 'escalation', '指派', '追蹤', '催辦', '協作', '升級'],
  },
  {
    id: 'evidence_and_review',
    label: '證據／覆核',
    terms: ['evidence', 'verification', 'proof', 'audit', 'review', 'photo', '驗證', '證據', '稽核', '覆核', '照片'],
  },
  {
    id: 'outcome_measurement',
    label: 'Outcome 量測',
    terms: ['outcome', 'impact', 'measurement', 'reporting', 'performance', 'roi', '結果', '成效', '量測', '報表', '投報'],
  },
  {
    id: 'rule_or_workflow_improvement',
    label: '規則／流程改善',
    terms: ['best practice', 'learning', 'workflow', 'sop', 'self-service', 'modular', '最佳實務', '學習', '工作流', '流程', '模組'],
  },
];

const PRODUCT_LAYER_LENSES: Lens[] = [
  {
    id: 'free_entry',
    label: '免費入口',
    terms: ['free plan', 'free tier', 'freemium', '免費方案', '免費版'],
  },
  {
    id: 'template_subscription',
    label: '模板／訂閱',
    terms: ['template', 'checklist', 'sop', 'workflow', 'task management', '模板', '檢核表', '工作流', '任務管理'],
  },
  {
    id: 'decision_module',
    label: '決策模組',
    terms: ['forecast', 'recommendation', 'decision', 'analytics', 'prioritized', '預測', '建議', '決策', '分析', '優先'],
  },
  {
    id: 'agent',
    label: 'Agent',
    terms: ['ai', 'agent', 'copilot', 'autonomous', 'coaching', '人工智慧', '智慧代理', '自主', '教練'],
  },
  {
    id: 'private_integration',
    label: '私有整合',
    terms: ['integration', 'cross-system', 'headless', 'mcp', 'api', 'erp', 'pos', '整合', '跨系統', '介接'],
  },
];

const containsAny = (text: string, terms: string[]) => terms.some((term) => text.includes(term.toLowerCase()));
const matchedLabels = (text: string, lenses: Lens[]) => lenses.filter((lens) => containsAny(text, lens.terms)).map((lens) => lens.label);

const sourceCorpus = (entry: any, check: any) => {
  const parts = [entry?.focus ?? ''];
  for (const source of check?.source_checks ?? []) {
    if (source?.status === 'failed') continue;
    parts.push(source?.title ?? '', source?.excerpt ?? '');
  }
  return parts.join(' ').toLowerCase();
};

const overlapLevel = (entry: any, actionLoopOverlap: string[]) => {
  const count = actionLoopOverlap.length;
  if (count >= 4 || (entry?.relationship === 'direct' && count >= 3)) return 'high' as const;
  if (count >= 2 || entry?.relationship === 'direct' || entry?.priority === 'high') return 'medium' as const;
  return 'low' as const;
};

const threatTypes = (entry: any, corpus: string, overlap: 'high' | 'medium' | 'low') => {
  const values = new Set<string>();
  if (entry?.relationship === 'direct' || overlap === 'high') values.add('功能替代');
  if (entry?.relationship === 'enabling') values.add('生態系優勢');
  if (entry?.market === 'taiwan') values.add('在地資料優勢');
  if (containsAny(corpus, ['integration', 'workflow', 'mcp', 'api', 'headless', '整合', '工作流', '介接'])) values.add('實作速度');
  if (containsAny(corpus, ['platform', 'ecosystem', 'commerce', 'pos', '平台', '生態系'])) values.add('通路／分發控制');
  if (containsAny(corpus, ['free', 'freemium', 'low cost', 'price', '免費', '低價', '價格'])) values.add('價格壓縮');
  return [...values];
};

const differentiationStatus = (entry: any, overlap: 'high' | 'medium' | 'low', changed: boolean) => {
  if (overlap === 'high') {
    return changed
      ? 'Action Layer 重疊高，且官方材料今天出現變化；需重新核對其閉環能力是否跨過現有差異邊界。'
      : 'Action Layer 重疊高；今天未見重大官方材料變化，差異仍需用資料接入、閉環成效與台灣落地深度驗證。';
  }
  if (overlap === 'medium') {
    return changed
      ? '目前屬部分重疊，但官方材料已有變化；重點看是否從既有資料／工作流優勢往 Action 閉環延伸。'
      : '目前屬部分重疊，主要壓力來自既有資料、工作流或通路生態，尚未驗證完整 Action 閉環替代。';
  }
  return changed
    ? '目前重疊低但出現新材料；先確認是否只是相鄰功能，避免把一般產品更新誤判成直接競爭。'
    : '目前重疊低，維持相鄰能力監測；沒有足夠證據把它升級成直接替代威脅。';
};

const recommendedAction = (overlap: 'high' | 'medium' | 'low', changed: boolean) => {
  if (overlap === 'high' && changed) return '優先拆解本次官方變化，逐項對照 Action→追蹤→證據→Outcome→改善閉環，確認是否需調整產品優先級。';
  if (overlap === 'high') return '維持高優先 benchmark；不因今天無新聞改策略，持續追蹤官方功能、客戶案例、定價與可驗證 Outcome。';
  if (overlap === 'medium' && changed) return '檢查新材料是否跨入任務執行、覆核或 Outcome；只有跨層時才升級競爭優先級。';
  if (overlap === 'medium') return '維持月度比較，重點監測它是否利用既有資料或通路優勢向執行閉環擴張。';
  return '保留低成本監測；只有出現可驗證的 RetailOps Action 閉環或台灣落地證據時才升級。';
};

export const buildCompetitorAnalysis = (entry: any, check: any): CompetitorAnalysisProjection => {
  const corpus = sourceCorpus(entry, check);
  const actionLoopOverlap = matchedLabels(corpus, ACTION_LOOP_LENSES);
  const affectedProductLayers = matchedLabels(corpus, PRODUCT_LAYER_LENSES);
  const overlap = overlapLevel(entry, actionLoopOverlap);
  const evidenceLinks = (check?.source_checks ?? [])
    .filter((source: any) => source?.url)
    .map((source: any) => ({
      sourceId: source.source_id,
      title: source.title || source.source_id,
      url: source.url,
    }));

  return {
    overlapLevel: overlap,
    actionLoopOverlap,
    affectedProductLayers,
    threatTypes: threatTypes(entry, corpus, overlap),
    relevanceToRetailOps: entry?.focus ?? '尚未建立 RetailOps 關聯描述。',
    currentDifferentiationStatus: differentiationStatus(entry, overlap, Boolean(check?.fresh_material_delta)),
    recommendedAction: recommendedAction(overlap, Boolean(check?.fresh_material_delta)),
    evidenceLinks,
  };
};
