/**
 * ApplicabilityResults Component
 * Displays which sub-areas are applicable based on assessment answers
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { ProjectApplicabilityResult, ApplicableSubArea } from '../types/api';
import apiService from '../services/api';

export default function ApplicabilityResults() {
  const { id } = useParams<{ id: string }>();
  const projectId = parseInt(id || '0');

  const [results, setResults] = useState<ProjectApplicabilityResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [groupBy, setGroupBy] = useState<'section' | 'all'>('section');

  useEffect(() => {
    if (projectId) {
      loadResults();
    }
  }, [projectId]);

  const loadResults = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProjectApplicableSubAreas(projectId);
      setResults(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load results:', err);
      setError('No assessment results found. Please complete the assessment first.');
    } finally {
      setLoading(false);
    }
  };

  const groupedBySection = (): Record<string, { chapter: number | null; subAreas: ApplicableSubArea[] }> => {
    if (!results || !results.applicable_sub_areas) return {};

    const grouped = results.applicable_sub_areas.reduce((acc, subArea) => {
      const sectionName = subArea.section_name;
      if (!acc[sectionName]) {
        acc[sectionName] = {
          chapter: subArea.chapter_number ?? null,
          subAreas: []
        };
      }
      acc[sectionName].subAreas.push(subArea);
      return acc;
    }, {} as Record<string, { chapter: number | null; subAreas: ApplicableSubArea[] }>);

    // Sort sections by chapter number
    return Object.fromEntries(
      Object.entries(grouped).sort(([, a], [, b]) => {
        const chapterA = a.chapter ?? 999;
        const chapterB = b.chapter ?? 999;
        return chapterA - chapterB;
      })
    );
  };

  const getConfidenceBadgeClass = (score: number): string => {
    if (score >= 80) return 'confidence-high';
    if (score >= 60) return 'confidence-medium';
    return 'confidence-low';
  };

  if (loading) {
    return (
      <div className="results-loading">
        <p>Loading results...</p>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="results-error">
        <p className="error-message">{error || 'No results found'}</p>
        <Link to={`/projects/${projectId}/assess`} className="btn-primary">
          Start Assessment
        </Link>
      </div>
    );
  }

  return (
    <div className="applicability-results">
      <div className="results-header">
        <div>
          <h2>Assessment Results</h2>
          <p className="results-summary">
            <strong>{results.applicable_count}</strong> applicable review areas found
          </p>
        </div>
        <div className="results-actions">
          <button
            onClick={() => setGroupBy(groupBy === 'section' ? 'all' : 'section')}
            className="btn-secondary"
          >
            {groupBy === 'section' ? 'Show All' : 'Group by Section'}
          </button>
          <Link to={`/projects/${projectId}/loe`} className="btn-primary">
            View LOE Summary
          </Link>
        </div>
      </div>

      {groupBy === 'section' ? (
        <div className="results-by-section">
          {Object.entries(groupedBySection()).map(([sectionName, { chapter, subAreas }]) => (
            <div key={sectionName} className="section-group">
              <h3 className="section-header">
                {chapter ? `${chapter}. ` : ''}{sectionName}
                <span className="section-count">({subAreas.length} areas)</span>
              </h3>

              <div className="sub-areas-list">
                {subAreas.map((subArea) => (
                  <div key={subArea.sub_area_id} className="sub-area-card">
                    <div className="sub-area-header">
                      <span className="sub-area-id">{subArea.sub_area_id}</span>
                      <span
                        className={`confidence-badge ${getConfidenceBadgeClass(
                          subArea.loe_confidence_score
                        )}`}
                      >
                        {subArea.loe_confidence} ({subArea.loe_confidence_score}%)
                      </span>
                    </div>

                    <h4 className="sub-area-question">{subArea.question}</h4>
                    <p className="sub-area-requirement">{subArea.basic_requirement}</p>

                    <div className="sub-area-footer">
                      <span className="loe-hours">
                        <strong>LOE:</strong> {subArea.loe_hours} hours
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="results-all">
          <div className="sub-areas-list">
            {results?.applicable_sub_areas?.map((subArea) => (
              <div key={subArea.sub_area_id} className="sub-area-card">
                <div className="sub-area-header">
                  <span className="sub-area-id">
                    {subArea.section_id} - {subArea.sub_area_id}
                  </span>
                  <span
                    className={`confidence-badge ${getConfidenceBadgeClass(
                      subArea.loe_confidence_score
                    )}`}
                  >
                    {subArea.loe_confidence} ({subArea.loe_confidence_score}%)
                  </span>
                </div>

                <div className="section-tag">
                  {subArea.chapter_number ? `${subArea.chapter_number}. ` : ''}{subArea.section_name}
                </div>

                <h4 className="sub-area-question">{subArea.question}</h4>
                <p className="sub-area-requirement">{subArea.basic_requirement}</p>

                <div className="sub-area-footer">
                  <span className="loe-hours">
                    <strong>LOE:</strong> {subArea.loe_hours} hours
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
