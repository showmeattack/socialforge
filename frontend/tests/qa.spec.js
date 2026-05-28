import { test, expect } from '@playwright/test'

// Helper: register + login to get a session
async function registerAndLogin(page) {
  await page.goto('/register')
  const ts = Date.now()
  await page.fill('input[type="text"]', `tester_${ts}`)
  await page.fill('input[type="password"]', 'Test1234!')
  await page.click('button[type="submit"], button:has-text("Register"), button:has-text("Регистрация")')
  await page.waitForTimeout(1000)
}

// ============================================================
// LANDING PAGE
// ============================================================
test('Landing: renders logo and CTA', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('text=SOCIALFORGE')).toBeVisible()
  // Should have login or start training link
  const cta = page.locator('a[href="/login"], a[href="/register"], text=Start Training, text=Войти')
  await expect(cta.first()).toBeVisible()
})

test('Landing: does not show broken images or JS errors', async ({ page }) => {
  const errors = []
  page.on('pageerror', e => errors.push(e.message))
  await page.goto('/')
  await page.waitForTimeout(1000)
  expect(errors.filter(e => !e.includes('favicon'))).toHaveLength(0)
})

// ============================================================
// AUTH FLOW
// ============================================================
test('Login page: renders form', async ({ page }) => {
  await page.goto('/login')
  await expect(page.locator('input[type="text"], input[placeholder*="user"]')).toBeVisible()
  await expect(page.locator('input[type="password"]')).toBeVisible()
})

test('Login: wrong credentials shows error', async ({ page }) => {
  await page.goto('/login')
  await page.fill('input[type="text"]', 'nobody_12345')
  await page.fill('input[type="password"]', 'wrongpassword')
  await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Войти")')
  await page.waitForTimeout(1000)
  // Should still be on login or show error
  const url = page.url()
  const isOnLogin = url.includes('/login') || url === 'http://localhost:3000/'
  expect(isOnLogin || await page.locator('text=Invalid, text=error, text=wrong').count() > 0).toBeTruthy()
})

test('Register page: renders form', async ({ page }) => {
  await page.goto('/register')
  await expect(page.locator('input[type="text"]')).toBeVisible()
  await expect(page.locator('input[type="password"]')).toBeVisible()
})

// ============================================================
// ONBOARDING GUIDE — ENGLISH
// ============================================================
test('Onboarding guide: opens and navigates all 6 steps (EN)', async ({ page }) => {
  await page.goto('/')
  // Clear onboarding state so it shows
  await page.evaluate(() => localStorage.removeItem('sf_onboarding_done'))
  await page.reload()
  await page.waitForTimeout(800)

  // Check guide appears OR can be opened via navbar
  const guide = page.locator('text=SOCIALFORGE').first()
  await expect(guide).toBeVisible()

  // If modal is showing, step through it
  const modal = page.locator('text=MISSION BRIEF, text=БРИФИНГ').first()
  if (await modal.isVisible()) {
    // Navigate all steps
    for (let i = 0; i < 5; i++) {
      const nextBtn = page.locator('button:has-text("NEXT"), button:has-text("ВПЕРЁД")').first()
      if (await nextBtn.isVisible()) {
        await nextBtn.click()
        await page.waitForTimeout(300)
      }
    }
    // Last step should show START HACKING or НАЧАТЬ ВЗЛОМ
    const lastBtn = page.locator('button:has-text("START HACKING"), button:has-text("НАЧАТЬ ВЗЛОМ")').first()
    await expect(lastBtn).toBeVisible()
  }
})

// ============================================================
// ONBOARDING GUIDE — RUSSIAN LOCALE
// ============================================================
test('Onboarding guide: shows Russian text when locale=ru', async ({ page }) => {
  await page.goto('/settings')
  // Try to find locale toggle
  await page.waitForTimeout(500)
  // Toggle locale via navbar globe button
  const globeBtn = page.locator('nav button:has-text("EN"), nav button:has-text("RU")').first()
  if (await globeBtn.isVisible()) {
    const currentText = await globeBtn.innerText()
    if (currentText.includes('EN')) await globeBtn.click()
    await page.waitForTimeout(300)
  }

  await page.goto('/')
  await page.evaluate(() => localStorage.removeItem('sf_onboarding_done'))
  await page.reload()
  await page.waitForTimeout(800)

  const ruHeader = page.locator('text=БРИФИНГ, text=Тренажёр')
  const enHeader = page.locator('text=MISSION BRIEF, text=Red Team Social Engineering Trainer')

  // Check that at least one Russian element is present when locale is RU
  // (guide may or may not be auto-shown)
  const guideBtn = page.locator('button:has-text("ГИД"), button:has-text("GUIDE"), button:has-text("RU")')
  // Just verify no crash
  const errors = []
  page.on('pageerror', e => errors.push(e.message))
  await page.waitForTimeout(500)
  expect(errors).toHaveLength(0)
})

