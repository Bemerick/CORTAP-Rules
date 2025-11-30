/**
 * App Component
 * Main application with routing
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import ProjectsPage from './pages/ProjectsPage';
import NewProjectPage from './pages/NewProjectPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import ProjectAssessmentPage from './pages/ProjectAssessmentPage';
import ProjectResultsPage from './pages/ProjectResultsPage';
import ProjectLOEPage from './pages/ProjectLOEPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/new" element={<NewProjectPage />} />
            <Route path="/projects/:id" element={<ProjectDetailPage />} />
            <Route path="/projects/:id/assess" element={<ProjectAssessmentPage />} />
            <Route path="/projects/:id/results" element={<ProjectResultsPage />} />
            <Route path="/projects/:id/loe" element={<ProjectLOEPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
