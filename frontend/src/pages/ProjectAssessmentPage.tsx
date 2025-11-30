/**
 * ProjectAssessmentPage
 * Page for running assessment on a project
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Questionnaire from '../components/Questionnaire';
import apiService from '../services/api';

export default function ProjectAssessmentPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const projectId = parseInt(id || '0');

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (answers: Record<string, string>) => {
    try {
      setSubmitting(true);
      setError(null);

      await apiService.submitProjectAnswers(projectId, { answers });

      // Navigate to results page
      navigate(`/projects/${projectId}/results`);
    } catch (err) {
      console.error('Failed to submit assessment:', err);
      setError('Failed to submit assessment. Please try again.');
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    navigate(`/projects/${projectId}`);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Project Assessment</h2>
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
        </div>
      )}

      {submitting ? (
        <div className="submitting-message">
          <p>Processing your assessment...</p>
          <p className="submitting-details">
            Evaluating applicability rules and calculating LOE...
          </p>
        </div>
      ) : (
        <Questionnaire onSubmit={handleSubmit} onCancel={handleCancel} />
      )}
    </div>
  );
}
