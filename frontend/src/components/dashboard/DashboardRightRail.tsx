import { type ReactNode } from 'react'

export type DashboardRailSection = {
  title: string
  content: ReactNode
}

type DashboardRightRailProps = {
  sections: DashboardRailSection[]
}

export default function DashboardRightRail({ sections }: DashboardRightRailProps) {
  return (
    <div className="dashboard-rail-sections">
      {sections.map((section) => (
        <section key={section.title} className="dashboard-rail-card">
          <h2 className="dashboard-rail-card-title">{section.title}</h2>
          <div className="dashboard-rail-card-content">{section.content}</div>
        </section>
      ))}
    </div>
  )
}
