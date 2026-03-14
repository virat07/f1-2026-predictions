import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import DriverStandings from './components/DriverStandings'
import ConstructorStandings from './components/ConstructorStandings'
import RaceCalendar from './components/RaceCalendar'
import Leaderboard from './components/Leaderboard'
import Regulations from './components/Regulations'
import HotTakes from './components/HotTakes'
import Notification from './components/Notification'
import Footer from './components/Footer'

function App() {
  const [activeSection, setActiveSection] = useState('hero')
  const [notification, setNotification] = useState({ message: '', type: 'info' })

  const notify = (message, type = 'info') => {
    setNotification({ message, type });
  };

  useEffect(() => {
    const sections = document.querySelectorAll('section[id]')
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id)
          }
        })
      },
      { rootMargin: '-30% 0px -70% 0px' }
    )

    sections.forEach((section) => observer.observe(section))
    return () => observer.disconnect()
  }, [])

  return (
    <div className="app">
      <Navbar activeSection={activeSection} />
      <Notification 
        message={notification.message} 
        type={notification.type} 
        onClose={() => setNotification({ ...notification, message: '' })} 
      />
      <Hero />
      <DriverStandings />
      <ConstructorStandings />
      <RaceCalendar notify={notify} />
      <Leaderboard />
      <Regulations />
      <HotTakes />
      <Footer />
    </div>
  )
}

export default App
