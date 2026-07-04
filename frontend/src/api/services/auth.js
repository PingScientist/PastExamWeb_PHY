import { api } from './client'

export const authService = {
  login() {
    window.__pastexam?.openLoginModal?.()
  },

  async localLogin(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await api.post('/auth/login', formData)
    return response.data
  },

  async heartbeat() {
    return api.post('/auth/heartbeat')
  },

  logout() {
    return api.post('/auth/logout')
  },
}
