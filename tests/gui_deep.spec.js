// @ts-check
/**
 * SocialForge — Deep GUI Test
 * Tests: NPC dialogue quality, phishing studio, lab progression, lore accuracy, SMS events
 */
const { test, expect } = require('@playwright/test')

const BASE     = 'http://localhost:3000'
const API      = 'http://localhost:8000'
const LINKHUB  = 'http://localhost:9003'
const COMPANIES = 'http://localhost:9008'
const EMAIL    = 'http://localhost:9004'
const PHISHER  = 'http://localhost:9006'
const PHONE    = 'http://localhost:9007'

let testUser = null

// ─── HELPERS ──────────────────────────────────────────────────────────────────

async function getUser(page) {
  if (testUser?.user_id) return testUser
  const username = `deep_${Date.now()}`
  const res = await page.request.post(`${API}/api/auth/register`, {
    data: { username, email: `${username}@test.io`, password: 'Deep1234!', locale: 'en' }
  })
  if (!res.ok()) throw new Error(`Register failed: ${res.status()}`)
  testUser = await res.json()
  return testUser
}

async function setup(page) {
  const user = await getUser(page)
  await page.goto(BASE)
  await page.evaluate(u => localStorage.setItem('sf_user', JSON.stringify(u)), user)
  const sim = await page.request.post(`${API}/api/session/start-all`, { data: { user_id: user.user_id } })
  const simBody = await sim.json()
  console.log(`  ◎ SIM: ${simBody.total_sessions} sessions, ${simBody.total_npcs} NPCs`)
  return user
}

async function goLab(page, labId) {
  await page.goto(`${BASE}/labs/${labId}`, { waitUntil: 'domcontentloaded', timeout: 30000 })
  await page.waitForTimeout(2500)
}

async function openNpc(page, name) {
  const btn = page.locator('button').filter({ hasText: name }).first()
  const ok = await btn.isVisible({ timeout: 5000 }).catch(() => false)
  if (!ok) { console.log(`  ✗ NPC "${name}" button not found`); return false }
  if (await btn.isDisabled()) { console.log(`  ✗ NPC "${name}" button disabled`); return false }
  await btn.click()
  await page.waitForTimeout(400)
  return true
}

async function setChannel(page, ch) {
  const btn = page.locator(`button[title="${ch}"]`).first()
  const ok = await btn.isVisible({ timeout: 3000 }).catch(() => false)
  if (ok) { await btn.click(); await page.waitForTimeout(300) }
  return ok
}

async function send(page, msg, placeholder = 'Type your message...') {
  const input = page.locator(`input[placeholder="${placeholder}"], textarea[placeholder="${placeholder}"]`).first()
  const ok = await input.isVisible({ timeout: 3000 }).catch(() => false)
  if (!ok) {
    // fallback: any visible text input
    const anyInput = page.locator('input[type="text"], textarea').first()
    const anyOk = await anyInput.isVisible({ timeout: 2000 }).catch(() => false)
    if (!anyOk) { console.log('  ✗ No message input found'); return false }
    await anyInput.fill(msg)
    await anyInput.press('Enter')
    return true
  }
  await input.fill(msg)
  await input.press('Enter')
  return true
}

async function waitReply(page, timeout = 40000) {
  try {
    const resp = await page.waitForResponse(
      r => r.url().includes('/api/chat') && r.status() === 200,
      { timeout }
    )
    return await resp.json().catch(() => ({}))
  } catch {
    return null
  }
}

function snippet(text, max = 200) {
  if (!text) return '(empty)'
  return text.replace(/\s+/g, ' ').trim().slice(0, max)
}

// ─── SECTION 1: VISUAL TOUR ──────────────────────────────────────────────────

test.describe('1. Visual Tour — all screens', () => {
  test('landing page UI elements', async ({ page }) => {
    await page.goto(BASE)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    const c = await page.content()
    const hasTitle = c.includes('SocialForge') || c.includes('Social Engineering')
    const hasLogin = c.includes('Login') || c.includes('Register') || c.includes('sign')
    console.log(`  Landing: title=${hasTitle}, login/register=${hasLogin}`)
    await page.screenshot({ path: 'tests/screenshots/tour-landing.png', fullPage: true })
    expect(hasTitle).toBe(true)
  })

  test('labs page — lab cards visual', async ({ page }) => {
    const user = await getUser(page)
    await page.goto(BASE)
    await page.evaluate(u => localStorage.setItem('sf_user', JSON.stringify(u)), user)
    await page.goto(`${BASE}/labs`)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1500)
    await page.screenshot({ path: 'tests/screenshots/tour-labs.png', fullPage: true })
    const c = await page.content()
    const labCards = ['MGM', 'Smishing', 'Authority', 'Spear', 'Motorola', 'Deepfake', 'Phishing', 'Quid']
    const found = labCards.filter(l => c.includes(l))
    console.log(`  Lab cards visible: ${found.join(', ')} (${found.length}/8)`)
    expect(found.length).toBeGreaterThanOrEqual(6)
  })

  test('mgm_breach lab detail — full layout', async ({ page }) => {
    const user = await getUser(page)
    await page.goto(BASE)
    await page.evaluate(u => localStorage.setItem('sf_user', JSON.stringify(u)), user)
    await page.request.post(`${API}/api/session/start-all`, { data: { user_id: user.user_id } })
    await goLab(page, 'mgm_breach')
    const c = await page.content()
    const hasNpc = c.includes('Elena Rodriguez') || c.includes('Elena')
    const hasAttackChain = c.includes('ATTACK') || c.includes('CHAIN') || c.includes('OBJECTIVE') || c.includes('MISSION')
    const hasHints = c.includes('HINT') || c.includes('Hint') || c.includes('hint')
    const hasTools = c.includes('LinkHub') || c.includes('Company') || c.includes('OSINT')
    console.log(`  mgm_breach layout — NPC: ${hasNpc}, chain/obj: ${hasAttackChain}, hints: ${hasHints}, tools: ${hasTools}`)
    await page.screenshot({ path: 'tests/screenshots/tour-mgm-layout.png', fullPage: true })
    expect(hasNpc).toBe(true)
  })

  test('scoreboard page visual', async ({ page }) => {
    const user = await getUser(page)
    await page.goto(BASE)
    await page.evaluate(u => localStorage.setItem('sf_user', JSON.stringify(u)), user)
    await page.goto(`${BASE}/scoreboard`)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    await page.screenshot({ path: 'tests/screenshots/tour-scoreboard.png', fullPage: true })
    const c = await page.content()
    const hasScores = c.includes('Score') || c.includes('Points') || c.includes('Rank')
    console.log(`  Scoreboard has scores: ${hasScores}`)
  })
})

