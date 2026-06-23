import { api } from './client'

export const courseService = {
  listCourses() {
    return api.get('/courses')
  },

  getCourseArchives(courseId) {
    return api.get(`/courses/${courseId}/archives`)
  },

  getAllCourses() {
    return api.get('/courses/admin/courses')
  },

  createCourse(courseData) {
    return api.post('/courses/admin/courses', courseData)
  },

  updateCourse(courseId, courseData) {
    return api.put(`/courses/admin/courses/${courseId}`, courseData)
  },

  reorderCourses(category, courseIds) {
    return api.post('/courses/admin/courses/reorder', {
      category,
      course_ids: courseIds,
    })
  },

  deleteCourse(courseId) {
    return api.delete(`/courses/admin/courses/${courseId}`)
  },

  requestCourse(courseData) {
    return api.post('/courses/requests', courseData)
  },

  listMyRequests() {
    return api.get('/courses/requests/me')
  },

  listAdminRequests() {
    return api.get('/courses/admin/requests')
  },

  approveRequest(requestId, note = '') {
    return api.post(`/courses/admin/requests/${requestId}/approve`, { note })
  },

  rejectRequest(requestId, note = '') {
    return api.post(`/courses/admin/requests/${requestId}/reject`, { note })
  },
}
