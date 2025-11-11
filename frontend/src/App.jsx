// src/App.jsx
import React, { useEffect, useState } from "react";
import LoginPage from "./components/LoginPage.jsx";
import AITravelChat from "./components/AITravelChat.jsx";
import HomePage from "./components/HomePage.jsx";

function App() {
  const [view, setView] = useState("home"); // 'home' | 'login' | 'chat'
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const rememberedUser = localStorage.getItem("rememberedUser");
    if (!rememberedUser) return;
    try {
      const userData = JSON.parse(rememberedUser);
      setUser(userData);
      setIsLoggedIn(true);
      setView("chat");
    } catch {
      localStorage.removeItem("rememberedUser");
    }
  }, []);

  const handleLogin = (email, password, rememberMe) => {
    const userName = email.split("@")[0];
    const userData = { email, name: userName, provider: "email" };
    if (rememberMe) localStorage.setItem("rememberedUser", JSON.stringify(userData));
    setUser(userData);
    setIsLoggedIn(true);
    setView("chat");
  };

  const handleGoogleLogin = () => {
    const userData = { email: "user@gmail.com", name: "Google User", provider: "google" };
    setUser(userData);
    setIsLoggedIn(true);
    setView("chat");
  };

  const handleLogout = () => {
    setUser(null);
    setIsLoggedIn(false);
    localStorage.removeItem("rememberedUser");
    setView("home");
  };

  return (
    <div className="App">
      {view === "home" && (
        <HomePage
          onGetStarted={() => setView("login")}
          onTryDemo={() => setView("login")}
        />
      )}

      {view === "login" && !isLoggedIn && (
        <LoginPage
          onLogin={handleLogin}
          onGoogleLogin={handleGoogleLogin}
        />
      )}

      {view === "chat" && isLoggedIn && (
        <AITravelChat
          user={user}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}

export default App;