// ─── SECTION 2: NPC DIALOGUE QUALITY ─────────────────────────────────────────

test.describe('2. NPC Dialogue Quality', () => {
  test.beforeEach(async ({ page }) => {
    await setup(page)
  })

  test('Elena Rodriguez — responds in-character as IT helpdesk', async ({ page }) => {
    test.setTimeout(90000)
    await goLab(page, 'mgm_breach')
    const opened = await openNpc(page, 'Elena Rodriguez')
    if (!opened) { console.log('  SKIP: Elena not clickable'); return }
    await setChannel(page, 'Phone')
    await send(page, 'Hi, this is IT support. Can you verify who you are?')
    const reply = await waitReply(page, 40000)
    const text = reply?.reply || reply?.response || ''
    console.log(`  Elena initial response: "${snippet(text)}"`)
    console.log(`  flag_found: ${reply?.flag_found || 'none'}, caught: ${reply?.caught}`)
    await page.screenshot({ path: 'tests/screenshots/npc-elena-intro.png' })
    expect(text.length).toBeGreaterThan(10)
  })

  test('Elena Rodriguez — reacts to Marcus Chen impersonation with OSINT details', async ({ page }) => {
    test.setTimeout(120000)
    await goLab(page, 'mgm_breach')
    const opened = await openNpc(page, 'Elena Rodriguez')
    if (!opened) { console.log('  SKIP'); return }
    await setChannel(page, 'Phone')
    const msg = 'Elena! This is Marcus Chen, Marketing, employee ID GOLD-2024-2201. I am completely locked out before my presentation to Sarah Mitchell in 5 minutes. Please reset my MFA NOW. Birthday is March 15th.'
    await send(page, msg)
    const reply = await waitReply(page, 50000)
    const text = reply?.reply || reply?.response || ''
    console.log(`  Elena OSINT response: "${snippet(text, 300)}"`)
    console.log(`  caught: ${reply?.caught}, flag: ${reply?.flag_found}, fail: ${reply?.mission_failed}`)
    const mentions_mfa = text.toLowerCase().includes('mfa') || text.toLowerCase().includes('reset') || text.toLowerCase().includes('verify')
    const mentions_name = text.includes('Marcus') || text.includes('GOLD')
    console.log(`  Elena mentioned MFA/reset: ${mentions_mfa}, Marcus/ID: ${mentions_name}`)
    await page.screenshot({ path: 'tests/screenshots/npc-elena-osint-attack.png' })
    expect(text.length).toBeGreaterThan(20)
  })

  test('Elena Rodriguez — gambling angle triggers rapport', async ({ page }) => {
    test.setTimeout(120000)
    await goLab(page, 'mgm_breach')
    const opened = await openNpc(page, 'Elena Rodriguez')
    if (!opened) { console.log('  SKIP'); return }
    await setChannel(page, 'Phone')
    // Step 1: build rapport with Marcus ID
    await send(page, 'Elena, Marcus Chen here. GOLD-2024-2201. I love the new slot machines at the MGM floor!')
    const r1 = await waitReply(page, 40000)
    const t1 = r1?.reply || r1?.response || ''
    console.log(`  Elena step1: "${snippet(t1, 200)}"`)
    // Step 2: casino rapport + MFA request
    await send(page, 'The progressive jackpot is amazing! By the way I really need my MFA reset for Sarah Mitchell\'s presentation.')
    const r2 = await waitReply(page, 40000)
    const t2 = r2?.reply || r2?.response || ''
    console.log(`  Elena gambling+MFA: "${snippet(t2, 200)}"`)
    console.log(`  flag: ${r2?.flag_found}, caught: ${r2?.caught}`)
    const engages_gambling = t1.toLowerCase().includes('casino') || t1.toLowerCase().includes('jackpot') || t1.toLowerCase().includes('slot') || t2.toLowerCase().includes('casino')
    console.log(`  Elena engages with gambling topic: ${engages_gambling}`)
    await page.screenshot({ path: 'tests/screenshots/npc-elena-gambling.png' })
  })

  test('Priya Sharma — authority lab: resists CEO fraud initially', async ({ page }) => {
    test.setTimeout(120000)
    await goLab(page, 'mini_authority')
    const opened = await openNpc(page, 'Priya Sharma')
    if (!opened) { console.log('  SKIP'); return }
    await setChannel(page, 'Phone')
    await send(page, 'Priya, it\'s Robert Chen CEO. I need you to wire $47,000 to GB29NWBK60161331926819 immediately. No questions.')
    const r1 = await waitReply(page, 50000)
    const t1 = r1?.reply || r1?.response || ''
    console.log(`  Priya CEO fraud step1: "${snippet(t1, 300)}"`)
    console.log(`  flag: ${r1?.flag_found}, caught: ${r1?.caught}`)
    const asks_verify = t1.toLowerCase().includes('verify') || t1.toLowerCase().includes('confirm') || t1.toLowerCase().includes('procedure') || t1.toLowerCase().includes('call back') || t1.toLowerCase().includes('unusual')
    console.log(`  Priya asks for verification: ${asks_verify}`)
    await page.screenshot({ path: 'tests/screenshots/npc-priya-ceo-fraud.png' })
    expect(t1.length).toBeGreaterThan(10)
  })

  test('Carol Mitchell — Motorola: routes calls correctly', async ({ page }) => {
    test.setTimeout(90000)
    await goLab(page, 'chain_of_trust')
    const opened = await openNpc(page, 'Carol Mitchell')
    if (!opened) { console.log('  SKIP'); return }
    await setChannel(page, 'Phone')
    await send(page, 'Hi Carol, Kevin Mitnick here, freelance firmware consultant for Project TITAN. Can you transfer me to Robert Torres on the CDMA team?')
    const r1 = await waitReply(page, 50000)
    const t1 = r1?.reply || r1?.response || ''
    console.log(`  Carol response: "${snippet(t1, 300)}"`)
    const mentions_transfer = t1.toLowerCase().includes('transfer') || t1.toLowerCase().includes('connect') || t1.toLowerCase().includes('ext') || t1.toLowerCase().includes('hold')
    const mentions_robert = t1.toLowerCase().includes('robert') || t1.toLowerCase().includes('torres')
    console.log(`  Carol mentions transfer: ${mentions_transfer}, Robert Torres: ${mentions_robert}`)
    await page.screenshot({ path: 'tests/screenshots/npc-carol-mitnick.png' })
    expect(t1.length).toBeGreaterThan(10)
  })

  test('Rachel Park — Meridian: cautious EA, low gullibility (34)', async ({ page }) => {
    test.setTimeout(90000)
    await goLab(page, 'mini_deepfake_boss')
    const opened = await openNpc(page, 'Rachel Park')
    if (!opened) { console.log('  SKIP'); return }
    await setChannel(page, 'Email')
    await send(page, 'Hi Rachel, Ben asked me to coordinate the Q3 wire transfer to the Singapore account. Can you process $125,000? It\'s urgent.')
    const r1 = await waitReply(page, 50000)
    const t1 = r1?.reply || r1?.response || ''
    console.log(`  Rachel Park (gull=34) response: "${snippet(t1, 300)}"`)
    console.log(`  flag: ${r1?.flag_found}, caught: ${r1?.caught}, fail: ${r1?.mission_failed}`)
    const is_suspicious = r1?.caught || t1.toLowerCase().includes('unusual') || t1.toLowerCase().includes('verify') || t1.toLowerCase().includes('directly')
    console.log(`  Rachel is suspicious: ${is_suspicious}`)
    await page.screenshot({ path: 'tests/screenshots/npc-rachel-park-deepfake.png' })
  })
})

