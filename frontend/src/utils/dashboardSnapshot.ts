export type StageSnapshotKey =
  | 'rh_latest_infertility_result'
  | 'rh_latest_pregnancy_result'
  | 'rh_latest_postpartum_result'

export type StageSnapshot = {
  riskLevel: string
  score: number
  summary: string
  modelVersion?: string
  capturedAt: string
}

export const SNAPSHOT_KEYS: Record<'infertility' | 'pregnancy' | 'postpartum', StageSnapshotKey> = {
  infertility: 'rh_latest_infertility_result',
  pregnancy: 'rh_latest_pregnancy_result',
  postpartum: 'rh_latest_postpartum_result',
}

export function readStageSnapshot(key: StageSnapshotKey): StageSnapshot | null {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) {
      return null
    }

    const parsed = JSON.parse(raw) as Partial<StageSnapshot>
    if (
      typeof parsed.riskLevel !== 'string' ||
      typeof parsed.score !== 'number' ||
      typeof parsed.summary !== 'string' ||
      typeof parsed.capturedAt !== 'string'
    ) {
      return null
    }

    return {
      riskLevel: parsed.riskLevel,
      score: parsed.score,
      summary: parsed.summary,
      capturedAt: parsed.capturedAt,
      modelVersion: typeof parsed.modelVersion === 'string' ? parsed.modelVersion : undefined,
    }
  } catch {
    return null
  }
}

export function writeStageSnapshot(key: StageSnapshotKey, snapshot: StageSnapshot): void {
  try {
    localStorage.setItem(key, JSON.stringify(snapshot))
  } catch {
    // Ignore storage write failures.
  }
}
