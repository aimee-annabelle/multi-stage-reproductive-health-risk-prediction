import type { PostpartumRequestPayload } from '../../services/predictionApi'

export const yesNoOptions = [
  { value: 'yes', label: 'Yes' },
  { value: 'no', label: 'No' },
]

export const epdsOptionsByField: Record<string, string[]> = {
  epds_laugh_and_funny_side: [
    'As much as I always could',
    'Not quite so much now',
    'Definitely not so much now',
    'Not at all',
  ],
  epds_looked_forward_enjoyment: [
    'As much as I ever did',
    'Rather less than I used to',
    'Definitely less than I used to',
    'Rarely',
  ],
  epds_blamed_myself: ['No, never', 'Not very often', 'Yes, some of the time', 'Yes, most of the time'],
  epds_anxious_or_worried: ['No, not at all', 'Hardly ever', 'Yes, sometimes', 'Yes, very often'],
  epds_scared_or_panicky: ['No, not at all', 'No, not much', 'Yes, sometimes', 'Yes, quite a lot'],
  epds_things_getting_on_top: [
    'No, I have been coping as well as ever',
    'No, most of the time I have coped quite well',
    'Yes, sometimes I have not been coping as well as usual',
    'I have not been able to cope at all',
  ],
  epds_unhappy_difficulty_sleeping: ['No, not at all', 'Not very often', 'Yes, sometimes', 'Yes, most of the time'],
  epds_sad_or_miserable: ['No, not at all', 'Not very often', 'Yes, quite often', 'Yes, most of the time'],
  epds_unhappy_crying: ['No, never', 'Only occasionally', 'Yes, quite often', 'Yes, most of the time'],
  epds_thought_of_harming_self: ['Never', 'Hardly ever', 'Sometimes', 'Yes, quite often'],
}

export const epdsLabelsByField: Record<string, string> = {
  epds_laugh_and_funny_side: 'Ability to laugh and see the funny side',
  epds_looked_forward_enjoyment: 'Looked forward to enjoyment',
  epds_blamed_myself: 'Blamed myself unnecessarily',
  epds_anxious_or_worried: 'Anxious or worried',
  epds_scared_or_panicky: 'Scared or panicky',
  epds_things_getting_on_top: 'Things getting on top of me',
  epds_unhappy_difficulty_sleeping: 'Unhappy and difficulty sleeping',
  epds_sad_or_miserable: 'Sad or miserable',
  epds_unhappy_crying: 'Unhappy and crying',
  epds_thought_of_harming_self: 'Thought of harming self',
}

export const binaryFieldDefs: Array<{ key: keyof PostpartumRequestPayload; label: string; hint: string }> = [
  { key: 'smoke_cigarettes', label: 'Smoke cigarettes', hint: 'Current or recent cigarette smoking' },
  { key: 'smoke_shisha', label: 'Smoke shisha', hint: 'Current or recent shisha use' },
  { key: 'premature_labour', label: 'Premature labour', hint: 'History of labor before full term' },
  { key: 'healthy_baby', label: 'Healthy baby', hint: 'Overall healthy newborn status' },
  { key: 'baby_admitted_nicu', label: 'Baby admitted in NICU', hint: 'Neonatal intensive care admission' },
  {
    key: 'baby_feeding_difficulties',
    label: 'Baby feeding difficulties',
    hint: 'Trouble breastfeeding or bottle feeding',
  },
  { key: 'pregnancy_problem', label: 'Pregnancy problems', hint: 'Complications experienced during pregnancy' },
  { key: 'postnatal_problems', label: 'Postnatal problems', hint: 'Any postpartum clinical or emotional issues' },
  { key: 'natal_problems', label: 'Natal problems', hint: 'Complications during birth' },
  { key: 'problems_with_husband', label: 'Problems with husband', hint: 'Relationship stress in partner context' },
  { key: 'financial_problems', label: 'Financial problems', hint: 'Current financial stress indicators' },
  { key: 'family_problems', label: 'Family problems', hint: 'Family conflict or low family support' },
  { key: 'had_covid_19', label: 'Had COVID-19', hint: 'Confirmed COVID-19 history' },
  { key: 'had_covid_19_vaccine', label: 'Had COVID-19 vaccine', hint: 'COVID-19 vaccination status' },
  {
    key: 'aware_of_ppd_symptoms',
    label: 'Aware of PPD symptoms and risk factors',
    hint: 'Awareness of postpartum depression warning signs',
  },
  {
    key: 'experienced_cultural_stigma_ppd',
    label: 'Experienced stigma around PPD',
    hint: 'Stigma or judgement within social context',
  },
  {
    key: 'received_support_or_treatment_ppd',
    label: 'Received support or treatment for PPD',
    hint: 'Any formal or informal care received',
  },
]

