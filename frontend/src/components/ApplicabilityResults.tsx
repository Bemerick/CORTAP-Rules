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
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [expandedAreas, setExpandedAreas] = useState<Set<string>>(new Set());
  const [exporting, setExporting] = useState(false);

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

  const toggleSection = (sectionName: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionName)) {
      newExpanded.delete(sectionName);
    } else {
      newExpanded.add(sectionName);
    }
    setExpandedSections(newExpanded);
  };

  const toggleArea = (subAreaId: string) => {
    const newExpanded = new Set(expandedAreas);
    if (newExpanded.has(subAreaId)) {
      newExpanded.delete(subAreaId);
    } else {
      newExpanded.add(subAreaId);
    }
    setExpandedAreas(newExpanded);
  };

  const calculateSectionSummary = (subAreas: ApplicableSubArea[]) => {
    const totalHours = subAreas.reduce((sum, sa) => sum + sa.loe_hours, 0);
    const avgConfidence = subAreas.reduce((sum, sa) => sum + sa.loe_confidence_score, 0) / subAreas.length;
    const totalIndicators = subAreas.reduce((sum, sa) => sum + (sa.indicators?.length || 0), 0);
    return { totalHours, avgConfidence, totalIndicators };
  };

  const getTotalIndicatorCount = (): number => {
    if (!results || !results.applicable_sub_areas) return 0;
    return results.applicable_sub_areas.reduce((sum, sa) => sum + (sa.indicators?.length || 0), 0);
  };

  const handleExportWorkbook = async () => {
    try {
      setExporting(true);
      await apiService.exportProjectWorkbook(projectId);
    } catch (err) {
      console.error('Failed to export workbook:', err);
      alert('Failed to generate workbook. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="results-loading">
        <div className="loading-container">
          <h3>Loading Assessment Results</h3>
          <div className="progress-bar">
            <div className="progress-bar-fill"></div>
          </div>
          <p>Analyzing your project and determining applicable review areas...</p>
        </div>
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
            <strong>{results.applicable_count}</strong> Questions Examined • <strong>{getTotalIndicatorCount()}</strong> Indicators of Compliance
          </p>
        </div>
        <div className="results-actions">
          <button
            onClick={() => setGroupBy(groupBy === 'section' ? 'all' : 'section')}
            className="btn-secondary"
          >
            {groupBy === 'section' ? 'Show All' : 'Group by Section'}
          </button>
          <button
            onClick={handleExportWorkbook}
            disabled={exporting}
            className="btn-secondary"
          >
            {exporting ? 'Generating...' : 'Generate Scoping Workbook'}
          </button>
          <Link to={`/projects/${projectId}/loe`} className="btn-primary">
            View LOE Summary
          </Link>
        </div>
      </div>

      {groupBy === 'section' ? (
        <div className="results-by-section">
          {Object.entries(groupedBySection()).map(([sectionName, { chapter, subAreas }]) => {
            const { totalHours, avgConfidence, totalIndicators } = calculateSectionSummary(subAreas);
            const isExpanded = expandedSections.has(sectionName);

            return (
              <div key={sectionName} className="section-group">
                <div
                  className="section-summary-card"
                  onClick={() => toggleSection(sectionName)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="section-summary-header">
                    <h3 className="section-title">
                      <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                      {chapter ? `${chapter}. ` : ''}{sectionName}
                    </h3>
                    <div className="section-summary-stats">
                      <span className="section-stat">
                        <strong>{subAreas.length}</strong> questions
                      </span>
                      <span className="section-stat">
                        <strong>{totalIndicators}</strong> indicators
                      </span>
                      <span className="section-stat">
                        <strong>{totalHours.toFixed(1)}</strong> hours
                      </span>
                      <span
                        className={`confidence-badge ${getConfidenceBadgeClass(avgConfidence)}`}
                      >
                        {avgConfidence.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <div className="sub-areas-list">
                    {subAreas.map((subArea) => {
                      const isAreaExpanded = expandedAreas.has(subArea.sub_area_id);
                      return (
                        <div key={subArea.sub_area_id} className="sub-area-card">
                          <div
                            className="sub-area-header"
                            onClick={() => toggleArea(subArea.sub_area_id)}
                            style={{ cursor: 'pointer' }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span className="expand-icon">{isAreaExpanded ? '▼' : '▶'}</span>
                              <span className="sub-area-id">{subArea.sub_area_id}</span>
                            </div>
                            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                              <span className="indicator-count">
                                {subArea.indicators?.length || 0} indicators
                              </span>
                              <span
                                className={`confidence-badge ${getConfidenceBadgeClass(
                                  subArea.loe_confidence_score
                                )}`}
                              >
                                {subArea.loe_confidence} ({subArea.loe_confidence_score}%)
                              </span>
                            </div>
                          </div>

                          <h4 className="sub-area-question">{subArea.question}</h4>
                          <p className="sub-area-requirement">{subArea.basic_requirement}</p>

                          {isAreaExpanded && subArea.indicators && subArea.indicators.length > 0 && (
                            <div className="indicators-list">
                              <h5 className="indicators-title">Indicators of Compliance:</h5>
                              <ul className="indicators-ul">
                                {subArea.indicators.map((indicator) => (
                                  <li key={indicator.id} className="indicator-item">
                                    <strong>{indicator.indicator_id}:</strong> {indicator.text}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          <div className="sub-area-footer">
                            <span className="loe-hours">
                              <strong>LOE:</strong> {subArea.loe_hours} hours
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="results-all">
          <div className="sub-areas-list">
            {results?.applicable_sub_areas?.map((subArea) => {
              const isAreaExpanded = expandedAreas.has(subArea.sub_area_id);
              return (
                <div key={subArea.sub_area_id} className="sub-area-card">
                  <div
                    className="sub-area-header"
                    onClick={() => toggleArea(subArea.sub_area_id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="expand-icon">{isAreaExpanded ? '▼' : '▶'}</span>
                      <span className="sub-area-id">
                        {subArea.section_id} - {subArea.sub_area_id}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <span className="indicator-count">
                        {subArea.indicators?.length || 0} indicators
                      </span>
                      <span
                        className={`confidence-badge ${getConfidenceBadgeClass(
                          subArea.loe_confidence_score
                        )}`}
                      >
                        {subArea.loe_confidence} ({subArea.loe_confidence_score}%)
                      </span>
                    </div>
                  </div>

                  <div className="section-tag">
                    {subArea.chapter_number ? `${subArea.chapter_number}. ` : ''}{subArea.section_name}
                  </div>

                  <h4 className="sub-area-question">{subArea.question}</h4>
                  <p className="sub-area-requirement">{subArea.basic_requirement}</p>

                  {isAreaExpanded && subArea.indicators && subArea.indicators.length > 0 && (
                    <div className="indicators-list">
                      <h5 className="indicators-title">Indicators of Compliance:</h5>
                      <ul className="indicators-ul">
                        {subArea.indicators.map((indicator) => (
                          <li key={indicator.id} className="indicator-item">
                            <strong>{indicator.indicator_id}:</strong> {indicator.text}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="sub-area-footer">
                    <span className="loe-hours">
                      <strong>LOE:</strong> {subArea.loe_hours} hours
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
