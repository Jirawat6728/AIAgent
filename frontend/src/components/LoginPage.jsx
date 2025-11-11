import React, { useState } from 'react';
import './LoginPage.css';

export default function LoginPage({ onLogin, onGoogleLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [lang, setLang] = useState('th'); // 🔄 ภาษาเริ่มต้น

  const handleLoginClick = () => {
    onLogin(email, password, rememberMe);
  };

  // 🈯️ ข้อความ 2 ภาษา
  const text = {
    en: {
      title: 'Log In',
      email: 'Email',
      password: 'Password',
      remember: 'Remember me',
      signIn: 'Sign In',
      signUp: 'Sign Up',
      forgot: 'Forgot Password?',
      orContinue: 'Or continue with',
      google: 'Login with Google',
      appName: 'AI Travel Agent',
    },
    th: {
      title: 'เข้าสู่ระบบ',
      email: 'อีเมล',
      password: 'รหัสผ่าน',
      remember: 'จำฉันไว้',
      signIn: 'เข้าสู่ระบบ',
      signUp: 'สมัครสมาชิก',
      forgot: 'ลืมรหัสผ่าน?',
      orContinue: 'หรือต่อด้วย',
      google: 'เข้าสู่ระบบด้วย Google',
      appName: 'ผู้ช่วยท่องเที่ยวอัจฉริยะ',
    },
  };

  return (
    <div className="login-container">
      {/* Header */}
      <header className="login-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">
              <svg className="plane-icon" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
              </svg>
            </div>
            <span className="logo-text">{text[lang].appName}</span>
          </div>

          {/* 🔘 ปุ่มเปลี่ยนภาษา */}
          <div className="header-buttons">
            <button
              className="btn-header"
              onClick={() => setLang(lang === 'en' ? 'th' : 'en')}
            >
              {lang === 'en' ? 'ภาษาไทย' : 'English'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="login-main">
        {/* Background */}
        <div className="login-background">
          <div className="bg-gradient">
            <div className="cloud-patterns">
              <div className="cloud cloud-1"></div>
              <div className="cloud cloud-2"></div>
              <div className="cloud cloud-3"></div>
            </div>
          </div>
          <div className="plane-wing">
            <svg viewBox="0 0 300 300" className="wing-svg">
              <path d="M0,150 Q50,100 150,120 L180,140 L0,200 Z" fill="#1e40af" opacity="0.5"/>
              <path d="M0,180 Q60,140 160,150 L190,160 L0,220 Z" fill="#1e3a8a" opacity="0.3"/>
            </svg>
          </div>
        </div>

        {/* Login Form */}
        <div className="form-container">
          <div className="login-card">
            <h2 className="login-title">{text[lang].title}</h2>

            <div className="form-content">
              {/* Email */}
              <div className="form-group">
                <label htmlFor="email" className="form-label">{text[lang].email}</label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={text[lang].email}
                  className="form-input"
                />
              </div>

              {/* Password */}
              <div className="form-group">
                <label htmlFor="password" className="form-label">{text[lang].password}</label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={text[lang].password}
                  className="form-input"
                />
              </div>

              {/* Remember Me */}
              <div className="remember-me">
                <input
                  type="checkbox"
                  id="remember"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="checkbox"
                />
                <label htmlFor="remember" className="checkbox-label">
                  {text[lang].remember}
                </label>
              </div>

              {/* Buttons */}
              <button onClick={handleLoginClick} className="btn-login">
                {text[lang].signIn}
              </button>
              <button onClick={handleLoginClick} className="btn-login">
                {text[lang].signUp}
              </button>

              {/* Forgot Password */}
              <div className="forgot-password">
                <a href="#" className="forgot-link">{text[lang].forgot}</a>
              </div>

              {/* Divider */}
              <div className="divider">
                <span className="divider-text">{text[lang].orContinue}</span>
              </div>

              {/* Google Login */}
              <button onClick={onGoogleLogin} className="btn-google">
                <svg className="google-icon" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                {text[lang].google}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