export const coreBinaryKeys: Array<keyof PostpartumRequestPayload> = [
  'postnatal_problems',
  'baby_feeding_difficulties',
  'financial_problems',
]

export const coreEpdsKeys = ['epds_anxious_or_worried', 'epds_sad_or_miserable', 'epds_thought_of_harming_self']

export const initialPostpartumFormValues: Record<string, string> = {
  age_group: '',
  baby_age_months: '',
  kgs_gained_during_pregnancy: '',
  marital_status: '',
  household_income: '',
  level_of_education: '',
  residency: '',
  comorbidities: '',
  access_to_healthcare_services: '',
  smoke_cigarettes: '',
  smoke_shisha: '',
  premature_labour: '',
  healthy_baby: '',
  baby_admitted_nicu: '',
  baby_feeding_difficulties: '',
  pregnancy_problem: '',
  postnatal_problems: '',
  natal_problems: '',
  problems_with_husband: '',
  financial_problems: '',
  family_problems: '',
  had_covid_19: '',
  had_covid_19_vaccine: '',
  aware_of_ppd_symptoms: '',
  experienced_cultural_stigma_ppd: '',
  received_support_or_treatment_ppd: '',
  epds_laugh_and_funny_side: '',
  epds_looked_forward_enjoyment: '',
  epds_blamed_myself: '',
  epds_anxious_or_worried: '',
  epds_scared_or_panicky: '',
  epds_things_getting_on_top: '',
  epds_unhappy_difficulty_sleeping: '',
  epds_sad_or_miserable: '',
  epds_unhappy_crying: '',
  epds_thought_of_harming_self: '',
}

export function toOptionalNumber(value: string): number | null {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) {
    return null
  }
  return numeric
}

export function buildPostpartumPayload(formValues: Record<string, string>): PostpartumRequestPayload {
  const payloadRecord: Record<string, string | number | boolean> = {}

  if (formValues.age_group) payloadRecord.age_group = formValues.age_group
  if (formValues.marital_status) payloadRecord.marital_status = formValues.marital_status
  if (formValues.household_income) payloadRecord.household_income = formValues.household_income
  if (formValues.level_of_education) payloadRecord.level_of_education = formValues.level_of_education
  if (formValues.residency) payloadRecord.residency = formValues.residency
  if (formValues.comorbidities.trim()) payloadRecord.comorbidities = formValues.comorbidities.trim()
  if (formValues.access_to_healthcare_services) {
    payloadRecord.access_to_healthcare_services = formValues.access_to_healthcare_services
  }

  const babyAgeMonths = toOptionalNumber(formValues.baby_age_months)
  const kgsGained = toOptionalNumber(formValues.kgs_gained_during_pregnancy)
  if (babyAgeMonths !== null) payloadRecord.baby_age_months = babyAgeMonths
  if (kgsGained !== null) payloadRecord.kgs_gained_during_pregnancy = kgsGained

  for (const binaryField of binaryFieldDefs) {
    const value = formValues[binaryField.key]
    if (value === 'yes' || value === 'no') {
      payloadRecord[binaryField.key] = value
    }
  }

  for (const epdsField of Object.keys(epdsOptionsByField)) {
    const value = formValues[epdsField]
    if (value) {
      payloadRecord[epdsField] = value
    }
  }

  return payloadRecord as PostpartumRequestPayload
}

export function formatShortWeekday(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'N/A'
  }
  return new Intl.DateTimeFormat(undefined, { weekday: 'short' }).format(date)
}

export function buildLinePath(values: number[], width: number, height: number, padding: number): string {
  if (values.length === 0) {
    return ''
  }

  const usableWidth = width - padding * 2
  const usableHeight = height - padding * 2

  return values
    .map((value, index) => {
      const x = values.length === 1 ? width / 2 : padding + (index / (values.length - 1)) * usableWidth
      const y = padding + (1 - value / 100) * usableHeight
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
    })
    .join(' ')
}

export function toRecoveryPhase(week: number | null): string {
  if (week === null) {
    return 'Initial Postpartum Monitoring'
  }
  if (week <= 6) {
    return 'Healing & Bonding Phase'
  }
  if (week <= 24) {
    return 'Adjustment & Recovery Phase'
  }
  return 'Long-term Wellness Phase'
}

export function toTitleLabel(value: string): string {
  return value
    .replaceAll('_', ' ')
    .split(' ')
    .filter(Boolean)
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(' ')
}
