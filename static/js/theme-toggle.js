(function() {
  const STORAGE_KEY = 'ctfmn-theme'
  const THEME_VALUES = new Set(['system', 'dark', 'light'])
  const LABELS = {
    system: 'Theme: System',
    dark: 'Theme: Dark',
    light: 'Theme: Light',
  }
  const button = document.getElementById('theme-toggle')
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

  const getMode = () => {
    try {
      const mode = localStorage.getItem(STORAGE_KEY)
      return THEME_VALUES.has(mode) ? mode : 'system'
    } catch (_error) {
      return 'system'
    }
  }

  const applyTheme = (mode) => {
    const isDark = mode === 'dark' || (mode === 'system' && mediaQuery.matches)
    document.documentElement.classList.toggle('dark', isDark)
    document.documentElement.style.colorScheme = isDark ? 'dark' : 'light'

    if (button) {
      const label = LABELS[mode] || LABELS.system
      button.textContent = label
      button.setAttribute('aria-label', label)
      button.setAttribute('aria-pressed', (mode !== 'system').toString())
    }
  }

  const cycleTheme = () => {
    const current = getMode()
    const next = current === 'system' ? 'dark' : current === 'dark' ? 'light' : 'system'
    try {
      localStorage.setItem(STORAGE_KEY, next)
    } catch (_error) {}
    applyTheme(next)
  }

  if (button) {
    button.addEventListener('click', cycleTheme)
  }

  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', () => {
      if (getMode() === 'system') {
        applyTheme('system')
      }
    })
  } else if (mediaQuery.addListener) {
    mediaQuery.addListener(() => {
      if (getMode() === 'system') {
        applyTheme('system')
      }
    })
  }

  applyTheme(getMode())
})()