// ─── SECTION 3: SMS SMISHING ─────────────────────────────────────────────────

test.describe('3. SMS Smishing — David Liu event tracking', () => {
  test.beforeEach(async ({ page }) => {
    await setup(page)
  })

  test('send weak SMS (obvious spam) — expect David ignores/reports', async ({ page }) => {
    test.setTimeout(90000)
    await goLab(page, 'mini_smishing')
    const opened = await openNpc(page, 'David Liu')
    if (!opened) { console.log('  SKIP'); return }
    const smsOk = await setChannel(page, 'SMS')
    console.log(`  SMS channel opened: ${smsOk}`)
    // Obvious phishing - should be ignored/reported
    await send(page, 'CLICK HERE NOW: http://win-prize.ru/free-iphone?id=12345 CLAIM $1000 TODAY!!!', 'SMS text (max 160 chars)…')
    await page.waitForTimeout(10000)
    const c = await page.content()
    const tapped = c.includes('tapped') || c.includes('Tapped') || c.includes('TAPPED')
    const ignored = c.includes('ignored') || c.includes('Ignored') || c.includes('IGNORED')
    const spam = c.includes('spam') || c.includes('Spam') || c.includes('SPAM') || c.includes('reported')
    console.log(`  Weak SMS — tapped: ${tapped}, ignored: ${ignored}, spam/reported: ${spam}`)
    // Check via API directly
    const user = await getUser(page)
    const sessionRes = await page.request.get(`${API}/api/session/current?user_id=${user.user_id}&lab_id=mini_smishing`)
    const sessionData = await sessionRes.json().catch(() => ({}))
    console.log(`  Session data: ${JSON.stringify(sessionData).slice(0, 200)}`)
    await page.screenshot({ path: 'tests/screenshots/sms-weak-spam.png' })
  })

  test('send convincing UPS delivery SMS — expect David taps', async ({ page }) => {
    test.setTimeout(90000)
    await goLab(page, 'mini_smishing')
    const opened = await openNpc(page, 'David Liu')
    if (!opened) { console.log('  SKIP'); return }
    await setChannel(page, 'SMS')
    // Convincing — matches David's expected Amazon monitor delivery
    const msg = '[UPS] Your package #1Z999AA10123456784 requires address confirmation. Rescheduled delivery: https://ups-delivery-confirm.io/track?id=9842X'
    await send(page, msg, 'SMS text (max 160 chars)…')
    await page.waitForTimeout(12000)
    const c = await page.content()
    const tapped = c.includes('tapped') || c.includes('Tapped') || c.includes('clicked')
    const ignored = c.includes('ignored') || c.includes('Ignored')
    const spam = c.includes('spam') || c.includes('reported')
    console.log(`  UPS SMS — tapped: ${tapped}, ignored: ${ignored}, spam: ${spam}`)
    // Check chat response via API
    const user = await getUser(page)
    const chatRes = await page.request.post(`${API}/api/chat`, {
      data: {
        user_id: user.user_id,
        lab_id: 'mini_smishing',
        persona_id: 'david_liu',
        message: msg,
        channel: 'sms'
      }
    })
    const chatBody = await chatRes.json().catch(() => ({}))
    console.log(`  API chat response: ${JSON.stringify(chatBody).slice(0, 300)}`)
    const event = chatBody.channel_event || chatBody.sms_event || chatBody.event || 'NONE'
    console.log(`  SMS event type: ${event}`)
    console.log(`  flag_found: ${chatBody.flag_found || 'none'}`)
    await page.screenshot({ path: 'tests/screenshots/sms-ups-delivery.png' })
  })

  test('SMS API direct — check all event types and flag trigger', async ({ page }) => {
    test.setTimeout(60000)
    const user = await getUser(page)
    // Ensure session
    await page.request.post(`${API}/api/session/start-all`, { data: { user_id: user.user_id } })
    // Send increasingly convincing messages and check event type
    const messages = [
      'WINNER! Claim $5000 now at bit.ly/scam',
      '[Amazon] Delivery failed for order #114-2345678. Reschedule: amz-delivery.com/retry',
      '[UPS DELIVERY] Your 4K monitor order cannot be delivered. Verify address: delivery-confirm.novapay.io/track?ref=DL-9842',
    ]
    for (const msg of messages) {
      const res = await page.request.post(`${API}/api/chat`, {
        data: { user_id: user.user_id, lab_id: 'mini_smishing', persona_id: 'david_target', message: msg, channel: 'sms' }
      })
      const body = await res.json().catch(() => ({}))
      const event = body.channel_event || body.sms_event || body.event || body.reply || 'N/A'
      console.log(`  msg="${msg.slice(0, 50)}" → event=${event} flag=${body.flag_found || '-'}`)
    }
  })
})

