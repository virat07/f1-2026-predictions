import './Footer.css'

function Footer() {
  return (
    <footer id="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-logo">
            <span className="logo-f1">F1</span>
            <span className="logo-year">2026</span>
            <span className="logo-tag">PREDICTIONS</span>
          </div>
          <p className="footer-disclaimer">
            This is a fan-made prediction page. All predictions are speculative and for entertainment purposes only. Not affiliated with Formula 1, FIA, or any F1 team.
          </p>
          <p className="footer-copyright">© 2026 F1 2026 Predictions. Made with ❤️ and a lot of speculation.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
