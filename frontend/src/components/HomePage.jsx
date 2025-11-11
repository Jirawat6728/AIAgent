import React, { useState } from 'react';
import './HomePage.css';

export default function HomePage({ onGetStarted }) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onGetStarted(searchQuery);
    }
  };

  return (
    <div className="home-container">
      {/* Header */}
      <header className="home-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">
              <svg className="plane-icon" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
              </svg>
            </div>
            <span className="logo-text">AI Travel Agent</span>
          </div>
          <nav className="nav-links">
            <a href="#features" className="nav-link">Features</a>
            <a href="#how-it-works" className="nav-link">How it Works</a>
            <a href="#destinations" className="nav-link">Destinations</a>
            <a href="#about" className="nav-link">About</a>
          </nav>
          <div className="header-buttons">
            <button onClick={onGetStarted} className="btn-header">Sign In</button>
            <button onClick={onGetStarted} className="btn-header-primary">Get Started</button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-background">
          <div className="gradient-overlay"></div>
          <div className="animated-shapes">
            <div className="shape shape-1"></div>
            <div className="shape shape-2"></div>
            <div className="shape shape-3"></div>
          </div>
        </div>
        
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-text">✨ Powered by AI</span>
          </div>
          <h1 className="hero-title">
            Your Personal AI Travel Agent
          </h1>
          <p className="hero-subtitle">
            Plan your perfect trip with AI. Find flights, hotels, and get personalized recommendations instantly.
          </p>
          
          {/* Search Bar */}
          <form onSubmit={handleSearch} className="search-box">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Where do you want to go? (e.g., Tokyo, Paris, New York)"
              className="search-input"
            />
            <button type="submit" className="search-button">
              <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Search
            </button>
          </form>

          {/* Quick Actions */}
          <div className="quick-actions">
            <button onClick={() => onGetStarted('flights')} className="quick-action">
              <span>✈️</span> Find Flights
            </button>
            <button onClick={() => onGetStarted('hotels')} className="quick-action">
              <span>🏨</span> Book Hotels
            </button>
            <button onClick={() => onGetStarted('destinations')} className="quick-action">
              <span>🌍</span> Explore Destinations
            </button>
          </div>
        </div>
      </section>

      
      



      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Start Your Journey?</h2>
          <p className="cta-subtitle">Join thousands of travelers who trust AI Travel Agent</p>
          <button onClick={onGetStarted} className="cta-button">
            Get Started Now
            <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <div className="footer-logo">
              <div className="logo-icon">
                <svg className="plane-icon" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
                </svg>
              </div>
              <span className="logo-text">AI Travel Agent</span>
            </div>
            <p className="footer-description">Your intelligent companion for seamless travel planning</p>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">Product</h4>
            <a href="#features" className="footer-link">Features</a>
            <a href="#how-it-works" className="footer-link">How it Works</a>
            <a href="#destinations" className="footer-link">Destinations</a>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">Company</h4>
            <a href="#about" className="footer-link">About Us</a>
            <a href="#" className="footer-link">Contact</a>
            <a href="#" className="footer-link">Privacy Policy</a>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">Connect</h4>
            <a href="#" className="footer-link">Twitter</a>
            <a href="#" className="footer-link">Facebook</a>
            <a href="#" className="footer-link">Instagram</a>
          </div>
        </div>

        <div className="footer-bottom">
          <p>© 2025 AI Travel Agent. Powered by Google Gemini & Amadeus </p>
        </div>
      </footer>
    </div>
  );
}