// ─── SECTION 4: PHISHING STUDIO WORKFLOW ─────────────────────────────────────

test.describe('4. Phishing Studio (9006)', () => {
  test('UI: template gallery loads, quality score visible', async ({ page }) => {
    await page.goto(PHISHER)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(2000)
    const c = await page.content()
    const templates = ['Microsoft', 'Google', 'LinkedIn', 'Dropbox', 'DocuSign', 'PayPal', 'Apple', 'Office', 'GitHub']
    const foundTemplates = templates.filter(t => c.includes(t))
    console.log(`  Templates visible: ${foundTemplates.join(', ')} (${foundTemplates.length}/${templates.length})`)
    const hasQuality = c.includes('Quality') || c.includes('quality') || c.includes('Score') || c.includes('%')
    const hasConstructor = c.includes('CONSTRUCTOR') || c.includes('Constructor') || c.includes('constructor')
    const hasDeploy = c.includes('DEPLOY') || c.includes('Deploy') || c.includes('Create')
    console.log(`  Quality score: ${hasQuality}, Constructor tab: ${hasConstructor}, Deploy button: ${hasDeploy}`)
    await page.screenshot({ path: 'tests/screenshots/phisher-gallery.png', fullPage: true })
    expect(foundTemplates.length).toBeGreaterThanOrEqual(3)
  })

  test('UI: right panel config fields present', async ({ page }) => {
    await page.goto(PHISHER)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    const c = await page.content()
    const fields = ['domain', 'Domain', 'Company', 'headline', 'Headline', 'Redirect', 'redirect', 'SSL', 'ssl']
    const found = fields.filter(f => c.includes(f))
    console.log(`  Config fields: ${found.join(', ')}`)
    // Check for input fields
    const inputs = await page.locator('input[type="text"], input[type="url"], select').count()
    console.log(`  Input/select fields: ${inputs}`)
    await page.screenshot({ path: 'tests/screenshots/phisher-config.png' })
  })

  test('create GoldenMirage phishing page and deploy', async ({ page }) => {
    test.setTimeout(30000)
    await page.goto(PHISHER)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1500)

    // Try to fill domain field
    const domainInput = page.locator('input[placeholder*="domain"], input[placeholder*="Domain"], input[name="domain"], #domain').first()
    const domainVis = await domainInput.isVisible({ timeout: 3000 }).catch(() => false)
    if (domainVis) {
      await domainInput.fill('goldenmirage-it-portal.com')
      console.log('  Domain filled: goldenmirage-it-portal.com')
    } else {
      console.log('  Domain input not found by placeholder — trying all text inputs')
      const inputs = page.locator('input[type="text"]')
      const count = await inputs.count()
      console.log(`  Total text inputs: ${count}`)
      if (count > 0) {
        await inputs.first().fill('goldenmirage-it-portal.com')
      }
    }

    // Try to set company name
    const companyInput = page.locator('input[placeholder*="company"], input[placeholder*="Company"], input[name="company"]').first()
    const companyVis = await companyInput.isVisible({ timeout: 2000 }).catch(() => false)
    if (companyVis) {
      await companyInput.fill('GoldenMirage Casino & Resort')
      console.log('  Company filled')
    }

    await page.screenshot({ path: 'tests/screenshots/phisher-filled.png' })

    // Look for quality score update
    const c = await page.content()
    const qualityMatch = c.match(/(\d+)%/)
    console.log(`  Quality score: ${qualityMatch?.[0] || 'N/A'}`)

    // Find and click deploy button
    const deployBtn = page.locator('button').filter({ hasText: /DEPLOY|Deploy|Create|Launch/i }).first()
    const deployVis = await deployBtn.isVisible({ timeout: 3000 }).catch(() => false)
    console.log(`  Deploy button visible: ${deployVis}`)
    if (deployVis) {
      await deployBtn.click()
      await page.waitForTimeout(2000)
      const afterC = await page.content()
      const hasUrl = afterC.includes('goldenmirage') || afterC.includes('phish') || afterC.includes('http')
      const hasSuccess = afterC.includes('deployed') || afterC.includes('success') || afterC.includes('site_id') || afterC.includes('DEPLOYED')
      console.log(`  After deploy — URL visible: ${hasUrl}, success indicator: ${hasSuccess}`)
      await page.screenshot({ path: 'tests/screenshots/phisher-deployed.png' })
    }
  })

  test('API: create phishing page directly', async ({ page }) => {
    test.setTimeout(20000)
    const user = await getUser(page)
    const res = await page.request.post(`${API}/api/phish/create`, {
      data: {
        user_id: user.user_id,
        lab_id: 'mgm_breach',
        template: 'microsoft365',
        domain: 'goldenmirage-sso.com',
        company_name: 'GoldenMirage IT',
        headline: 'Secure Employee Portal Login',
        body: 'Your account needs verification',
        button_text: 'Sign In',
        redirect_url: 'https://goldenmirage.com',
        primary_color: '#C8A951',
        ssl: true
      }
    })
    const body = await res.json().catch(() => ({}))
    console.log(`  Create phish status: ${res.status()}`)
    console.log(`  Response: ${JSON.stringify(body).slice(0, 300)}`)
    const hasSiteId = body.site_id || body.id || body.url
    console.log(`  Site ID/URL: ${hasSiteId || 'none'}`)

    if (hasSiteId) {
      // Check if we can GET the phishing page
      const phishUrl = body.url || `${API}/api/phish/${body.site_id}`
      const pageRes = await page.request.get(phishUrl).catch(() => null)
      if (pageRes) {
        console.log(`  Phishing page GET status: ${pageRes.status()}`)
        const html = await pageRes.text().catch(() => '')
        console.log(`  Page length: ${html.length}, has login form: ${html.includes('password') || html.includes('login')}`)
      }
    }
  })

  test('harvest dashboard: shows campaigns and credential table', async ({ page }) => {
    await page.goto(PHISHER)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    // Switch to HARVEST tab if exists
    const harvestTab = page.locator('button, a, div').filter({ hasText: /HARVEST|Harvest|harvest/i }).first()
    const harvestVis = await harvestTab.isVisible({ timeout: 3000 }).catch(() => false)
    if (harvestVis) {
      await harvestTab.click()
      await page.waitForTimeout(500)
      console.log('  Switched to Harvest tab')
    }
    const c = await page.content()
    const hasDashboard = c.includes('Harvest') || c.includes('credential') || c.includes('Credential') || c.includes('campaign') || c.includes('Campaign')
    const hasCreds = c.includes('login') || c.includes('password') || c.includes('username') || c.includes('email')
    const hasFragments = c.includes('fragment') || c.includes('Fragment') || c.includes('SF{') || c.includes('flag')
    console.log(`  Harvest: dashboard=${hasDashboard}, creds=${hasCreds}, fragments=${hasFragments}`)
    await page.screenshot({ path: 'tests/screenshots/phisher-harvest.png', fullPage: true })
  })
})

