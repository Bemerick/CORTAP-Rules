/**
 * ProjectDetail Component
 * Displays project details and assessment results
 */

import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import type { Project } from '../types/api';
import apiService from '../services/api';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const projectId = parseInt(id || '0');

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) {
      loadProject();
    }
  }, [projectId]);

  const loadProject = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProject(projectId);
      setProject(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load project:', err);
      setError('Failed to load project. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="project-detail-loading">
        <p>Loading project...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="project-detail-error">
        <p className="error-message">{error || 'Project not found'}</p>
        <Link to="/projects" className="btn-secondary">
          Back to Projects
        </Link>
      </div>
    );
  }

  return (
    <div className="project-detail">
      <div className="project-detail-header">
        <div>
          <h2>{project.name}</h2>
          {project.description && (
            <p className="project-description">{project.description}</p>
          )}
        </div>
        <Link to="/projects" className="btn-secondary">
          Back to Projects
        </Link>
      </div>

      <div className="project-meta">
        <div className="meta-item">
          <strong>Created:</strong> {formatDate(project.created_at)}
        </div>
        <div className="meta-item">
          <strong>Last Updated:</strong> {formatDate(project.updated_at)}
        </div>
      </div>

      <div className="project-actions">
        <Link to={`/projects/${project.id}/assess`} className="btn-primary">
          Start/Update Assessment
        </Link>
        <Link to={`/projects/${project.id}/results`} className="btn-secondary">
          View Results
        </Link>
        <Link to={`/projects/${project.id}/loe`} className="btn-secondary">
          View LOE Summary
        </Link>
      </div>
    </div>
  );
}
