/**
 * HomePage
 * Landing page with overview and quick actions
 */

import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="home-page">
      <div className="hero">
        <h1>FTA Comprehensive Review Assessment</h1>
        <p className="hero-subtitle">
          Determine applicable review areas and estimate Level of Effort for your transit
          project
        </p>
      </div>

      <div className="features">
        <div className="feature-card">
          <h3>Project Management</h3>
          <p>Create and manage multiple review projects with saved assessments</p>
          <Link to="/projects" className="btn-primary">
            View Projects
          </Link>
        </div>

        <div className="feature-card">
          <h3>Applicability Assessment</h3>
          <p>Answer questions to determine which FTA review areas apply to your project</p>
          <Link to="/projects/new" className="btn-primary">
            New Assessment
          </Link>
        </div>

        <div className="feature-card">
          <h3>LOE Estimation</h3>
          <p>Get AI-powered estimates of review hours for applicable areas</p>
        </div>
      </div>
    </div>
  );
}
