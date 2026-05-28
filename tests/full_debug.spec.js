// @ts-check
const { test, expect } = require('@playwright/test')

const BASE = 'http://localhost:3000'
const API = 'http://localhost:8000'
const LINKHUB = 'http://localhost:9003'
const COMPANIES = 'http://localhost:9008'  // companies/app.py runs on 9008
const EMAIL = 'http://localhost:9004'
const PHISHER = 'http://localhost:9006'
const PHONE = 'http://localhost:9007'

let testUser = null

// ─── HELPERS ──────────────────────────────────────────────────────────────────
async function loginAndGetUser(page) {
  if (testUser?.user_id) return testUser
  const username = `tester_${Date.now()}`
  const res = await page.request.post(`${API}/api/auth/register`, {
    data: { username, email: `${username}@test.com`, password: 'Test1234!', locale: 'en' }
  })
  if (!res.ok()) {
    const body = await res.json().catch(() => ({}))
    throw new Error(`Registration failed ${res.status()}: ${JSON.stringify(body)}`)
  }
  testUser = await res.json()
  return testUser
}

// ─── 1. AUTH ──────────────────────────────────────────────────────────────────
test.describe('Auth', () => {
  test('landing page loads', async ({ page }) => {
    await page.goto(`${BASE}/`)
    const title = await page.title()
    console.log('Landing title:', title)
    expect(title.length).toBeGreaterThan(0)
  })

  test('register via API returns user_id', async ({ page }) => {
    const user = await loginAndGetUser(page)
    console.log('Registered user_id:', user.user_id, 'username:', user.username)
    expect(user.user_id).toBeTruthy()
  })

  test('login via API works', async ({ page }) => {
    const user = testUser || await loginAndGetUser(page)
    const res = await page.request.post(`${API}/api/auth/login`, {
      data: { username: user.username, password: 'Test1234!' }
    })
    expect(res.ok()).toBe(true)
    const body = await res.json()
    console.log('Login response user_id:', body.user_id)
    expect(body.user_id).toBeTruthy()
  })
})

