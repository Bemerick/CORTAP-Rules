/**
 * ProjectList Component
 * Displays all projects with options to view, edit, or delete
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { Project } from '../types/api';
import apiService from '../services/api';

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProjects();
      setProjects(data.sort((a, b) =>
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      ));
      setError(null);
    } catch (err) {
      console.error('Failed to load projects:', err);
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
      return;
    }

    try {
      await apiService.deleteProject(id);
      setProjects(projects.filter((p) => p.id !== id));
    } catch (err) {
      console.error('Failed to delete project:', err);
      alert('Failed to delete project. Please try again.');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="project-list-loading">
        <p>Loading projects...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="project-list-error">
        <p className="error-message">{error}</p>
        <button onClick={loadProjects}>Retry</button>
      </div>
    );
  }

  return (
    <div className="project-list">
      <div className="project-list-header">
        <h2>My Projects</h2>
        <Link to="/projects/new" className="btn-primary">
          New Project
        </Link>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state">
          <p>No projects yet. Create your first project to get started!</p>
          <Link to="/projects/new" className="btn-primary">
            Create Project
          </Link>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div key={project.id} className="project-card">
              <div className="project-card-header">
                <h3>{project.name}</h3>
              </div>

              <div className="project-card-body">
                {project.description && (
                  <p className="project-description">{project.description}</p>
                )}

                <div className="project-meta">
                  <span>Updated: {formatDate(project.updated_at)}</span>
                </div>
              </div>

              <div className="project-card-actions">
                <Link to={`/projects/${project.id}`} className="btn-secondary">
                  View Details
                </Link>
                <Link to={`/projects/${project.id}/assess`} className="btn-primary">
                  Start Assessment
                </Link>
                <button
                  onClick={() => handleDelete(project.id, project.name)}
                  className="btn-danger"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
