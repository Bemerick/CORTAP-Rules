/**
 * API Service Layer
 * Provides typed methods for communicating with the FastAPI backend
 */

import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type {
  Question,
  Section,
  SectionSummary,
  SubArea,
  SubAreaDetail,
  Project,
  ProjectCreate,
  ProjectUpdate,
  ProjectAnswers,
  ProjectApplicabilityResult,
  ProjectLOESummary,
  AssessmentRequest,
  AssessmentResult,
} from '../types/api';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Questions API
  async getQuestions(): Promise<Question[]> {
    const response = await this.client.get('/api/questions');
    return response.data;
  }

  async getQuestion(id: number): Promise<Question> {
    const response = await this.client.get(`/api/questions/${id}`);
    return response.data;
  }

  // Sections API
  async getSections(): Promise<Section[]> {
    const response = await this.client.get('/api/sections');
    return response.data;
  }

  async getSectionsSummary(): Promise<SectionSummary[]> {
    const response = await this.client.get('/api/sections/summary');
    return response.data;
  }

  async getSection(id: string): Promise<Section> {
    const response = await this.client.get(`/api/sections/${id}`);
    return response.data;
  }

  // Sub-Areas API
  async getSubAreas(sectionId?: string): Promise<SubArea[]> {
    const params = sectionId ? { section_id: sectionId } : {};
    const response = await this.client.get('/api/sub-areas', { params });
    return response.data;
  }

  async getSubArea(id: number): Promise<SubAreaDetail> {
    const response = await this.client.get(`/api/sub-areas/${id}`);
    return response.data;
  }

  // Projects API
  async getProjects(): Promise<Project[]> {
    const response = await this.client.get('/api/projects');
    return response.data;
  }

  async createProject(data: ProjectCreate): Promise<Project> {
    const response = await this.client.post('/api/projects', data);
    return response.data;
  }

  async getProject(id: number): Promise<Project> {
    const response = await this.client.get(`/api/projects/${id}`);
    return response.data;
  }

  async updateProject(id: number, data: ProjectUpdate): Promise<Project> {
    const response = await this.client.put(`/api/projects/${id}`, data);
    return response.data;
  }

  async deleteProject(id: number): Promise<void> {
    await this.client.delete(`/api/projects/${id}`);
  }

  async submitProjectAnswers(
    id: number,
    answers: ProjectAnswers
  ): Promise<ProjectApplicabilityResult> {
    const response = await this.client.post(`/api/projects/${id}/answers`, answers);
    return response.data;
  }

  async getProjectApplicableSubAreas(id: number): Promise<ProjectApplicabilityResult> {
    const response = await this.client.get(`/api/projects/${id}/applicable-sub-areas`);
    return response.data;
  }

  async getProjectLOESummary(id: number): Promise<ProjectLOESummary> {
    const response = await this.client.get(`/api/projects/${id}/loe-summary`);
    return response.data;
  }

  async exportProjectWorkbook(id: number): Promise<void> {
    const response = await this.client.get(`/api/projects/${id}/export-workbook`, {
      responseType: 'blob',
    });

    // Extract filename from Content-Disposition header
    const contentDisposition = response.headers['content-disposition'];
    let filename = `Project-${id}-Scoping-Workbook.xlsx`;

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/);
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1]);
      }
    }

    // Create blob and trigger download
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  // Assessment API
  async assess(data: AssessmentRequest): Promise<AssessmentResult> {
    const response = await this.client.post('/api/assess', data);
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
