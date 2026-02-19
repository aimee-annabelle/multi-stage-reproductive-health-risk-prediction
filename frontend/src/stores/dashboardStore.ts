import { create } from 'zustand'

export type HealthStage = 'infertility' | 'pregnancy' | 'postpartum'

type StageFormValues = Record<HealthStage, Record<string, string>>

type AssessmentResult = {
  riskLabel: 'Low Risk' | 'Moderate Risk' | 'High Risk'
  score: number
  summary: string
  recommendations: string[]
}

type DashboardState = {
  selectedStage: HealthStage
  formValues: StageFormValues
  result: AssessmentResult | null
  setStage: (stage: HealthStage) => void
  setField: (field: string, value: string) => void
  assessRisk: () => void
  resetAssessment: () => void
}

const initialFormValues: StageFormValues = {
  infertility: {
    cycleLength: '28',
    periodLength: '5',
    basalTemp: '98.2',
    lhLevel: '14',
    symptoms: '',
  },
  pregnancy: {
    currentWeek: 'Week 1-40',
    systolicBP: '120',
    diastolicBP: '80',
    symptoms: '',
  },
  postpartum: {
    weeksPostpartum: '6',
    sleepHours: '7',
    moodScore: '8',
    symptoms: '',
  },
}

function calculateRisk(stage: HealthStage, values: Record<string, string>): AssessmentResult {
  let score = 20
  const symptoms = values.symptoms || ''
  const symptomCount = symptoms
    .split(',')
    .map((entry) => entry.trim())
    .filter(Boolean).length

  score += Math.min(symptomCount * 8, 30)

  if (stage === 'pregnancy') {
    const systolic = Number(values.systolicBP || '0')
    const diastolic = Number(values.diastolicBP || '0')
    if (systolic >= 140 || diastolic >= 90) score += 35
    else if (systolic >= 130 || diastolic >= 85) score += 20
    score += 8
  }

  if (stage === 'infertility') {
    const cycleLength = Number(values.cycleLength || '0')
    const periodLength = Number(values.periodLength || '0')
    const lhLevel = Number(values.lhLevel || '0')
    if (cycleLength && (cycleLength < 24 || cycleLength > 35)) score += 16
    if (periodLength && (periodLength < 3 || periodLength > 7)) score += 12
    if (lhLevel && (lhLevel < 8 || lhLevel > 24)) score += 10
  }

  if (stage === 'postpartum') {
    const sleepHours = Number(values.sleepHours || '0')
    const moodScore = Number(values.moodScore || '0')
    if (sleepHours && sleepHours < 6) score += 16
    if (moodScore && moodScore < 5) score += 12
    score += 4
  }

  score = Math.max(0, Math.min(100, score))

  if (score >= 70) {
    return {
      riskLabel: 'High Risk',
      score,
      summary: 'Immediate clinician review recommended based on current vitals and symptom load.',
      recommendations: [
        'Contact your care provider today for immediate guidance.',
        'Track blood pressure 2-3 times daily until symptoms stabilize.',
        'Avoid missing prescribed medication and hydration schedule.',
      ],
    }
  }

  if (score >= 45) {
    return {
      riskLabel: 'Moderate Risk',
      score,
      summary: 'There are notable risk indicators that should be monitored closely this week.',
      recommendations: [
        'Repeat vital readings at the same time each day.',
        'Document symptom frequency and intensity in detail.',
        'Schedule a check-in with your provider within 48 hours.',
      ],
    }
  }

  return {
    riskLabel: 'Low Risk',
    score,
    summary: 'Current signs indicate a stable profile with low near-term risk.',
    recommendations: [
      'Continue your current routine and weekly monitoring.',
      'Maintain sleep and hydration targets.',
      'Report any sudden symptom changes immediately.',
    ],
  }
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  selectedStage: 'pregnancy',
  formValues: initialFormValues,
  result: null,

  setStage: (stage) => set({ selectedStage: stage, result: null }),

  setField: (field, value) => {
    const { selectedStage, formValues } = get()
    set({
      formValues: {
        ...formValues,
        [selectedStage]: {
          ...formValues[selectedStage],
          [field]: value,
        },
      },
    })
  },

  assessRisk: () => {
    const { selectedStage, formValues } = get()
    const result = calculateRisk(selectedStage, formValues[selectedStage])
    set({ result })
  },

  resetAssessment: () => {
    const { selectedStage, formValues } = get()
    set({
      formValues: {
        ...formValues,
        [selectedStage]: { ...initialFormValues[selectedStage] },
      },
      result: null,
    })
  },
}))
