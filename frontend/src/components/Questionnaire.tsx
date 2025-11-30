/**
 * Questionnaire Component
 * Displays assessment questions and collects user answers
 */

import { useState, useEffect } from 'react';
import type { Question } from '../types/api';
import apiService from '../services/api';

interface QuestionnaireProps {
  onSubmit: (answers: Record<string, string>) => void;
  onCancel?: () => void;
  initialAnswers?: Record<string, string>;
}

export default function Questionnaire({
  onSubmit,
  onCancel,
  initialAnswers = {},
}: QuestionnaireProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>(initialAnswers);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const data = await apiService.getQuestions();
      setQuestions(data.sort((a, b) => a.display_order - b.display_order));
      setError(null);
    } catch (err) {
      console.error('Failed to load questions:', err);
      setError('Failed to load questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRadioChange = (questionKey: string, value: string) => {
    setAnswers({ ...answers, [questionKey]: value });
  };

  const handleCheckboxChange = (questionKey: string, value: string) => {
    const currentValues = answers[questionKey] ? JSON.parse(answers[questionKey]) : [];
    const newValues = currentValues.includes(value)
      ? currentValues.filter((v: string) => v !== value)
      : [...currentValues, value];
    setAnswers({ ...answers, [questionKey]: JSON.stringify(newValues) });
  };

  const isCheckboxChecked = (questionKey: string, value: string): boolean => {
    const currentValues = answers[questionKey] ? JSON.parse(answers[questionKey]) : [];
    return currentValues.includes(value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate required questions
    const missingRequired = questions
      .filter((q) => q.is_required && !answers[q.question_key])
      .map((q) => q.question_text);

    if (missingRequired.length > 0) {
      alert(`Please answer all required questions:\n${missingRequired.join('\n')}`);
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
        {questions.map((question) => (
          <div key={question.id} className="question-block">
            <label className="question-label">
              {question.question_text}
              {question.is_required && <span className="required">*</span>}
            </label>

            {question.help_text && (
              <p className="help-text">{question.help_text}</p>
            )}

            <div className="options-container">
              {question.question_type === 'radio' && (
                <>
                  {question.options?.map((option) => (
                    <label key={option.id} className="option-label">
                      <input
                        type="radio"
                        name={question.question_key}
                        value={option.option_value}
                        checked={answers[question.question_key] === option.option_value}
                        onChange={(e) =>
                          handleRadioChange(question.question_key, e.target.value)
                        }
                      />
                      <span>{option.option_label}</span>
                    </label>
                  ))}
                </>
              )}

              {question.question_type === 'checkbox' && (
                <>
                  {question.options?.map((option) => (
                    <label key={option.id} className="option-label">
                      <input
                        type="checkbox"
                        name={question.question_key}
                        value={option.option_value}
                        checked={isCheckboxChecked(
                          question.question_key,
                          option.option_value
                        )}
                        onChange={(e) =>
                          handleCheckboxChange(question.question_key, e.target.value)
                        }
                      />
                      <span>{option.option_label}</span>
                    </label>
                  ))}
                </>
              )}
            </div>
          </div>
        ))}
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
