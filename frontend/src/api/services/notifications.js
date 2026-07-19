import { api } from './client'

const BASE_PATH = '/notifications'

export const notificationService = {
  getActive() {
    return api.get(`${BASE_PATH}/active`)
  },
  getAll() {
    return api.get(BASE_PATH)
  },
  getCenter(params) {
    return api.get(`${BASE_PATH}/center`, { params })
  },
  getCounts() {
    return api.get(`${BASE_PATH}/counts`)
  },
  getUnreadSummary(params) {
    return api.get(`${BASE_PATH}/unread-summary`, { params })
  },
  markAnnouncementRead(id) {
    return api.put(`${BASE_PATH}/announcements/${id}/read`)
  },
  markPersonalRead(id) {
    return api.put(`${BASE_PATH}/personal/${id}/read`)
  },
  markAllPersonalRead() {
    return api.put(`${BASE_PATH}/personal/read-all`)
  },
  markAllRead() {
    return api.put(`${BASE_PATH}/mark-all-read`)
  },
  getAllAdmin() {
    return api.get(`${BASE_PATH}/admin/notifications`)
  },
  create(payload) {
    return api.post(`${BASE_PATH}/admin/notifications`, payload)
  },
  update(id, payload) {
    return api.put(`${BASE_PATH}/admin/notifications/${id}`, payload)
  },
  remove(id) {
    return api.delete(`${BASE_PATH}/admin/notifications/${id}`)
  },
}
