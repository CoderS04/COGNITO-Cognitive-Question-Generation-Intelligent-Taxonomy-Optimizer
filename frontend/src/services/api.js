import axios from 'axios';

const API_BASE = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Courses & Syllabus
  getCourses: () => apiClient.get('/courses'),
  getCourseDetail: (id) => apiClient.get(`/courses/${id}`),
  createCourse: (data) => apiClient.post('/courses', data),
  addUnit: (courseId, data) => apiClient.post(`/courses/${courseId}/units`, data),

  // Questions & Analysis
  getQuestions: (params) => apiClient.get('/questions', { params }),
  addQuestion: (data) => apiClient.post('/questions', data),
  analyzeQuestion: (data) => apiClient.post('/questions/analyze', data),
  reframeQuestion: (data) => apiClient.post('/questions/reframe', data),
  updateQuestion: (id, data) => apiClient.put(`/questions/${id}`, data),
  deleteQuestion: (id) => apiClient.delete(`/questions/${id}`),
  bulkDeleteQuestions: (ids) => apiClient.post('/questions/bulk-delete', { question_ids: ids }),
  checkSimilarity: (data) => apiClient.post('/questions/similarity-check', data),

  // Templates
  getTemplates: () => apiClient.get('/templates'),
  createTemplate: (data) => apiClient.post('/templates', data),
  getTemplateDetail: (id) => apiClient.get(`/templates/${id}`),
  updateTemplate: (id, data) => apiClient.put(`/templates/${id}`, data),
  deleteTemplate: (id) => apiClient.delete(`/templates/${id}`),

  // Exam Papers & Optimization
  getPapers: () => apiClient.get('/papers'),
  getPaperDetail: (id) => apiClient.get(`/papers/${id}`),
  generatePaper: (data) => apiClient.post('/papers/generate', data),
  replaceQuestion: (paperId, data) => apiClient.put(`/papers/${paperId}/replace-question`, data),
  savePaperQuestions: (paperId, data) => apiClient.post(`/papers/${paperId}/save-questions`, data),
  deletePaper: (id) => apiClient.delete(`/papers/${id}`),

  // Validation Engine
  validatePaper: (paperId) => apiClient.post(`/validation/validate/${paperId}`),
  autoRefinePaper: (paperId) => apiClient.post(`/validation/auto-refine/${paperId}`),

  // Analytics & Reporting
  getPaperAnalytics: (paperId) => apiClient.get(`/analytics/paper/${paperId}`),
  getSystemStats: () => apiClient.get('/analytics/overview'),

  // Document Ingestion
  uploadDocument: (formData) => apiClient.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  approveDocument: (documentId, data) => apiClient.post(`/documents/${documentId}/approve`, data),
  getQuestionAlternatives: (paperId, paperQuestionId) =>
    apiClient.get(`/papers/${paperId}/questions/${paperQuestionId}/alternatives`),
  getDocuments: () => apiClient.get('/documents'),

  // Export URLs
  getPdfDownloadUrl: (id) => `${API_BASE}/export/paper/${id}/pdf`,
  getDocxDownloadUrl: (id) => `${API_BASE}/export/paper/${id}/docx`,
  getJsonDownloadUrl: (id) => `${API_BASE}/export/paper/${id}/json`,
};

export default api;
