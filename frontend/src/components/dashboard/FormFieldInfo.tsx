import { CircleAlert } from 'lucide-react'

type FormFieldInfoProps = {
  label: string
  description: string
  textClassName?: string
}

export default function FormFieldInfo({ label, description, textClassName }: FormFieldInfoProps) {
  return (
    <span className="field-info-label">
      <span className={textClassName}>{label}</span>
      <span className="field-info-tooltip">
        <button
          type="button"
          className="field-info-trigger"
          aria-label={`More information about ${label}`}
        >
          <CircleAlert size={14} strokeWidth={2} aria-hidden />
        </button>
        <span role="tooltip" className="field-info-bubble">
          {description}
        </span>
      </span>
    </span>
  )
}
