import {
  binaryFieldDefs,
  coreBinaryKeys,
  coreEpdsKeys,
  epdsDescriptionsByField,
  epdsLabelsByField,
  epdsOptionsByField,
  initialPostpartumFormValues,
  yesNoOptions,
  buildPostpartumPayload,
} from './postpartumShared'

export {
  epdsLabelsByField,
  epdsDescriptionsByField,
  epdsOptionsByField,
  initialPostpartumFormValues,
  yesNoOptions,
  buildPostpartumPayload,
  coreEpdsKeys,
}

export const coreBinaryFields = binaryFieldDefs.filter((field) => coreBinaryKeys.includes(field.key))

export const advancedBinaryFields = binaryFieldDefs.filter((field) => !coreBinaryKeys.includes(field.key))

export const advancedEpdsFields = Object.keys(epdsOptionsByField).filter(
  (field) => !coreEpdsKeys.includes(field),
)
