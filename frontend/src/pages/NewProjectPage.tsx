/**
 * NewProjectPage
 * Page for creating a new project
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectForm from '../components/ProjectForm';
import type { ProjectCreate } from '../types/api';
import apiService from '../services/api';

export default function NewProjectPage() {
  const navigate = useNavigate();
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: ProjectCreate) => {
    try {
      setCreating(true);
      setError(null);
      const project = await apiService.createProject(data);
      // Navigate to assessment page after creating project
      navigate(`/projects/${project.id}/assess`);
    } catch (err) {
      console.error('Failed to create project:', err);
      setError('Failed to create project. Please try again.');
      setCreating(false);
    }
  };

  const handleCancel = () => {
    navigate('/projects');
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Create New Project</h2>
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
        </div>
      )}

      {creating ? (
        <div className="creating-message">
          <p>Creating project...</p>
        </div>
      ) : (
        <ProjectForm onSubmit={handleSubmit} onCancel={handleCancel} />
      )}
    </div>
  );
}