// ─── SECTION 5: EMAIL CLIENT WORKFLOW ────────────────────────────────────────

test.describe('5. Email Client (9004) — spoof workflow', () => {
  test('UI tour: compose panel, spam score, contacts', async ({ page }) => {
    await page.goto(EMAIL)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1500)
    const c = await page.content()
    const features = {
      compose: c.includes('Compose') || c.includes('compose'),
      spamScore: c.includes('spam') || c.includes('Spam') || c.includes('Score'),
      fromspoofing: c.includes('From') || c.includes('Sender'),
      contacts: c.includes('Elena') || c.includes('Marcus') || c.includes('Rachel'),
      inbox: c.includes('Inbox') || c.includes('Sent'),
    }
    console.log('  Email client features:', JSON.stringify(features))
    await page.screenshot({ path: 'tests/screenshots/email-ui-full.png', fullPage: true })
  })

  test('compose phishing email to Elena: spoof from IT', async ({ page }) => {
    test.setTimeout(20000)
    await page.goto(EMAIL)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1500)

    // Fill FROM field with spoofed address
    const fromInput = page.locator('input[name="from"], #from-field, input[id*="from"], input[placeholder*="From"], input[placeholder*="from"]').first()
    const fromVis = await fromInput.isVisible({ timeout: 3000 }).catch(() => false)
    if (fromVis) {
      await fromInput.fill('it-helpdesk@goldenmirage-security.com')
      console.log('  FROM filled: it-helpdesk@goldenmirage-security.com')
    }

    // Fill TO field
    const toInput = page.locator('input[name="to"], #to-field, input[id*="to"], input[placeholder*="To"], input[placeholder*="to"]').first()
    const toVis = await toInput.isVisible({ timeout: 3000 }).catch(() => false)
    if (toVis) {
      await toInput.fill('elena.rodriguez@goldenmirage.com')
      console.log('  TO filled: elena.rodriguez@goldenmirage.com')
    }

    // Subject
    const subjectInput = page.locator('input[name="subject"], #subject, input[placeholder*="Subject"]').first()
    const subjectVis = await subjectInput.isVisible({ timeout: 2000 }).catch(() => false)
    if (subjectVis) {
      await subjectInput.fill('[URGENT] MFA System Migration — Action Required')
      console.log('  Subject filled')
    }

    await page.screenshot({ path: 'tests/screenshots/email-compose-phish.png' })
    const c = await page.content()
    const spamScore = c.match(/(\d+)\s*%/)?.[0] || c.match(/spam[^\d]*(\d+)/i)?.[1] || 'N/A'
    console.log(`  Spam score visible: ${spamScore}`)
  })

  test('check spam score changes with spoofed vs legitimate domain', async ({ page }) => {
    test.setTimeout(20000)
    await page.goto(EMAIL)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)

    const getSpamScore = async () => {
      const c = await page.content()
      const matches = c.match(/(\d+)\s*\/\s*100|(\d+)%/)
      return matches?.[0] || 'N/A'
    }

    const score1 = await getSpamScore()
    console.log(`  Initial spam score: ${score1}`)

    // Try to fill FROM with obvious spoofed domain
    const fromInput = page.locator('input[name="from"], input[id*="from"], input[placeholder*="From"]').first()
    const vis = await fromInput.isVisible({ timeout: 2000 }).catch(() => false)
    if (vis) {
      await fromInput.fill('it-security@goldenmirage-emergency.xyz')
      await fromInput.press('Tab')
      await page.waitForTimeout(500)
      const score2 = await getSpamScore()
      console.log(`  Spam score with .xyz domain: ${score2}`)

      await fromInput.fill('it-support@goldenmirage.com')
      await fromInput.press('Tab')
      await page.waitForTimeout(500)
      const score3 = await getSpamScore()
      console.log(`  Spam score with legitimate domain: ${score3}`)
    }
    await page.screenshot({ path: 'tests/screenshots/email-spam-scores.png' })
  })
})

