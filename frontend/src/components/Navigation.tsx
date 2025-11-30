/**
 * Navigation Component
 * Main navigation bar
 */

import { Link, useLocation } from 'react-router-dom';

export default function Navigation() {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          FTA Review
        </Link>

        <div className="nav-links">
          <Link to="/" className={`nav-link ${isActive('/')}`}>
            Home
          </Link>
          <Link to="/projects" className={`nav-link ${isActive('/projects')}`}>
            Projects
          </Link>
        </div>
      </div>
    </nav>
  );
}
