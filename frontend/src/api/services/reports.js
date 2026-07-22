import { api } from './client'

export const reportService = {
  createSystemIssue(payload) {
    return api.post('/reports/system-issues', payload)
  },
  listSystemIssues(params) {
    return api.get('/reports/admin/system-issues', { params })
  },
  deleteSystemIssue(id) {
    return api.delete(`/reports/admin/system-issues/${id}`)
  },
  listCommentReports(params) {
    return api.get('/reports/admin/comments', { params })
  },
  getCommentReport(id) {
    return api.get(`/reports/admin/comments/${id}`)
  },
  deleteCommentReport(id) {
    return api.delete(`/reports/admin/comments/${id}`)
  },
  reviewCommentReport(id, payload) {
    return api.patch(`/reports/admin/comments/${id}`, payload)
  },
}
