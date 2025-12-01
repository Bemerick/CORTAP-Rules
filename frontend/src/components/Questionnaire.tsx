/**
 * Questionnaire Component
 * Displays assessment questions and collects user answers
 */

import { useState, useEffect } from 'react';
import type { Question } from '../types/api';
import apiService from '../services/api';

interface QuestionnaireProps {
  onSubmit: (answers: Record<number, string>) => void;
  onCancel?: () => void;
  initialAnswers?: Record<number, string>;
}

// Question options hardcoded for the 12 assessment questions
const QUESTION_OPTIONS: Record<number, { value: string; label: string }[]> = {
  1: [
    { value: 'all', label: 'All recipients' },
    { value: 'state', label: 'State recipient' },
    { value: 'non_state', label: 'Non-state recipient' },
  ],
  2: [
    { value: 'less_750k', label: 'Less than $750,000' },
    { value: 'gte_750k', label: '$750,000 or more' },
  ],
  3: [
    { value: 'yes', label: 'Yes' },
    { value: 'no', label: 'No' },
  ],
  4: [
    { value: 'yes', label: 'Yes' },
    { value: 'no', label: 'No' },
  ],
  5: [
    { value: 'tier_1', label: 'Tier I' },
    { value: 'tier_2', label: 'Tier II' },
    { value: 'na', label: 'Not applicable' },
  ],
  6: [
    { value: '5310', label: 'Section 5310' },
    { value: '5311', label: 'Section 5311' },
    { value: '5307', label: 'Section 5307' },
    { value: '5337', label: 'Section 5337' },
    { value: 'other', label: 'Other funds' },
  ],
  7: [
    { value: 'fixed_route', label: 'Fixed-route service' },
    { value: 'demand_response', label: 'Demand response' },
    { value: 'commuter_rail', label: 'Commuter rail' },
    { value: 'commuter_bus', label: 'Commuter bus' },
    { value: 'other', label: 'Other' },
  ],
  8: [
    { value: 'yes', label: 'Yes' },
    { value: 'no', label: 'No' },
  ],
  9: [
    { value: 'yes', label: 'Yes' },
    { value: 'no', label: 'No' },
  ],
  10: [
    { value: 'participant', label: 'Participant' },
    { value: 'sponsor', label: 'Sponsor' },
    { value: 'na', label: 'Not applicable' },
  ],
  11: [
    { value: 'yes', label: 'Yes' },
    { value: 'no', label: 'No' },
  ],
  12: [
    { value: 'yes', label: 'Yes' },
    { value: 'no', label: 'No' },
  ],
};

// Questions 6 and 7 allow multiple selections
const MULTI_SELECT_QUESTIONS = [6, 7];

export default function Questionnaire({
  onSubmit,
  onCancel,
  initialAnswers = {},
}: QuestionnaireProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>(initialAnswers);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const data = await apiService.getQuestions();
      setQuestions(data.sort((a, b) => a.question_number - b.question_number));
      setError(null);
    } catch (err) {
      console.error('Failed to load questions:', err);
      setError('Failed to load questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRadioChange = (questionId: number, value: string) => {
    setAnswers({ ...answers, [questionId]: value });
  };

  const handleCheckboxChange = (questionId: number, value: string) => {
    const currentValues = answers[questionId] ? answers[questionId].split(',') : [];
    const newValues = currentValues.includes(value)
      ? currentValues.filter((v: string) => v !== value)
      : [...currentValues, value];
    setAnswers({ ...answers, [questionId]: newValues.join(',') });
  };

  const isCheckboxChecked = (questionId: number, value: string): boolean => {
    const currentValues = answers[questionId] ? answers[questionId].split(',') : [];
    return currentValues.includes(value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all questions are answered
    const missingRequired = questions
      .filter((q) => !answers[q.id])
      .map((q) => q.question_text);

    if (missingRequired.length > 0) {
      alert(`Please answer all questions:\n${missingRequired.join('\n')}`);
      return;
    }

    onSubmit(answers);
  };

  if (loading) {
    return (
      <div className="questionnaire-loading">
        <p>Loading questions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="questionnaire-error">
        <p className="error-message">{error}</p>
        <button onClick={loadQuestions}>Retry</button>
      </div>
    );
  }

  return (
    <form className="questionnaire" onSubmit={handleSubmit}>
      <div className="questionnaire-header">
        <h2>FTA Comprehensive Review Assessment</h2>
        <p>Please answer the following questions to determine applicable review areas.</p>
      </div>

      <div className="questions-container">
        {questions.map((question) => {
          const options = QUESTION_OPTIONS[question.question_number] || [];
          const isMultiSelect = MULTI_SELECT_QUESTIONS.includes(question.question_number);

          return (
            <div key={question.id} className="question-block">
              <label className="question-label">
                {question.question_text}
                <span className="required">*</span>
              </label>

              <div className="options-container">
                {isMultiSelect ? (
                  // Checkbox for multi-select questions
                  <>
                    {options.map((option, idx) => (
                      <label key={idx} className="option-label">
                        <input
                          type="checkbox"
                          name={`question_${question.id}`}
                          value={option.value}
                          checked={isCheckboxChecked(question.id, option.value)}
                          onChange={(e) =>
                            handleCheckboxChange(question.id, e.target.value)
                          }
                        />
                        <span>{option.label}</span>
                      </label>
                    ))}
                  </>
                ) : (
                  // Radio for single-select questions
                  <>
                    {options.map((option, idx) => (
                      <label key={idx} className="option-label">
                        <input
                          type="radio"
                          name={`question_${question.id}`}
                          value={option.value}
                          checked={answers[question.id] === option.value}
                          onChange={(e) =>
                            handleRadioChange(question.id, e.target.value)
                          }
                        />
                        <span>{option.label}</span>
                      </label>
                    ))}
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="questionnaire-actions">
        {onCancel && (
          <button type="button" className="btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
        <button type="submit" className="btn-primary">
          Submit Assessment
        </button>
      </div>
    </form>
  );
}