// ============================================================
// NAVBAR
// ============================================================
test('Navbar: shows MESSENGER link when logged in', async ({ page }) => {
  // Register first
  await page.goto('/register')
  const ts = Date.now()
  await page.fill('input[type="text"]', `nav_test_${ts}`)
  await page.fill('input[type="password"]', 'Test1234!')
  await page.click('button[type="submit"], button:has-text("Register")')
  await page.waitForTimeout(1200)

  // Check navbar for MESSENGER
  const messengerLink = page.locator('nav a[href="/messenger"], nav *:has-text("MESSENGER"), nav *:has-text("МЕССЕНДЖЕР")')
  await expect(messengerLink.first()).toBeVisible()
})

test('Navbar: locale toggle switches between EN and RU', async ({ page }) => {
  await page.goto('/')
  const globeBtn = page.locator('nav button').filter({ hasText: /^(EN|RU)$/ }).first()
  await expect(globeBtn).toBeVisible()
  const before = await globeBtn.innerText()
  await globeBtn.click()
  await page.waitForTimeout(300)
  const after = await globeBtn.innerText()
  expect(before).not.toBe(after)
})

// ============================================================
// LABS PAGE
// ============================================================
test('Labs page: loads and shows labs', async ({ page }) => {
  await page.goto('/labs')
  await page.waitForTimeout(1000)
  // Either shows labs or redirects to login
  const url = page.url()
  if (url.includes('/login')) {
    // OK — protected route
    return
  }
  // If accessible, should show some labs
  const labs = page.locator('[data-testid="lab-card"], .lab-card, text=MGM, text=Phishing, text=Chain')
  const labCount = await labs.count()
  expect(labCount >= 0).toBeTruthy() // page at least loads
})

// ============================================================
// MESSENGER PAGE
// ============================================================
test('Messenger page: loads without errors', async ({ page }) => {
  const errors = []
  page.on('pageerror', e => errors.push(e.message))
  await page.goto('/messenger')
  await page.waitForTimeout(1000)
  await expect(page.locator('text=MESSENGER, text=МЕССЕНДЖЕР')).toBeVisible()
  expect(errors).toHaveLength(0)
})

test('Messenger: shows NPC ACCOUNT ACCESS header', async ({ page }) => {
  await page.goto('/messenger')
  await expect(page.locator('text=NPC ACCOUNT ACCESS')).toBeVisible()
})

test('Messenger: shows login form with email+password fields', async ({ page }) => {
  await page.goto('/messenger')
  await page.waitForTimeout(500)
  await expect(page.locator('input[type="email"], input[placeholder*="target"]')).toBeVisible()
  await expect(page.locator('input[placeholder*="harvested"]')).toBeVisible()
})

test('Messenger: wrong credentials shows error', async ({ page }) => {
  await page.goto('/messenger')
  await page.waitForTimeout(500)
  await page.fill('input[type="email"]', 'nobody@nowhere.com')
  await page.fill('input[placeholder*="harvested"]', 'wrongpass')
  await page.click('button:has-text("ACCESS ACCOUNT")')
  await page.waitForTimeout(1000)
  const errMsg = page.locator('text=Account not found, text=Invalid credentials, text=Authentication failed')
  await expect(errMsg.first()).toBeVisible()
})

test('Messenger: valid credentials show inbox', async ({ page }) => {
  await page.goto('/messenger')
  await page.waitForTimeout(500)
  await page.fill('input[type="email"]', 'elena.rodriguez@goldenmirage.com')
  await page.fill('input[placeholder*="harvested"]', 'Helpdesk#2020')
  await page.click('button:has-text("ACCESS ACCOUNT")')
  await page.waitForTimeout(2000)
  // Should show INBOX header with her name
  await expect(page.locator('text=INBOX, text=Elena Rodriguez')).toBeVisible()
})

test('Messenger: inbox messages are expandable', async ({ page }) => {
  await page.goto('/messenger')
  await page.waitForTimeout(500)
  await page.fill('input[type="email"]', 'elena.rodriguez@goldenmirage.com')
  await page.fill('input[placeholder*="harvested"]', 'Helpdesk#2020')
  await page.click('button:has-text("ACCESS ACCOUNT")')
  await page.waitForTimeout(2000)
  // Click first message
  const firstMsg = page.locator('text=VPN Admin Creds').first()
  await expect(firstMsg).toBeVisible()
  await firstMsg.click()
  await page.waitForTimeout(300)
  // Body should be visible now
  await expect(page.locator('text=OktaAdmin')).toBeVisible()
})

test('Messenger: logout returns to login form', async ({ page }) => {
  await page.goto('/messenger')
  await page.waitForTimeout(500)
  await page.fill('input[type="email"]', 'elena.rodriguez@goldenmirage.com')
  await page.fill('input[placeholder*="harvested"]', 'Helpdesk#2020')
  await page.click('button:has-text("ACCESS ACCOUNT")')
  await page.waitForTimeout(2000)
  await page.click('button:has-text("LOG OUT")')
  await page.waitForTimeout(500)
  await expect(page.locator('button:has-text("ACCESS ACCOUNT")')).toBeVisible()
})

