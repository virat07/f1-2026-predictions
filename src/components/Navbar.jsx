import { useState } from 'react'
import './Navbar.css'

const navItems = [
  { id: 'hero', label: 'Home' },
  { id: 'drivers', label: 'Drivers' },
  { id: 'constructors', label: 'Teams' },
  { id: 'calendar', label: 'Calendar' },
  { id: 'leaderboard', label: 'Compete' },
  { id: 'regulations', label: 'Regulations' },
  { id: 'hot-takes', label: 'Hot Takes' },
]

function Navbar({ activeSection }) {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useState(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  })

  const handleClick = (e, id) => {
    e.preventDefault()
    const el = document.getElementById(id)
    if (el) {
      const navHeight = 70
      const top = el.getBoundingClientRect().top + window.pageYOffset - navHeight
      window.scrollTo({ top, behavior: 'smooth' })
    }
    setIsOpen(false)
  }

  return (
    <nav id="main-nav" className={scrolled ? 'scrolled' : ''}>
      <div className="nav-container">
        <div className="nav-logo">
          <span className="logo-f1">F1</span>
          <span className="logo-year">2026</span>
          <span className="logo-tag">PREDICTIONS</span>
        </div>
        <div className={`nav-links ${isOpen ? 'open' : ''}`}>
          {navItems.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`nav-link ${activeSection === item.id ? 'active' : ''}`}
              onClick={(e) => handleClick(e, item.id)}
            >
              {item.label}
            </a>
          ))}
        </div>
        <button
          className={`nav-toggle ${isOpen ? 'active' : ''}`}
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle navigation"
        >
          <span></span><span></span><span></span>
        </button>
      </div>
    </nav>
  )
}

export default Navbar
