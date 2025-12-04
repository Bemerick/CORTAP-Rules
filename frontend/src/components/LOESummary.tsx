/**
 * LOESummary Component
 * Displays Level of Effort summary by section for a project
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { ProjectLOESummary } from '../types/api';
import apiService from '../services/api';

export default function LOESummary() {
  const { id } = useParams<{ id: string }>();
  const projectId = parseInt(id || '0');

  const [summary, setSummary] = useState<ProjectLOESummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) {
      loadSummary();
    }
  }, [projectId]);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProjectLOESummary(projectId);
      setSummary(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load LOE summary:', err);
      setError('No LOE data found. Please complete the assessment first.');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceBadgeClass = (score: number): string => {
    if (score >= 80) return 'confidence-high';
    if (score >= 60) return 'confidence-medium';
    return 'confidence-low';
  };

  if (loading) {
    return (
      <div className="loe-loading">
        <p>Loading LOE summary...</p>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="loe-error">
        <p className="error-message">{error || 'No LOE data found'}</p>
        <Link to={`/projects/${projectId}/assess`} className="btn-primary">
          Start Assessment
        </Link>
      </div>
    );
  }

  return (
    <div className="loe-summary">
      <div className="loe-header">
        <div>
          <h2>Level of Effort Summary</h2>
          <p className="project-name">{summary.project_name}</p>
        </div>
        <Link to={`/projects/${projectId}/results`} className="btn-secondary">
          View Results
        </Link>
      </div>

      <div className="loe-totals">
        <div className="total-card grand-total">
          <h3>Grand Total</h3>
          <div className="total-value">{summary.total_hours.toFixed(2)} hours</div>
          <div className="total-meta">
            <span>{summary.total_sub_areas} Questions Examined</span>
            <span>{summary.total_indicators} Indicators of Compliance</span>
            <span
              className={`confidence-badge ${getConfidenceBadgeClass(
                summary.avg_confidence_score
              )}`}
            >
              Avg Confidence: {summary.avg_confidence_score.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      <div className="loe-sections">
        <h3>Hours by Section</h3>

        <div className="sections-table">
          <table>
            <thead>
              <tr>
                <th>Section</th>
                <th>Questions Examined</th>
                <th>Indicators of Compliance</th>
                <th>Total Hours</th>
                <th>Avg Confidence</th>
              </tr>
            </thead>
            <tbody>
              {summary.sections
                .sort((a, b) => (a.chapter_number ?? 999) - (b.chapter_number ?? 999))
                .map((section) => (
                  <tr key={section.section_id}>
                    <td className="section-name">
                      {section.chapter_number ? `${section.chapter_number}. ` : ''}{section.section_name}
                    </td>
                    <td className="section-count">{section.sub_area_count}</td>
                    <td className="section-count">{section.indicator_count}</td>
                    <td className="section-hours">
                      <strong>{section.total_hours.toFixed(2)}</strong> hours
                    </td>
                    <td className="section-confidence">
                      <span
                        className={`confidence-badge ${getConfidenceBadgeClass(
                          section.avg_confidence_score
                        )}`}
                      >
                        {section.avg_confidence_score.toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
            </tbody>
            <tfoot>
              <tr className="totals-row">
                <td><strong>Total</strong></td>
                <td><strong>{summary.total_sub_areas}</strong></td>
                <td><strong>{summary.total_indicators}</strong></td>
                <td><strong>{summary.total_hours.toFixed(2)} hours</strong></td>
                <td>
                  <span
                    className={`confidence-badge ${getConfidenceBadgeClass(
                      summary.avg_confidence_score
                    )}`}
                  >
                    {summary.avg_confidence_score.toFixed(1)}%
                  </span>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <div className="loe-chart">
        <h3>Hours Distribution</h3>
        <div className="chart-bars">
          {summary.sections
            .sort((a, b) => (a.chapter_number ?? 999) - (b.chapter_number ?? 999))
            .slice(0, 10)
            .map((section) => {
              const percentage = (section.total_hours / summary.total_hours) * 100;
              return (
                <div key={section.section_id} className="chart-bar-row">
                  <div className="bar-label">
                    {section.chapter_number ? `${section.chapter_number}. ` : ''}{section.section_name}
                  </div>
                  <div className="bar-container">
                    <div
                      className="bar-fill"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="bar-value">{section.total_hours.toFixed(1)}h</div>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}
