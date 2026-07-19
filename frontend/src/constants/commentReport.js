export const COMMENT_REPORT_CUSTOM_MESSAGE_MAX_LENGTH = 200
export const COMMENT_REPORT_OTHER_REASON = 'other'
export const COMMENT_REPORT_SUBMISSION_AVAILABLE = false

export const COMMENT_REPORT_REASONS = Object.freeze([
  { label: '垃圾訊息或重複洗版', value: 'spam_or_duplicate' },
  { label: '攻擊、騷擾或不友善內容', value: 'harassment_or_hostility' },
  { label: '不當或違法內容', value: 'inappropriate_or_illegal' },
  { label: '洩漏個人資料或隱私', value: 'privacy_violation' },
  { label: '錯誤或誤導資訊', value: 'misinformation' },
  { label: '其他', value: COMMENT_REPORT_OTHER_REASON },
])

export function buildCommentReportPayload(commentId, reportReason, customMessage = '') {
  return {
    comment_id: Number(commentId),
    report_reason: reportReason,
    custom_message:
      reportReason === COMMENT_REPORT_OTHER_REASON ? String(customMessage).trim() : null,
  }
}
