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

export const epdsDescriptionsByField: Record<string, string> = {
  epds_laugh_and_funny_side: 'Choose the option that best matches how easily you have been able to laugh or notice the funny side lately.',
  epds_looked_forward_enjoyment: 'Choose the option that best matches how much you have looked forward to enjoyable things lately.',
  epds_blamed_myself: 'Choose the option that best matches how often you have blamed yourself when things went wrong.',
  epds_anxious_or_worried: 'Choose the option that best matches how often you have felt anxious or worried recently.',
  epds_scared_or_panicky: 'Choose the option that best matches how often you have felt scared or panicky.',
  epds_things_getting_on_top: 'Choose the option that best matches whether daily responsibilities have felt hard to manage.',
  epds_unhappy_difficulty_sleeping: 'Choose the option that best matches whether unhappiness has made it hard to sleep.',
  epds_sad_or_miserable: 'Choose the option that best matches how often you have felt sad or miserable.',
  epds_unhappy_crying: 'Choose the option that best matches how often you have felt so unhappy that you cried.',
  epds_thought_of_harming_self: 'Choose the option that best matches whether thoughts of harming yourself have occurred.',
}

export const binaryFieldDefs: Array<{
  key: keyof PostpartumRequestPayload
  label: string
  hint: string
  description: string
}> = [
  {
    key: 'smoke_cigarettes',
    label: 'Smoke cigarettes',
    hint: 'Current or recent cigarette smoking',
    description: 'Choose Yes if cigarettes are currently smoked or were smoked recently. Choose No if not.',
  },
  {
    key: 'smoke_shisha',
    label: 'Smoke shisha',
    hint: 'Current or recent shisha use',
    description: 'Choose Yes if shisha or hookah is currently used or was used recently. Choose No if not.',
  },
  {
    key: 'premature_labour',
    label: 'Premature labour',
    hint: 'History of labor before full term',
    description: 'Choose Yes if labor started before full term. Choose No if it did not.',
  },
  {
    key: 'healthy_baby',
    label: 'Healthy baby',
    hint: 'Overall healthy newborn status',
    description: 'Choose Yes if the baby is currently considered healthy overall. Choose No if there are health concerns.',
  },
  {
    key: 'baby_admitted_nicu',
    label: 'Baby admitted in NICU',
    hint: 'Neonatal intensive care admission',
    description: 'Choose Yes if the baby was admitted to a neonatal intensive care unit. Choose No if not.',
  },
  {
    key: 'baby_feeding_difficulties',
    label: 'Baby feeding difficulties',
    hint: 'Trouble breastfeeding or bottle feeding',
    description: 'Choose Yes if there have been difficulties with breastfeeding, bottle feeding, or latching.',
  },
  {
    key: 'pregnancy_problem',
    label: 'Pregnancy problems',
    hint: 'Complications experienced during pregnancy',
    description: 'Choose Yes if there were notable problems or complications during pregnancy.',
  },
  {
    key: 'postnatal_problems',
    label: 'Postnatal problems',
    hint: 'Any postpartum clinical or emotional issues',
    description: 'Choose Yes if there have been physical, emotional, or medical problems after delivery.',
  },
  {
    key: 'natal_problems',
    label: 'Natal problems',
    hint: 'Complications during birth',
    description: 'Choose Yes if there were complications during labor or birth.',
  },
  {
    key: 'problems_with_husband',
    label: 'Problems with husband',
    hint: 'Relationship stress in partner context',
    description: 'Choose Yes if there is current relationship stress or conflict with a partner.',
  },
  {
    key: 'financial_problems',
    label: 'Financial problems',
    hint: 'Current financial stress indicators',
    description: 'Choose Yes if there is current financial stress, difficulty paying bills, or money-related pressure.',
  },
  {
    key: 'family_problems',
    label: 'Family problems',
    hint: 'Family conflict or low family support',
    description: 'Choose Yes if there is ongoing family conflict or limited family support.',
  },
  {
    key: 'had_covid_19',
    label: 'Had COVID-19',
    hint: 'Confirmed COVID-19 history',
    description: 'Choose Yes if there has been a COVID-19 infection before or during this period.',
  },
  {
    key: 'had_covid_19_vaccine',
    label: 'Had COVID-19 vaccine',
    hint: 'COVID-19 vaccination status',
    description: 'Choose Yes if a COVID-19 vaccine was received. Choose No if not.',
  },
  {
    key: 'aware_of_ppd_symptoms',
    label: 'Aware of PPD symptoms and risk factors',
    hint: 'Awareness of postpartum depression warning signs',
    description: 'Choose Yes if there is awareness of postpartum depression symptoms and warning signs. Choose No if not.',
  },
  {
    key: 'experienced_cultural_stigma_ppd',
    label: 'Experienced stigma around PPD',
    hint: 'Stigma or judgement within social context',
    description: 'Choose Yes if there has been judgement, stigma, or negative social pressure around postpartum depression.',
  },
  {
    key: 'received_support_or_treatment_ppd',
    label: 'Received support or treatment for PPD',
    hint: 'Any formal or informal care received',
    description: 'Choose Yes if support, counselling, medication, or other treatment for postpartum depression has been received.',
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
