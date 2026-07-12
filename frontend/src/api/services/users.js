import { api } from './client'

export const userService = {
  getMe() {
    return api.get('/users/me')
  },

  updateMyDiscussionSettings(nickname, showLevelTitle) {
    return api.patch('/users/me/nickname', {
      nickname,
      show_level_title: showLevelTitle,
    })
  },

  updateMyNickname(nickname) {
    return api.patch('/users/me/nickname', { nickname })
  },
}