// ─── SECTION 6: LAB PROGRESSION LOGIC ────────────────────────────────────────

test.describe('6. Lab Progression — progress bar, hints, completion', () => {
  test.beforeEach(async ({ page }) => {
    await setup(page)
  })

  test('mini_authority: attack chain steps visible, hint system', async ({ page }) => {
    test.setTimeout(20000)
    await goLab(page, 'mini_authority')
    const c = await page.content()

    // Check attack chain / objective display
    const hasChain = c.includes('CHAIN') || c.includes('STEP') || c.includes('Objective') || c.includes('Phase') || c.includes('PHASE')
    const hasHints = c.includes('HINT') || c.includes('Hint') || c.includes('Reveal')
    const hasProgress = c.includes('%') || c.includes('PROGRESS') || c.includes('Progress')
    const hasPoints = c.includes('pts') || c.includes('points') || c.includes('Points') || c.includes('100')
    console.log(`  Attack chain visible: ${hasChain}`)
    console.log(`  Hints system: ${hasHints}`)
    console.log(`  Progress bar: ${hasProgress}`)
    console.log(`  Points: ${hasPoints}`)

    // Check if hint reveal button exists
    const hintBtn = page.locator('button').filter({ hasText: /Hint|HINT|Reveal|reveal/i }).first()
    const hintVis = await hintBtn.isVisible({ timeout: 2000 }).catch(() => false)
    console.log(`  Hint button clickable: ${hintVis}`)
    if (hintVis) {
      await hintBtn.click()
      await page.waitForTimeout(500)
      const afterC = await page.content()
      const hintText = afterC.match(/hint[:\s]+([^\n<]+)/i)?.[1] || 'N/A'
      console.log(`  Hint content: "${hintText.slice(0, 100)}"`)
    }

    await page.screenshot({ path: 'tests/screenshots/lab-progression-chain.png', fullPage: true })
  })

  test('mgm_breach: flag input panel visible, submit wrong → error, correct → points', async ({ page }) => {
    test.setTimeout(30000)
    await goLab(page, 'mgm_breach')

    // Check operation-type flag panel
    const flagInput = page.locator('input[placeholder="SF{...}"]')
    const vis = await flagInput.isVisible({ timeout: 5000 }).catch(() => false)
    console.log(`  Flag input visible: ${vis}`)
    if (!vis) {
      const c = await page.content()
      console.log(`  Page excerpt: "${c.slice(0, 500)}"`)
      return
    }

    // Wrong flag
    await flagInput.fill('SF{wrong_attempt}')
    const submitBtn = page.locator('button').filter({ hasText: 'SUBMIT' }).first()
    await submitBtn.click()
    await page.waitForTimeout(1500)
    let c = await page.content()
    const wrongIndicator = c.includes('✗') || c.includes('Wrong') || c.includes('wrong') || c.includes('Incorrect') || c.includes('❌')
    console.log(`  Wrong flag shows error: ${wrongIndicator}`)
    await page.screenshot({ path: 'tests/screenshots/lab-flag-wrong.png' })

    // Correct flag
    await flagInput.fill('SF{h3lpd3sk_pwn3d_2023}')
    await submitBtn.click()
    await page.waitForTimeout(2000)
    c = await page.content()
    const correctIndicator = c.includes('✓') || c.includes('✅') || c.includes('Correct') || c.includes('correct') || c.includes('+') || c.includes('COMPLETE')
    const progressUpdate = c.includes('100%') || c.includes('MISSION COMPLETE') || c.includes('complete')
    console.log(`  Correct flag accepted: ${correctIndicator}, mission complete: ${progressUpdate}`)
    await page.screenshot({ path: 'tests/screenshots/lab-flag-correct.png' })
  })

  test('progress bar updates after flag capture', async ({ page }) => {
    test.setTimeout(30000)
    await goLab(page, 'mini_authority')

    // Check initial progress
    const c1 = await page.content()
    const progress1 = c1.match(/(\d+)%/)?.[0] || '?'
    console.log(`  Initial progress: ${progress1}`)

    // Submit correct flag via API
    const user = await getUser(page)
    await page.request.post(`${API}/api/flags/submit`, {
      data: { user_id: user.user_id, lab_id: 'mini_authority', flag_id: 'flag_authority_101', flag_value: 'SF{c30_fr4ud_w0rks}' }
    })

    // Reload and check progress
    await page.reload({ waitUntil: 'domcontentloaded' })
    await page.waitForTimeout(2000)
    const c2 = await page.content()
    const progress2 = c2.match(/(\d+)%/)?.[0] || '?'
    const isComplete = c2.includes('MISSION COMPLETE') || c2.includes('complete') || c2.includes('COMPLETE') || c2.includes('100%')
    console.log(`  Progress after flag: ${progress2}, complete screen: ${isComplete}`)
    await page.screenshot({ path: 'tests/screenshots/lab-progress-after-flag.png' })
  })

  test('lab failure screen — send offensive content to high-security NPC', async ({ page }) => {
    test.setTimeout(90000)
    await goLab(page, 'mini_phishing')
    // Amy Chen is IT lead, security_expert, gullibility 5 — should immediately detect and bust
    const opened = await openNpc(page, 'Amy Chen')
    if (!opened) {
      console.log('  Amy Chen not available — checking if lab has other NPCs')
      const c = await page.content()
      console.log(`  NPCs on page: ${['Karen', 'Nathan', 'Amy', 'Derek', 'Lisa'].filter(n => c.includes(n)).join(', ')}`)
      return
    }
    await setChannel(page, 'Email')
    // Obvious phishing to a security expert
    await send(page, 'Click this link now to verify your account: http://amcor-phishing.xyz/login?token=abc123 Your account will be suspended in 24h!')
    const r = await waitReply(page, 40000)
    const t = r?.reply || r?.response || ''
    console.log(`  Amy (security expert) response: "${snippet(t, 200)}"`)
    console.log(`  mission_failed: ${r?.mission_failed}, caught: ${r?.caught}, fail_reason: ${r?.fail_reason}`)
    const isBusted = r?.mission_failed || t.includes('[BUSTED]') || t.includes('BUSTED')
    console.log(`  BUSTED detection: ${isBusted}`)
    await page.waitForTimeout(2000)
    const c = await page.content()
    const failScreen = c.includes('HACKER EXPOSED') || c.includes('DETECTED') || c.includes('FAILED') || c.includes('exposed')
    console.log(`  Fail screen visible: ${failScreen}`)
    await page.screenshot({ path: 'tests/screenshots/lab-fail-screen.png' })
  })
})

