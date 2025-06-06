import React from 'react';

const Header = () => (
  <>
    {/* Accessibility and language bar */}
    <div className="ernet-access-bar">
      <a href="#" className="ernet-access-link">Screen Reader Access</a>
      <a href="#" className="ernet-access-link">Skip to Main Content</a>
      <select className="ernet-access-lang">
        <option value="en">Select Language</option>
        <option value="hi">Hindi</option>
      </select>
      <button className="ernet-access-btn">A-</button>
      <button className="ernet-access-btn">A</button>
      <button className="ernet-access-btn">A+</button>
      <button className="ernet-access-btn ernet-access-btn-invert">A</button>
      <span className="ernet-access-help">Help</span>
    </div>
    <header className="ernet-header">
      <div className="ernet-header-top improved-header-layout">
        <img src="/ernet-logo.png" alt="ERNET India Logo" className="ernet-logo" />
        <nav className="ernet-nav improved-nav-bar">
          <a href="#" className="ernet-nav-link improved-nav-link">Home</a>
          <a href="#" className="ernet-nav-link improved-nav-link">Guidelines and T&amp;C</a>
          <a href="#" className="ernet-nav-link improved-nav-link">Tariff</a>
          <a href="#" className="ernet-nav-link improved-nav-link">Value Added Services</a>
          <a href="#" className="ernet-nav-link improved-nav-link">Panel Login</a>
          <a href="#" className="ernet-nav-link improved-nav-link">Contact Us</a>
        </nav>
        <div className="ernet-header-logos">
          <img src="/g20-logo.png" alt="G20 India Logo" className="ernet-g20-logo" />
          <img src="/gov-logo.png" alt="Government of India Logo" className="ernet-gov-logo" />
        </div>
      </div>
    </header>
  </>
);

export default Header; 