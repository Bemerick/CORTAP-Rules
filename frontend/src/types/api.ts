/**
 * TypeScript interfaces for FastAPI backend
 * These mirror the Pydantic schemas in the backend
 */

// Question types
export interface Question {
  id: number;
  question_number: number;
  question_text: string;
  category?: string;
}

// Section types
export interface Section {
  id: number;
  section_id: string;
  section_name: string;
  description?: string;
  display_order: number;
}

export interface SectionSummary extends Section {
  sub_area_count: number;
  total_loe_hours: number;
  avg_loe_hours: number;
  avg_confidence_score: number;
}

// SubArea types
export interface Indicator {
  id: number;
  sub_area_id: string;
  indicator_text: string;
  indicator_order: number;
}

export interface Deficiency {
  id: number;
  sub_area_id: string;
  deficiency_text: string;
  deficiency_order: number;
}

export interface SubArea {
  id: number;
  section_id: string;
  sub_area_id: string;
  question: string;
  basic_requirement: string;
  applicability: string;
  loe_hours?: number;
  loe_confidence?: string;
  loe_confidence_score?: number;
}

export interface SubAreaDetail extends SubArea {
  detailed_explanation?: string;
  instructions_for_reviewer?: string;
  loe_reasoning?: string;
  indicators: Indicator[];
  deficiencies: Deficiency[];
}

// Project types
export interface Project {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
}

export interface ProjectAnswers {
  answers: Record<string, string>;
}

export interface IndicatorOfCompliance {
  id: number;
  indicator_id: string;
  text: string;
}

export interface ApplicableSubArea {
  section_id: string;
  section_name: string;
  chapter_number?: number;
  sub_area_id: string;
  question: string;
  basic_requirement: string;
  loe_hours: number;
  loe_confidence: string;
  loe_confidence_score: number;
  indicators: IndicatorOfCompliance[];
}

export interface ProjectApplicabilityResult {
  project_id: number;
  applicable_count: number;
  applicable_sub_areas: ApplicableSubArea[];
}

export interface SectionLOESummary {
  section_id: string;
  section_name: string;
  chapter_number?: number;
  sub_area_count: number;
  total_hours: number;
  avg_confidence_score: number;
}

export interface ProjectLOESummary {
  project_id: number;
  project_name: string;
  total_sub_areas: number;
  total_hours: number;
  avg_confidence_score: number;
  sections: SectionLOESummary[];
}

// Assessment types
export interface AssessmentRequest {
  answers: Record<string, string>;
}

export interface AssessmentResult {
  applicable_count: number;
  applicable_sub_areas: ApplicableSubArea[];
}