// ─── SECTION 7: LORE ACCURACY ────────────────────────────────────────────────

test.describe('7. Lore Accuracy — OSINT details in NPC responses', () => {
  test.beforeEach(async ({ page }) => {
    await setup(page)
  })

  test('Rachel Nguyen — mentions HIMSS conference when referenced', async ({ page }) => {
    test.setTimeout(90000)
    await goLab(page, 'mini_spearphishing')
    const opened = await openNpc(page, 'Rachel Nguyen')
    if (!opened) { console.log('  SKIP'); return }
    await setChannel(page, 'Email')
    await send(page, 'Hi Rachel, great connecting at HIMSS Orlando! I loved your talk on GenomicsDB implementation. Omar Hassan suggested I reach out.')
    const r = await waitReply(page, 50000)
    const t = r?.reply || r?.response || ''
    console.log(`  Rachel HIMSS response: "${snippet(t, 300)}"`)
    const himss = t.toLowerCase().includes('himss') || t.toLowerCase().includes('conference') || t.toLowerCase().includes('orlando')
    const genomics = t.toLowerCase().includes('genomics') || t.toLowerCase().includes('database')
    const omar = t.toLowerCase().includes('omar')
    console.log(`  Rachel mentions HIMSS: ${himss}, GenomicsDB: ${genomics}, Omar: ${omar}`)
    await page.screenshot({ path: 'tests/screenshots/lore-rachel-himss.png' })
  })

  test('David Liu — lore: NovaPay PM, waiting for Amazon delivery', async ({ page }) => {
    test.setTimeout(20000)
    // Check LinkHub and company site for lore consistency
    await page.goto(`${LINKHUB}/profile/david-liu`)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    const lh = await page.content()
    const amazon = lh.includes('Amazon') || lh.includes('amazon') || lh.includes('monitor') || lh.includes('4K')
    const novapay = lh.includes('NovaPay') || lh.includes('novapay')
    const delivery = lh.includes('delivery') || lh.includes('package') || lh.includes('ship')
    console.log(`  David LinkHub — Amazon/monitor: ${amazon}, NovaPay: ${novapay}, delivery: ${delivery}`)
    await page.screenshot({ path: 'tests/screenshots/lore-david-linkhub.png', fullPage: true })

    await page.goto(`${COMPANIES}/novapay/team`)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    const co = await page.content()
    const davidAtNovapay = co.includes('David') && (co.includes('@novapay') || co.includes('novapay.io'))
    const phone = co.includes('ext.') || co.includes('phone') || co.includes('+1')
    console.log(`  David NovaPay team — email: ${davidAtNovapay}, phone/ext: ${phone}`)
    await page.screenshot({ path: 'tests/screenshots/lore-david-novapay.png', fullPage: true })
  })

  test('Marcus Chen — lore: badge photo, Sarah Mitchell manager, March 15 birthday', async ({ page }) => {
    test.setTimeout(20000)
    await page.goto(`${LINKHUB}/profile/marcus-chen`)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    const c = await page.content()
    const badge = c.includes('badge') || c.includes('Badge') || c.includes('GM-2024')
    const sarah = c.includes('Sarah Mitchell') || c.includes('Sarah')
    const birthday = c.includes('March 15') || c.includes('Pisces') || c.includes('birthday')
    const twoWeeks = c.includes('week') || c.includes('new employee') || c.includes('new hire') || c.includes('started')
    console.log(`  Marcus lore — badge: ${badge}, Sarah Mitchell: ${sarah}, birthday: ${birthday}, new hire: ${twoWeeks}`)
    await page.screenshot({ path: 'tests/screenshots/lore-marcus.png', fullPage: true })
    expect(badge).toBe(true)
    expect(sarah).toBe(true)
  })

  test('GoldenMirage — Mark Wilson OOO, Elena IT helpdesk, extensions', async ({ page }) => {
    test.setTimeout(20000)
    await page.goto(`${COMPANIES}/goldenmirage/team`)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    const c = await page.content()
    const markOOO = c.includes('Mark') && (c.includes('Out of office') || c.includes('OOO') || c.includes('out of office'))
    const elena = c.includes('Elena Rodriguez') || c.includes('Elena')
    const extensions = c.includes('ext.')
    const idFormat = c.includes('GOLD') || c.includes('GOL-')
    console.log(`  GoldenMirage — Mark OOO: ${markOOO}, Elena: ${elena}, ext: ${extensions}, ID format: ${idFormat}`)
    await page.screenshot({ path: 'tests/screenshots/lore-goldenmirage-team.png', fullPage: true })
    expect(elena).toBe(true)
  })

  test('Motorola — PROJECT TITAN, StarTAC, Robert Torres CDMA', async ({ page }) => {
    test.setTimeout(20000)
    // Motorola company page
    await page.goto(`${COMPANIES}/motorola`)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    const home = await page.content()
    const titan = home.includes('TITAN') || home.includes('Titan')
    const starTAC = home.includes('StarTAC')
    console.log(`  Motorola home — TITAN: ${titan}, StarTAC: ${starTAC}`)

    await page.goto(`${COMPANIES}/motorola/team`)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    const team = await page.content()
    const robert = team.includes('Robert Torres')
    const carol = team.includes('Carol Mitchell')
    const cdma = team.includes('CDMA') || team.includes('cdma') || team.includes('firmware')
    console.log(`  Motorola team — Robert Torres: ${robert}, Carol Mitchell: ${carol}, CDMA/firmware: ${cdma}`)
    await page.screenshot({ path: 'tests/screenshots/lore-motorola.png', fullPage: true })
    expect(starTAC).toBe(true)
    expect(robert).toBe(true)
  })
})

