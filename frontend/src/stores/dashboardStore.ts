import { create } from 'zustand'
import { predictInfertility } from '../services/infertilityApi'

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
  isAssessing: boolean
  assessmentError: string | null
  setStage: (stage: HealthStage) => void
  setField: (field: string, value: string) => void
  assessRisk: () => Promise<void>
  resetAssessment: () => void
}

const initialFormValues: StageFormValues = {
  infertility: {
    age: '28',
    everCohabited: '1',
    childrenEverBorn: '0',
    irregularMenstrualCycles: '0',
    chronicPelvicPain: '0',
    historyPelvicInfections: '0',
    hormonalSymptoms: '0',
    earlyMenopauseSymptoms: '0',
    autoimmuneHistory: '0',
    reproductiveSurgeryHistory: '0',
    bmi: '24.5',
    smokedLast12mo: '0',
    alcoholLast12mo: '0',
    ageAtFirstMarriage: '22',
    monthsSinceFirstCohabitation: '96',
    monthsSinceLastSex: '2',
  },
  pregnancy: {
    currentWeek: '20',
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

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value))
}

function backendRiskLabelToUiLabel(label: string): AssessmentResult['riskLabel'] {
  if (label === 'High Risk' || label === 'Moderate Risk' || label === 'Low Risk') {
    return label
  }
  return 'Moderate Risk'
}

