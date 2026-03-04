import { type ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { Asterisk, Grid2x2, Heart, Smile } from 'lucide-react'
import { useAuthStore } from '../../stores/authStore'
import appLogo from '../../assets/logo.svg'

type DashboardSidebarProps = {
  onNavigate?: () => void
}

type NavItem = {
  label: string
  to: string
  icon: ReactNode
}

const navItems: NavItem[] = [
  {
    label: 'Overview',
    to: '/dashboard',
    icon: <Grid2x2 size={16} strokeWidth={2} aria-hidden />,
  },
  {
    label: 'Infertility',
    to: '/dashboard/infertility',
    icon: <Asterisk size={16} strokeWidth={2} aria-hidden />,
  },
  {
    label: 'Pregnancy',
    to: '/dashboard/pregnancy',
    icon: <Heart size={16} strokeWidth={2} aria-hidden />,
  },
  {
    label: 'Postpartum',
    to: '/dashboard/postpartum',
    icon: <Smile size={16} strokeWidth={2} aria-hidden />,
  },
]

export default function DashboardSidebar({ onNavigate }: DashboardSidebarProps) {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  const fullName = user?.fullName || 'Sarah Jenkins'
  const email = user?.email || 'sarah@example.com'

  const handleLogout = async () => {
    await logout()
    onNavigate?.()
    navigate('/sign-in')
  }

  return (
    <aside className="dashboard-sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-brand-icon">
          <img src={appLogo} alt="EveBloom logo" className="sidebar-brand-logo" />
        </span>
        <div>
          <p className="sidebar-brand-title">EveBloom</p>
          <p className="sidebar-brand-subtitle">Care Dashboard</p>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Dashboard navigation">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/dashboard'}
            className={({ isActive }) => (isActive ? 'sidebar-link active' : 'sidebar-link')}
            onClick={onNavigate}
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="sidebar-user-card">
          <div className="sidebar-user-head">
            <span className="sidebar-avatar">
              <img src={appLogo} alt="User logo" className="sidebar-avatar-logo" />
            </span>
            <div>
              <p className="sidebar-user-name">{fullName}</p>
              <p className="sidebar-user-email">{email}</p>
            </div>
          </div>

          <button type="button" className="sidebar-signout" onClick={() => void handleLogout()}>
            Sign Out
          </button>
        </div>
      </div>
    </aside>
  )
}