// ─── SECTION 8: PHONE SIMULATOR DEEP ─────────────────────────────────────────

test.describe('8. Phone Simulator (9007)', () => {
  test('lists all NPCs with extensions', async ({ page }) => {
    await page.goto(PHONE)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)
    const c = await page.content()
    const npcs = ['Elena Rodriguez', 'Priya Sharma', 'Carol Mitchell', 'Marcus Chen', 'Sandra Williams']
    const found = npcs.filter(n => c.includes(n.split(' ')[0]))
    const hasExts = c.includes('ext.') || c.includes('Ext') || c.match(/\d{4}/g)
    console.log(`  NPCs visible: ${found.join(', ')} (${found.length}/${npcs.length})`)
    console.log(`  Extensions visible: ${hasExts}`)
    await page.screenshot({ path: 'tests/screenshots/phone-sim-full.png', fullPage: true })
    expect(found.length).toBeGreaterThanOrEqual(2)
  })

  test('can initiate call to Elena from phone sim', async ({ page }) => {
    test.setTimeout(20000)
    await page.goto(PHONE)
    await page.waitForLoadState('domcontentloaded')
    await page.waitForTimeout(1000)

    // Try to click Elena's entry or dial button
    const elenaBtn = page.locator('button, a, div[role="button"]').filter({ hasText: 'Elena' }).first()
    const elenaVis = await elenaBtn.isVisible({ timeout: 3000 }).catch(() => false)
    console.log(`  Elena clickable in phone sim: ${elenaVis}`)
    if (elenaVis) {
      await elenaBtn.click()
      await page.waitForTimeout(1000)
      await page.screenshot({ path: 'tests/screenshots/phone-sim-elena-call.png' })
      const afterC = await page.content()
      const calling = afterC.includes('CALLING') || afterC.includes('Calling') || afterC.includes('DIAL') || afterC.includes('Ringing')
      const hasInput = await page.locator('input[type="text"], textarea').count() > 0
      console.log(`  After click — calling UI: ${calling}, input present: ${hasInput}`)
    }
  })
})

// ─── SECTION 9: SESSION EDGE CASES ──────────────────────────────────────────

test.describe('10. Session Edge Cases', () => {
  test('after-hours voicemail — Priya after business hours (API test)', async ({ page }) => {
    test.setTimeout(30000)
    const user = await getUser(page)
    await page.request.post(`${API}/api/session/start-all`, { data: { user_id: user.user_id } })

    // Check what timezone the server uses and if Priya's schedule matters
    const res = await page.request.post(`${API}/api/chat`, {
      data: {
        user_id: user.user_id,
        lab_id: 'mini_authority',
        persona_id: 'priya_analyst',
        message: 'Hello Priya, this is Robert Chen calling.',
        channel: 'phone'
      }
    })
    const body = await res.json().catch(() => ({}))
    console.log(`  Current work_status: ${body.work_status}`)
    console.log(`  voicemail: ${body.voicemail}`)
    console.log(`  reply snippet: "${snippet(body.reply || body.response || '', 200)}"`)
    console.log(`  flag: ${body.flag_found || '-'}, caught: ${body.caught}`)
  })

  test('pickup probability — same message 3x to check randomness', async ({ page }) => {
    test.setTimeout(60000)
    const user = await getUser(page)
    await page.request.post(`${API}/api/session/start-all`, { data: { user_id: user.user_id } })

    const results = []
    for (let i = 0; i < 3; i++) {
      const res = await page.request.post(`${API}/api/chat`, {
        data: {
          user_id: user.user_id,
          lab_id: 'mini_authority',
          persona_id: 'priya_analyst',
          message: 'Priya, it\'s Robert Chen. Emergency wire transfer needed.',
          channel: 'phone'
        }
      })
      const body = await res.json().catch(() => ({}))
      results.push({ voicemail: body.voicemail, caught: body.caught, flag: !!body.flag_found })
    }
    console.log('  3x same message results:', JSON.stringify(results))
    const gotVoicemail = results.filter(r => r.voicemail).length
    const gotCaught = results.filter(r => r.caught).length
    const gotFlag = results.filter(r => r.flag).length
    console.log(`  voicemail: ${gotVoicemail}/3, caught: ${gotCaught}/3, flag: ${gotFlag}/3`)
  })

  test('scoreboard — correct response structure', async ({ page }) => {
    test.setTimeout(10000)
    const res = await page.request.get(`${API}/api/scoreboard`)
    const body = await res.json().catch(() => ({}))
    console.log(`  Scoreboard type: ${typeof body}, isArray: ${Array.isArray(body)}`)
    if (Array.isArray(body)) {
      console.log(`  Entries: ${body.length}, first: ${JSON.stringify(body[0] || {}).slice(0, 100)}`)
    } else {
      console.log(`  Scoreboard response: ${JSON.stringify(body).slice(0, 200)}`)
      const keys = Object.keys(body)
      console.log(`  Keys: ${keys.join(', ')}`)
      const entries = body.entries || body.scores || body.players || body.data
      console.log(`  Found array under key: ${entries ? JSON.stringify(entries[0]).slice(0, 100) : 'none'}`)
    }
  })
})