function recommendationsFromRisk(riskLabel: AssessmentResult['riskLabel']): string[] {
  if (riskLabel === 'High Risk') {
    return [
      'Contact your care provider today for immediate guidance.',
      'Track symptoms daily and escalate any sudden worsening.',
      'Keep all follow-up appointments and labs on schedule.',
    ]
  }
  if (riskLabel === 'Moderate Risk') {
    return [
      'Continue daily tracking and note symptom changes.',
      'Book a provider follow-up within the next few days.',
      'Maintain hydration, sleep, and medication adherence.',
    ]
  }
  return [
    'Continue your current routine and weekly monitoring.',
    'Maintain sleep and hydration targets.',
    'Report any sudden symptom changes immediately.',
  ]
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  selectedStage: 'pregnancy',
  formValues: initialFormValues,
  result: null,
  isAssessing: false,
  assessmentError: null,

  setStage: (stage) => set({ selectedStage: stage, result: null, assessmentError: null }),

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

  assessRisk: async () => {
    const { selectedStage, formValues } = get()
    if (selectedStage !== 'infertility') {
      const result = calculateRisk(selectedStage, formValues[selectedStage])
      set({ result, assessmentError: null })
      return
    }

    const infertilityValues = formValues.infertility
    const rawAge = Number(infertilityValues.age || '')
    const rawChildrenEverBorn = Number(infertilityValues.childrenEverBorn || '')
    if (!Number.isFinite(rawAge) || !Number.isFinite(rawChildrenEverBorn)) {
      set({
        assessmentError: 'Age and Children Ever Born are required numeric values.',
        result: null,
      })
      return
    }

    const age = clamp(rawAge, 15, 60)
    const everCohabited = infertilityValues.everCohabited === '0' ? 0 : 1
    const includeHistoricalInputs = everCohabited === 1
    const childrenEverBorn = clamp(rawChildrenEverBorn, 0, 20)
    const bmiValue = Number(infertilityValues.bmi || '')
    const smokedLast12moValue = Number(infertilityValues.smokedLast12mo || '')
    const alcoholLast12moValue = Number(infertilityValues.alcoholLast12mo || '')
    const ageAtFirstMarriageValue = Number(infertilityValues.ageAtFirstMarriage || '')
    const monthsSinceFirstCohabitationValue = Number(infertilityValues.monthsSinceFirstCohabitation || '')
    const monthsSinceLastSexValue = Number(infertilityValues.monthsSinceLastSex || '')
    const irregularMenstrualCyclesValue = Number(infertilityValues.irregularMenstrualCycles || '')
    const chronicPelvicPainValue = Number(infertilityValues.chronicPelvicPain || '')
    const historyPelvicInfectionsValue = Number(infertilityValues.historyPelvicInfections || '')
    const hormonalSymptomsValue = Number(infertilityValues.hormonalSymptoms || '')
    const earlyMenopauseSymptomsValue = Number(infertilityValues.earlyMenopauseSymptoms || '')
    const autoimmuneHistoryValue = Number(infertilityValues.autoimmuneHistory || '')
    const reproductiveSurgeryHistoryValue = Number(infertilityValues.reproductiveSurgeryHistory || '')

    set({ isAssessing: true, assessmentError: null, result: null })
    try {
      const prediction = await predictInfertility({
        age,
        ever_cohabited: everCohabited,
        children_ever_born: childrenEverBorn,
        ...(Number.isFinite(irregularMenstrualCyclesValue)
          ? { irregular_menstrual_cycles: irregularMenstrualCyclesValue === 1 ? 1 : 0 }
          : {}),
        ...(Number.isFinite(chronicPelvicPainValue)
          ? { chronic_pelvic_pain: chronicPelvicPainValue === 1 ? 1 : 0 }
          : {}),
        ...(Number.isFinite(historyPelvicInfectionsValue)
          ? { history_pelvic_infections: historyPelvicInfectionsValue === 1 ? 1 : 0 }
          : {}),
        ...(Number.isFinite(hormonalSymptomsValue)
          ? { hormonal_symptoms: hormonalSymptomsValue === 1 ? 1 : 0 }
          : {}),
        ...(Number.isFinite(earlyMenopauseSymptomsValue)
          ? { early_menopause_symptoms: earlyMenopauseSymptomsValue === 1 ? 1 : 0 }
          : {}),
        ...(Number.isFinite(autoimmuneHistoryValue)
          ? { autoimmune_history: autoimmuneHistoryValue === 1 ? 1 : 0 }
          : {}),
        ...(Number.isFinite(reproductiveSurgeryHistoryValue)
          ? { reproductive_surgery_history: reproductiveSurgeryHistoryValue === 1 ? 1 : 0 }
          : {}),
        ...(includeHistoricalInputs && Number.isFinite(bmiValue) ? { bmi: bmiValue } : {}),
        ...(includeHistoricalInputs && Number.isFinite(smokedLast12moValue)
          ? { smoked_last_12mo: smokedLast12moValue === 1 ? 1 : 0 }
          : {}),
        ...(includeHistoricalInputs && Number.isFinite(alcoholLast12moValue)
          ? { alcohol_last_12mo: alcoholLast12moValue === 1 ? 1 : 0 }
          : {}),
        ...(includeHistoricalInputs && Number.isFinite(ageAtFirstMarriageValue)
          ? { age_at_first_marriage: ageAtFirstMarriageValue }
          : {}),
        ...(includeHistoricalInputs && Number.isFinite(monthsSinceFirstCohabitationValue)
          ? { months_since_first_cohabitation: monthsSinceFirstCohabitationValue }
          : {}),
        ...(includeHistoricalInputs && Number.isFinite(monthsSinceLastSexValue)
          ? { months_since_last_sex: monthsSinceLastSexValue }
          : {}),
      })

      const riskLabel = backendRiskLabelToUiLabel(prediction.risk_level)
      set({
        isAssessing: false,
        assessmentError: null,
        result: {
          riskLabel,
          score: Math.round(prediction.probability_infertile * 100),
          summary: `Prediction mode: ${prediction.assessment_mode.replace('_', ' ')}. Class: ${prediction.predicted_class.replaceAll('_', ' ')}.`,
          recommendations: recommendationsFromRisk(riskLabel),
        },
      })
    } catch (error) {
      set({
        isAssessing: false,
        assessmentError:
          error instanceof Error ? error.message : 'Failed to generate infertility assessment.',
        result: null,
      })
    }
  },

  resetAssessment: () => {
    const { selectedStage, formValues } = get()
    set({
      formValues: {
        ...formValues,
        [selectedStage]: { ...initialFormValues[selectedStage] },
      },
      result: null,
      assessmentError: null,
    })
  },
}))