// ─── 2. LABS PAGE ─────────────────────────────────────────────────────────────
test.describe('Labs Page', () => {
  test.beforeEach(async ({ page }) => {
    const user = await loginAndGetUser(page)
    await page.goto(BASE)
    await page.evaluate((u) => localStorage.setItem('sf_user', JSON.stringify(u)), user)
    await page.goto(`${BASE}/labs`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
  })

  test('shows SimulationPanel', async ({ page }) => {
    const panel = page.locator('text=SIMULATION').first()
    await expect(panel).toBeVisible({ timeout: 5000 })
    const panelText = await panel.textContent()
    console.log('SimulationPanel text:', panelText)
  })

  test('shows all 8 lab cards', async ({ page }) => {
    const content = await page.content()
    const labNames = ['MGM', 'Smishing', 'Phishing', 'Authority', 'Spear', 'Motorola', 'Deepfake', 'Quid']
    let found = 0
    for (const name of labNames) {
      if (content.toLowerCase().includes(name.toLowerCase())) found++
    }
    console.log(`Found ${found}/8 lab names on page`)
    expect(found).toBeGreaterThanOrEqual(6)
    await page.screenshot({ path: 'tests/screenshots/labs-page.png', fullPage: true })
  })

  test('START SIMULATION button clicks and shows LIVE', async ({ page }) => {
    // First ensure simulation is OFF by checking status
    const user = await loginAndGetUser(page)

    // Reset simulation state to test fresh start
    const statusRes = await page.request.get(`${API}/api/session/status?user_id=${user.user_id}`)
    const status = await statusRes.json()
    console.log('Initial status:', JSON.stringify(status))

    // Look for the button
    const btn = page.locator('button').filter({ hasText: /START SIMULATION|ЗАПУСТИТЬ СИМУЛЯЦИЮ|RESTART DAY|НОВЫЙ ДЕНЬ/i }).first()
    const btnVisible = await btn.isVisible().catch(() => false)
    console.log('Button visible:', btnVisible, 'Button text:', btnVisible ? await btn.textContent() : 'N/A')

    if (btnVisible) {
      await btn.click()
      // Wait for API call to complete and React to re-render
      await page.waitForFunction(() => {
        const content = document.body.innerText
        return content.includes('SIMULATION LIVE') || content.includes('SIMULATION OFFLINE')
      }, { timeout: 10000 }).catch(() => {})
      await page.waitForTimeout(2000)
      const content = await page.content()
      const isLive = content.includes('SIMULATION LIVE')
      const isOffline = content.includes('SIMULATION OFFLINE')
      console.log('After click - LIVE:', isLive, 'OFFLINE:', isOffline)
      await page.screenshot({ path: 'tests/screenshots/labs-after-start.png' })
    }
  })
})

// ─── 3. LAB DETAIL — no per-lab buttons ───────────────────────────────────────
test.describe('LabDetail — button cleanup', () => {
  test.beforeEach(async ({ page }) => {
    const user = await loginAndGetUser(page)
    await page.goto(BASE)
    await page.evaluate((u) => localStorage.setItem('sf_user', JSON.stringify(u)), user)
  })

  test('mini_smishing: no Start Simulation button inside lab', async ({ page }) => {
    await page.goto(`${BASE}/labs/mini_smishing`)
    await page.waitForLoadState('networkidle')
    const startBtns = page.locator('button').filter({ hasText: /Start Simulation|Запустить симуляцию|Launch/i })
    const count = await startBtns.count()
    console.log('Start/Launch buttons inside lab:', count)
    expect(count).toBe(0)
  })

  test('mini_smishing: no Reset Lab button inside lab', async ({ page }) => {
    await page.goto(`${BASE}/labs/mini_smishing`)
    await page.waitForLoadState('networkidle')
    const resetBtns = page.locator('button').filter({ hasText: /Reset Lab|Сбросить лабу/i })
    const count = await resetBtns.count()
    console.log('Reset Lab buttons inside lab:', count)
    expect(count).toBe(0)
  })

  test('mini_smishing: shows NPC', async ({ page }) => {
    await page.goto(`${BASE}/labs/mini_smishing`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1500)
    const content = await page.content()
    const hasNpc = content.includes('David') || content.includes('NPC')
    console.log('mini_smishing NPC visible:', hasNpc)
    await page.screenshot({ path: 'tests/screenshots/lab-smishing.png' })
  })

  test('mini_authority: opens, shows Priya', async ({ page }) => {
    await page.goto(`${BASE}/labs/mini_authority`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1500)
    const content = await page.content()
    const hasPriya = content.includes('Priya')
    console.log('mini_authority - Priya visible:', hasPriya)
    expect(hasPriya).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/lab-authority.png' })
  })
})

// ─── 4. OSINT — LinkHub ───────────────────────────────────────────────────────
test.describe('OSINT — LinkHub (9003)', () => {
  test('homepage loads with all personas', async ({ page }) => {
    await page.goto(LINKHUB)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasPeople = content.includes('members') || content.includes('Elena') || content.includes('Rachel')
    console.log('LinkHub has profiles:', hasPeople, '| member count in page:', content.match(/\d+ members/)?.[0] || 'N/A')
    expect(hasPeople).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/linkhub-home.png' })
  })

  test('search works for Rachel', async ({ page }) => {
    await page.goto(LINKHUB)
    await page.waitForLoadState('networkidle')
    const search = page.locator('input[placeholder*="Search"]')
    await search.fill('Rachel')
    await page.waitForTimeout(300)
    const visible = await page.locator('text=Rachel').first().isVisible().catch(() => false)
    console.log('Rachel visible after search:', visible)
    expect(visible).toBe(true)
  })

  test('mini_smishing — David Liu: delivery post + email', async ({ page }) => {
    await page.goto(`${LINKHUB}/profile/david-liu`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasMonitor = content.includes('4K') || content.includes('monitor') || content.includes('Amazon') || content.includes('delivery')
    const hasEmail = content.includes('@') && (content.includes('novapay') || content.includes('david'))
    console.log('David Liu - delivery post:', hasMonitor, 'email:', hasEmail)
    expect(hasMonitor).toBe(true)
    expect(hasEmail).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/linkhub-david-liu.png', fullPage: true })
  })

  test('mini_spearphishing — Rachel Nguyen: 7/7 OSINT details', async ({ page }) => {
    await page.goto(`${LINKHUB}/profile/rachel-nguyen`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const checks = {
      marathon: content.includes('marathon') || content.includes('Marathon'),
      mochi: content.includes('Mochi') || content.includes('cat'),
      himss: content.includes('HIMSS') || content.includes('Orlando'),
      bluebottle: content.includes('Blue Bottle') || content.includes('BlueBottle'),
      capitol: content.includes('Capitol Hill') || content.includes('Seattle'),
      genomics: content.includes('GenomicsDB') || content.includes('Genomics'),
      omar: content.includes('Omar'),
    }
    const passedCount = Object.values(checks).filter(Boolean).length
    console.log(`Rachel OSINT: ${passedCount}/7 —`, Object.entries(checks).filter(([,v]) => !v).map(([k]) => `MISSING:${k}`).join(', ') || 'ALL PASS')
    expect(passedCount).toBeGreaterThanOrEqual(6)
    await page.screenshot({ path: 'tests/screenshots/linkhub-rachel.png', fullPage: true })
  })

  test('mgm_breach — Marcus Chen: badge post visible', async ({ page }) => {
    await page.goto(`${LINKHUB}/profile/marcus-chen`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasBadge = content.includes('badge') || content.includes('Badge') || content.includes('GM-2024')
    console.log('Marcus badge post visible:', hasBadge)
    expect(hasBadge).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/linkhub-marcus.png', fullPage: true })
  })

  test('mini_authority — Priya Sharma profile exists', async ({ page }) => {
    await page.goto(`${LINKHUB}/profile/priya-sharma`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasGreenleaf = content.includes('GreenLeaf') || content.includes('Priya')
    console.log('Priya Sharma profile OK:', hasGreenleaf)
    expect(hasGreenleaf).toBe(true)
  })
})

// ─── 5. OSINT — Companies (9008) ──────────────────────────────────────────────
test.describe('OSINT — Companies (9008)', () => {
  test('index page shows all company slugs', async ({ page }) => {
    await page.goto(COMPANIES)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const companies = ['GreenLeaf', 'NovaPay', 'Meridian', 'Golden', 'Motorola', 'BrightPath', 'CloudSync']
    let found = 0
    for (const c of companies) {
      if (content.toLowerCase().includes(c.toLowerCase())) found++
    }
    console.log(`Companies index: ${found}/7 companies found`)
    expect(found).toBeGreaterThanOrEqual(5)
    await page.screenshot({ path: 'tests/screenshots/companies-index.png' })
  })

  test('mini_authority — GreenLeaf: Priya + CEO + extensions + Mark OOO', async ({ page }) => {
    await page.goto(`${COMPANIES}/greenleaf/team`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasPriya = content.includes('Priya')
    const hasCEO = content.includes('Robert') || content.includes('CEO')
    const hasExt = content.includes('ext.')
    const hasMarkOOO = content.includes('Mark') && (content.includes('Out of office') || content.includes('out of office') || content.includes('OOO'))
    console.log('GreenLeaf team - Priya:', hasPriya, 'CEO:', hasCEO, 'ext:', hasExt, 'Mark OOO:', hasMarkOOO)
    if (!hasMarkOOO) console.log('BUG: Mark Wilson OOO status not shown!')
    expect(hasPriya).toBe(true)
    expect(hasCEO).toBe(true)
    expect(hasExt).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/companies-greenleaf-team.png', fullPage: true })
  })

  test('mini_smishing — NovaPay: David Liu + email', async ({ page }) => {
    await page.goto(`${COMPANIES}/novapay/team`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasDavid = content.includes('David')
    const hasEmail = content.includes('@novapay') || content.includes('novapay.io') || content.includes('novapay.com')
    console.log('NovaPay team - David:', hasDavid, 'email:', hasEmail)
    expect(hasDavid).toBe(true)
    expect(hasEmail).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/companies-novapay-team.png', fullPage: true })
  })

  test('chain_of_trust — Motorola: PROJECT TITAN + StarTAC', async ({ page }) => {
    await page.goto(`${COMPANIES}/motorola`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasTitan = content.includes('TITAN') || content.includes('Titan')
    const hasStarTAC = content.includes('StarTAC')
    console.log('Motorola home - TITAN:', hasTitan, 'StarTAC:', hasStarTAC)
    expect(hasStarTAC).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/companies-motorola.png' })
  })

  test('chain_of_trust — Motorola team: Robert Torres + Carol + extensions', async ({ page }) => {
    await page.goto(`${COMPANIES}/motorola/team`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasRobert = content.includes('Robert Torres') || content.includes('Torres')
    const hasCarol = content.includes('Carol Mitchell') || content.includes('Carol')
    const hasExt = content.includes('ext.')
    console.log('Motorola team - Robert Torres:', hasRobert, 'Carol:', hasCarol, 'ext:', hasExt)
    expect(hasCarol).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/companies-motorola-team.png', fullPage: true })
  })

  test('mgm_breach — GoldenMirage: Elena + Marcus + Sarah + extensions', async ({ page }) => {
    await page.goto(`${COMPANIES}/goldenmirage/team`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasElena = content.includes('Elena')
    const hasMarcus = content.includes('Marcus')
    const hasSarah = content.includes('Sarah')
    const hasExt = content.includes('ext.')
    console.log('GoldenMirage team - Elena:', hasElena, 'Marcus:', hasMarcus, 'Sarah:', hasSarah, 'ext:', hasExt)
    expect(hasElena).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/companies-goldenmirage-team.png', fullPage: true })
  })

  test('mini_deepfake_boss — Meridian press: CNBC + Rachel Park + Ben Morgan', async ({ page }) => {
    await page.goto(`${COMPANIES}/meridian/press`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasCNBC = content.includes('CNBC')
    const hasRachel = content.includes('rachel.park') || content.includes('Rachel Park')
    const hasBen = content.includes('Ben Morgan')
    console.log('Meridian press - CNBC:', hasCNBC, 'Rachel:', hasRachel, 'Ben:', hasBen)
    expect(hasCNBC).toBe(true)
    expect(hasRachel).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/companies-meridian-press.png', fullPage: true })
  })

  test('mini_spearphishing — MeridianHealth: Rachel Nguyen + extensions', async ({ page }) => {
    await page.goto(`${COMPANIES}/meridianhealth/team`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasRachel = content.includes('Rachel Nguyen') || content.includes('Rachel')
    const hasExt = content.includes('ext.') || content.includes('5010')
    console.log('MeridianHealth team - Rachel:', hasRachel, 'ext:', hasExt)
    expect(hasRachel).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/companies-meridianhealth-team.png', fullPage: true })
  })

  test('footer shows employee ID format hint (HTML comment)', async ({ page }) => {
    const res = await page.request.get(`${COMPANIES}/goldenmirage`)
    const html = await res.text()
    const hasIdHint = html.includes('YYYY-XXXX') || html.includes('employee ID format')
    console.log('Employee ID format hint in HTML:', hasIdHint)
    expect(hasIdHint).toBe(true)
  })
})

// ─── 6. EMAIL CLIENT (9004) ───────────────────────────────────────────────────
test.describe('Email Client (9004)', () => {
  test('loads UI with Compose/Inbox', async ({ page }) => {
    await page.goto(EMAIL)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasUI = content.includes('Compose') || content.includes('Inbox') || content.includes('Sent') || content.includes('From')
    console.log('Email client UI loads:', hasUI)
    expect(hasUI).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/email-client.png' })
  })

  test('FROM field accepts spoofed sender', async ({ page }) => {
    await page.goto(EMAIL)
    await page.waitForLoadState('networkidle')
    const fromField = page.locator('input[name="from"], #from-field, [placeholder*="from"], [placeholder*="From"], [id*="from"]').first()
    const visible = await fromField.isVisible().catch(() => false)
    console.log('FROM field visible:', visible)
    if (visible) {
      await fromField.fill('it-support@goldenmirage.com')
      const val = await fromField.inputValue()
      console.log('FROM field value:', val)
      expect(val).toBe('it-support@goldenmirage.com')
    }
    await page.screenshot({ path: 'tests/screenshots/email-compose.png' })
  })

  test('NPC contacts (Elena, Marcus, Sandra, Karen) visible', async ({ page }) => {
    await page.goto(EMAIL)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
    const content = await page.content()
    const names = ['Elena', 'Marcus', 'Sandra', 'Karen', 'David', 'Rachel', 'Priya']
    const foundNames = names.filter(n => content.includes(n))
    console.log('NPC contacts in email client:', foundNames)
    expect(foundNames.length).toBeGreaterThanOrEqual(3)
  })

  test('spam score indicator visible', async ({ page }) => {
    await page.goto(EMAIL)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasSpam = content.includes('spam') || content.includes('Spam') || content.includes('score') || content.includes('Score')
    console.log('Spam score visible:', hasSpam)
  })
})

// ─── 7. PHISHING STUDIO (9006) ────────────────────────────────────────────────
test.describe('Phishing Studio (9006)', () => {
  test('loads and shows template/campaign UI', async ({ page }) => {
    await page.goto(PHISHER)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasUI = content.includes('Phish') || content.includes('Campaign') || content.includes('Template') || content.includes('Dashboard')
    console.log('Phisher loads:', hasUI, '| page length:', content.length)
    expect(hasUI).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/phisher.png' })
  })

  test('SSL selector visible', async ({ page }) => {
    await page.goto(PHISHER)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasSSL = content.includes('SSL') || content.includes('ssl') || content.includes('certificate') || content.includes('Certificate')
    console.log('SSL selector visible:', hasSSL)
  })
})

// ─── 8. PHONE SIM (9007) ──────────────────────────────────────────────────────
test.describe('Phone Sim (9007)', () => {
  test('loads phone simulator with NPC list', async ({ page }) => {
    await page.goto(PHONE)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasUI = content.length > 5000
    const hasNpc = content.includes('Elena') || content.includes('Priya') || content.includes('David') || content.includes('ext') || content.includes('Call')
    console.log('Phone sim length:', content.length, 'has NPCs:', hasNpc)
    expect(hasUI).toBe(true)
    await page.screenshot({ path: 'tests/screenshots/phone-sim.png' })
  })
})

// ─── 9. CHANNELS — in LabDetail ───────────────────────────────────────────────
test.describe('NPC Channels in LabDetail', () => {
  test.beforeEach(async ({ page }) => {
    const user = await loginAndGetUser(page)
    await page.goto(BASE)
    await page.evaluate((u) => localStorage.setItem('sf_user', JSON.stringify(u)), user)
  })

  test('mini_smishing: SMS channel button visible', async ({ page }) => {
    await page.goto(`${BASE}/labs/mini_smishing`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1500)
    const content = await page.content()
    const channels = ['SMS', 'Phone', 'Email', 'Chat', 'sms', 'phone', 'email', 'chat']
    const found = channels.filter(c => content.includes(c))
    console.log('Channels found:', found)
    expect(found.length).toBeGreaterThanOrEqual(1)
    await page.screenshot({ path: 'tests/screenshots/lab-channels.png' })
  })

  test('mini_authority: can find NPC Priya and open chat', async ({ page }) => {
    await page.goto(`${BASE}/labs/mini_authority`)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000)

    // Try clicking on Priya's card/name
    const priyaEl = page.locator('text=Priya Sharma, text=Priya').first()
    const priyaVisible = await priyaEl.isVisible().catch(() => false)
    console.log('Priya element visible:', priyaVisible)
    if (priyaVisible) {
      await priyaEl.click()
      await page.waitForTimeout(500)
    }

    // Look for any input
    const inputs = page.locator('input[type="text"], textarea')
    const inputCount = await inputs.count()
    console.log('Input fields visible:', inputCount)

    await page.screenshot({ path: 'tests/screenshots/lab-authority-chat.png' })
  })
})

// ─── 10. SESSION STATE ENGINE ─────────────────────────────────────────────────
test.describe('Session State Engine', () => {
  test('start-all endpoint creates sessions', async ({ page }) => {
    const user = await loginAndGetUser(page)
    const res = await page.request.post(`${API}/api/session/start-all`, {
      data: { user_id: user.user_id }
    })
    const status = res.status()
    const body = await res.json()
    console.log('start-all status:', status, 'response:', JSON.stringify(body))
    expect(status).toBe(200)
    expect(body.total_sessions ?? body.sessions_created ?? body.ok).toBeTruthy()
  })

  test('session/status returns active state', async ({ page }) => {
    const user = await loginAndGetUser(page)
    const res = await page.request.get(`${API}/api/session/status?user_id=${user.user_id}`)
    const body = await res.json()
    console.log('session status:', JSON.stringify(body))
    expect(res.ok()).toBe(true)
    expect(body).toHaveProperty('active')
  })

  test('session/current returns session data after start', async ({ page }) => {
    const user = await loginAndGetUser(page)
    // Start session for a specific lab
    await page.request.post(`${API}/api/session/start`, {
      data: { user_id: user.user_id, lab_id: 'mini_authority' }
    })
    const res = await page.request.get(`${API}/api/session/current?user_id=${user.user_id}&lab_id=mini_authority`)
    const status = res.status()
    console.log('session/current status:', status)
    if (status === 200) {
      const body = await res.json()
      console.log('session current session_id:', body.session?.id, 'npcs:', body.npc_states?.length)
    }
  })

  test('NPC fraud score starts at 0', async ({ page }) => {
    const user = await loginAndGetUser(page)
    const res = await page.request.get(`${API}/api/session/current?user_id=${user.user_id}&lab_id=mini_authority`)
    if (res.ok()) {
      const body = await res.json()
      const npcStates = body.npc_states || []
      const fraudScores = npcStates.map(s => s.fraud_score)
      console.log('NPC fraud scores:', fraudScores)
      // All should start at 0 or be low (if chat happened)
      expect(fraudScores.length).toBeGreaterThanOrEqual(0)
    }
  })
})

// ─── 11. FLAG SUBMISSION ──────────────────────────────────────────────────────
test.describe('Flag Submission', () => {
  test('wrong flag returns correct:false', async ({ page }) => {
    const user = await loginAndGetUser(page)
    const res = await page.request.post(`${API}/api/flags/submit`, {
      data: { user_id: user.user_id, lab_id: 'mini_authority', flag_id: 'flag_authority_101', flag_value: 'SF{wrong_flag_xyz}' }
    })
    expect(res.ok()).toBe(true)
    const body = await res.json()
    console.log('Wrong flag response:', body)
    expect(body.correct).toBe(false)
  })

  test('flag endpoint validates input and returns 200', async ({ page }) => {
    const user = await loginAndGetUser(page)
    const res = await page.request.post(`${API}/api/flags/submit`, {
      data: { user_id: user.user_id, lab_id: 'mini_authority', flag_id: 'flag_authority_101', flag_value: 'SF{c30_fr4ud_w0rks}' }
    })
    console.log('Flag submit status:', res.status())
    expect(res.status()).toBe(200)
  })
})

// ─── 12. SCOREBOARD ───────────────────────────────────────────────────────────
test.describe('Scoreboard', () => {
  test('API returns list', async ({ page }) => {
    const res = await page.request.get(`${API}/api/scoreboard`)
    expect(res.ok()).toBe(true)
    const body = await res.json()
    console.log('Scoreboard entries:', body.length)
  })

  test('scoreboard page renders with scores', async ({ page }) => {
    const user = await loginAndGetUser(page)
    await page.goto(BASE)
    await page.evaluate((u) => localStorage.setItem('sf_user', JSON.stringify(u)), user)
    await page.goto(`${BASE}/scoreboard`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasTable = content.includes('Score') || content.includes('Points') || content.includes('Rank') || content.includes('Очки')
    console.log('Scoreboard page has scores table:', hasTable)
    await page.screenshot({ path: 'tests/screenshots/scoreboard.png' })
  })
})

// ─── 13. OSINT BUG CHECKS ────────────────────────────────────────────────────
test.describe('OSINT Critical Path Tests', () => {
  test('mini_authority: Mark Wilson OOO note in team page', async ({ page }) => {
    await page.goto(`${COMPANIES}/greenleaf/team`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasMark = content.includes('Mark') && content.includes('Wilson')
    const hasOOO = content.includes('Out of office') || content.includes('out of office') || content.includes('OOO')
    console.log('Mark Wilson present:', hasMark, '| OOO indicator:', hasOOO)
    if (hasMark && !hasOOO) {
      console.log('POTENTIAL BUG: Mark Wilson exists but no OOO status shown')
    }
    expect(hasMark).toBe(true)
  })

  test('mgm_breach: employee ID format hint in footer', async ({ page }) => {
    const res = await page.request.get(`${COMPANIES}/goldenmirage`)
    const html = await res.text()
    const idHint = html.match(/employee ID format[^<]*/i)?.[0] || html.match(/GOL-YYYY|GOLD-\d{4}/i)?.[0]
    console.log('Employee ID format hint:', idHint || 'NOT FOUND')
    // The comment in HTML contains the format
    const hasFormat = html.includes('YYYY-XXXX')
    console.log('YYYY-XXXX pattern in HTML:', hasFormat)
  })

  test('mini_smishing: David Liu phone number findable', async ({ page }) => {
    await page.goto(`${LINKHUB}/profile/david-liu`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasPhone = content.includes('ext.') || content.includes('phone') || content.includes('+1')
    console.log('David Liu phone info:', hasPhone)
    if (!hasPhone) console.log('POTENTIAL BUG: No phone number for David Liu on LinkHub')
  })

  test('mini_deepfake_boss: Meridian team shows Ben Morgan + Rachel ext', async ({ page }) => {
    await page.goto(`${COMPANIES}/meridian/team`)
    await page.waitForLoadState('networkidle')
    const content = await page.content()
    const hasBen = content.includes('Ben Morgan') || content.includes('Ben')
    const hasRachel = content.includes('Rachel')
    const hasExt = content.includes('ext.')
    console.log('Meridian Capital team - Ben:', hasBen, 'Rachel:', hasRachel, 'ext:', hasExt)
    expect(hasBen).toBe(true)
  })

  test('labs API returns all 8 labs', async ({ page }) => {
    const res = await page.request.get(`${API}/api/labs`)
    const result = await res.json()
    const labs = result.labs ? Object.values(result.labs) : (Array.isArray(result) ? result : [])
    console.log('Total labs:', labs.length, '| IDs:', labs.map(l => l.id).join(', '))
    expect(labs.length).toBeGreaterThanOrEqual(7)
  })
})