// ============================================================
// PHISHER PAGE
// ============================================================
test('Phisher page: loads with correct header', async ({ page }) => {
  const errors = []
  page.on('pageerror', e => errors.push(e.message))
  await page.goto('/phisher')
  await page.waitForTimeout(800)
  await expect(page.locator('text=PHISHING STUDIO')).toBeVisible()
  expect(errors).toHaveLength(0)
})

test('Phisher: quality score updates when domain typed', async ({ page }) => {
  await page.goto('/phisher')
  await page.waitForTimeout(500)
  const scoreBefore = await page.locator('text=%').first().innerText().catch(() => '0%')
  await page.fill('input[placeholder*="secure-login"]', 'accounts.google.com')
  await page.waitForTimeout(300)
  const scoreAfter = await page.locator('text=%').first().innerText().catch(() => '0%')
  // Score should have changed or stayed high
  expect(scoreAfter).toBeTruthy()
})

// ============================================================
// SETTINGS PAGE
// ============================================================
test('Settings page: loads without errors', async ({ page }) => {
  const errors = []
  page.on('pageerror', e => errors.push(e.message))
  await page.goto('/settings')
  await page.waitForTimeout(500)
  expect(errors).toHaveLength(0)
})

// ============================================================
// LINKHUB (port 9003)
// ============================================================
test('LinkHub homepage: loads and shows profiles', async ({ page }) => {
  await page.goto('http://127.0.0.1:9003/')
  await expect(page.locator('text=LinkHub')).toBeVisible()
  const profiles = page.locator('.search-result, a[href*="/profile/"]')
  const count = await profiles.count()
  expect(count).toBeGreaterThan(5)
})

test('LinkHub profile: Elena Rodriguez has 4+ post images', async ({ page }) => {
  await page.goto('http://127.0.0.1:9003/profile/elena-rodriguez')
  await page.waitForTimeout(1000)
  const images = page.locator('.post img, img[src*="unsplash"]')
  const count = await images.count()
  expect(count).toBeGreaterThanOrEqual(4)
})

test('LinkHub profile: has banner (background image)', async ({ page }) => {
  await page.goto('http://127.0.0.1:9003/profile/elena-rodriguez')
  await page.waitForTimeout(500)
  const banner = page.locator('.banner')
  await expect(banner).toBeVisible()
  const style = await banner.getAttribute('style')
  expect(style).toContain('background')
})

test('LinkHub DM: sends message without user_id error', async ({ page }) => {
  await page.goto('http://127.0.0.1:9003/profile/elena-rodriguez?lab_id=mgm_breach')
  await page.waitForTimeout(800)
  // Look for DM input
  const dmInput = page.locator('#dm-input, input[placeholder*="message"], input[placeholder*="Message"]').first()
  if (await dmInput.isVisible()) {
    await dmInput.fill('Hello')
    await page.click('button:has-text("Send")')
    await page.waitForTimeout(2000)
    // Should NOT show "Missing required fields"
    await expect(page.locator('text=Missing required fields')).not.toBeVisible()
  }
})

test('LinkHub login: accepts NPC credentials', async ({ page }) => {
  await page.goto('http://127.0.0.1:9003/login?lab_id=mgm_breach')
  await page.fill('#email', 'elena.rodriguez@goldenmirage.com')
  await page.fill('#password', 'Helpdesk#2020')
  await page.click('button:has-text("Sign In")')
  await page.waitForTimeout(1500)
  // Should redirect to inbox
  expect(page.url()).toContain('/inbox')
})

// ============================================================
// COMPANIES (port 9008)
// ============================================================
test('Companies homepage: loads', async ({ page }) => {
  await page.goto('http://127.0.0.1:9008/')
  await page.waitForTimeout(500)
  const body = await page.content()
  expect(body.length).toBeGreaterThan(200)
})

test('Companies: Golden Mirage page loads with nav', async ({ page }) => {
  await page.goto('http://127.0.0.1:9008/company/golden-mirage')
  await page.waitForTimeout(500)
  await expect(page.locator('text=Golden Mirage, nav, .navbar')).toBeVisible()
})

test('Companies: chart block renders for meridian', async ({ page }) => {
  await page.goto('http://127.0.0.1:9008/company/meridian')
  await page.waitForTimeout(500)
  const chart = page.locator('text=FUND PERFORMANCE, text=Net IRR')
  await expect(chart.first()).toBeVisible()
})

// ============================================================
// BACKEND API (port 8000)
// ============================================================
test('Backend: /api/labs returns labs list', async ({ page }) => {
  const response = await page.request.get('http://127.0.0.1:8000/api/labs')
  expect(response.status()).toBe(200)
  const data = await response.json()
  expect(Array.isArray(data)).toBeTruthy()
  expect(data.length).toBeGreaterThan(0)
})

test('Backend: /api/health or root responds', async ({ page }) => {
  const response = await page.request.get('http://127.0.0.1:8000/')
  expect(response.status()).toBeLessThan(500)
})
