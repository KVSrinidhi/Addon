import { useState } from "react";
import "./App.css"
const App = () => {
  const [darkMode, setDarkMode] = useState(false);
  return (
    <>
      <div className={`app-container ${darkMode ? "dark" : "light"}`}>
        <div className="top-bar">
          <div className="top-bar-left">
            <div className="page-title" id="page-title">Dashboard</div>
            <div className="breadcrumb" id="breadcrumb">EduGenie | Home</div>
          </div>
          <div className="top-bar-right">
            <button className="theme-toggle"
              onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? "🌙" : "☀️"}
            </button>
          </div>
        </div>
        <div className="content-area" id="content-area">
          <div className="welcome-block" id="Welcome-block">
            <div className="welcome-header">Welcome back to EduGenie 👋</div>
            <div className="welcome-description">Transform your study materials into an interactive learning experience. Upload PDFs, ask questions, generate summaries, and receive personalized assistance powered by AI.</div>
          </div>
        </div>
      </div>
    </>
  );
};

export default App;