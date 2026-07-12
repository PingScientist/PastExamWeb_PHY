export const SUBMISSION_LEVELS = [
  { level: 1, name: '新手投稿者', minExp: 0 },
  { level: 2, name: '初階整理者', minExp: 2 },
  { level: 3, name: '穩定投稿者', minExp: 5 },
  { level: 4, name: '認真貢獻者', minExp: 9 },
  { level: 5, name: '經典整理師', minExp: 14 },
  { level: 6, name: '題庫建設者', minExp: 20 },
  { level: 7, name: '資源探索者', minExp: 27 },
  { level: 8, name: '校園收藏家', minExp: 35 },
  { level: 9, name: '傳奇貢獻者', minExp: 44 },
  { level: 10, name: '題庫宗師', minExp: 54 },
]

export function resolveSubmissionLevel(experience) {
  const currentExp = Math.max(0, Number(experience) || 0)
  const currentLevel = SUBMISSION_LEVELS.reduce(
    (matchedLevel, level) => (currentExp >= level.minExp ? level : matchedLevel),
    SUBMISSION_LEVELS[0]
  )
  const nextLevel = SUBMISSION_LEVELS[currentLevel.level]
  if (!nextLevel) {
    return {
      ...currentLevel,
      currentExp,
      isMaxLevel: true,
      progressInLevel: 1,
      progressRange: 1,
      progressPercent: 100,
      expToNextLevel: 0,
    }
  }
  const progressRange = nextLevel.minExp - currentLevel.minExp
  const progressInLevel = Math.max(0, currentExp - currentLevel.minExp)
  return {
    ...currentLevel,
    currentExp,
    isMaxLevel: false,
    progressInLevel,
    progressRange,
    progressPercent: Math.min(100, (progressInLevel / progressRange) * 100),
    expToNextLevel: Math.max(0, nextLevel.minExp - currentExp),
  }
}

export function formatSubmissionLevelTitle(experience) {
  const level = resolveSubmissionLevel(experience)
  return `Lv.${level.level} ${level.name}`
}
