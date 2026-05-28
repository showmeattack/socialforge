import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'
import { useApp } from '../store'

const C = {
  bg:           '#04080d',
  surface:      '#060a0f',
  card:         '#080e18',
  accent:       '#00ff88',
  accentDim:    'rgba(0,255,136,0.06)',
  accentBorder: 'rgba(0,255,136,0.18)',
  text:         '#c8e8d4',
  textDim:      'rgba(200,232,212,0.38)',
  textMid:      'rgba(200,232,212,0.62)',
  border:       'rgba(0,255,136,0.08)',
  amber:        '#f59e0b',
  amberDim:     'rgba(245,158,11,0.07)',
  amberBorder:  'rgba(245,158,11,0.28)',
  red:          '#ef4444',
  blue:         '#38bdf8',
  blueDim:      'rgba(56,189,248,0.06)',
  blueBorder:   'rgba(56,189,248,0.18)',
  teal:         '#2dd4bf',
  tealDim:      'rgba(45,212,191,0.06)',
  tealBorder:   'rgba(45,212,191,0.18)',
  purple:       '#a78bfa',
  purpleDim:    'rgba(167,139,250,0.06)',
  purpleBorder: 'rgba(167,139,250,0.18)',
  pink:         '#f472b6',
  success:      '#10b981',
}

const TOTAL_STEPS = 6

function getStepMeta(locale) {
  const ru = locale === 'ru'
  return [
    { id: '01', label: ru ? 'БРИФИНГ'        : 'MISSION BRIEF',  color: C.accent, dim: C.accentDim, border: C.accentBorder },
    { id: '02', label: ru ? 'УГРОЗЫ'         : 'THREAT INTEL',   color: C.blue,   dim: C.blueDim,   border: C.blueBorder   },
    { id: '03', label: ru ? 'ИНСТРУМЕНТЫ'    : 'ATTACK TOOLKIT', color: C.teal,   dim: C.tealDim,   border: C.tealBorder   },
    { id: '04', label: ru ? 'ПРАВИЛА'        : 'FIELD DOCTRINE', color: C.purple, dim: C.purpleDim, border: C.purpleBorder },
    { id: '05', label: ru ? 'ДИСКЛЕЙМЕР'     : 'LEGAL NOTICE',   color: C.amber,  dim: C.amberDim,  border: C.amberBorder  },
    { id: '06', label: ru ? 'НАСТРОЙКА AI'   : 'AI SYNC',        color: C.accent, dim: C.accentDim, border: C.accentBorder },
  ]
}

function StepDots({ current, onGo, stepMeta }) {
  return (
    <div style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
      {Array.from({ length: TOTAL_STEPS }, (_, i) => {
        const active = i === current
        const done = i < current
        const { color } = stepMeta[i]
        return (
          <button
            key={i}
            onClick={() => onGo(i)}
            title={stepMeta[i].label}
            style={{
              width: active ? 22 : 7,
              height: 7,
              borderRadius: 4,
              border: 'none',
              background: active ? color : done ? `${color}40` : 'rgba(255,255,255,0.06)',
              cursor: 'pointer',
              padding: 0,
              transition: 'all 0.22s ease',
              boxShadow: active ? `0 0 10px ${color}70` : 'none',
            }}
          />
        )
      })}
    </div>
  )
}

function NavButtons({ step, onPrev, onNext, onDone, stepMeta, locale }) {
  const { color, dim, border } = stepMeta[step]
  const isLast = step === TOTAL_STEPS - 1
  const ru = locale === 'ru'
  const base = {
    fontFamily: 'JetBrains Mono, monospace',
    fontSize: 10,
    fontWeight: 700,
    letterSpacing: 1.5,
    padding: '10px 22px',
    borderRadius: 5,
    cursor: 'pointer',
    transition: 'all 0.15s',
  }
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <button
        onClick={onPrev}
        disabled={step === 0}
        style={{
          ...base,
          background: 'transparent',
          border: step === 0 ? '1px solid transparent' : '1px solid rgba(255,255,255,0.08)',
          color: step === 0 ? 'transparent' : C.textDim,
          cursor: step === 0 ? 'default' : 'pointer',
        }}
      >{ru ? '← НАЗАД' : '← PREV'}</button>

      <span style={{ fontSize: 9, color: C.textDim, letterSpacing: 2, fontFamily: 'JetBrains Mono, monospace' }}>
        {step + 1} / {TOTAL_STEPS}
      </span>

      {!isLast ? (
        <button
          onClick={onNext}
          style={{ ...base, background: dim, border: `1px solid ${border}`, color }}
          onMouseEnter={e => { e.currentTarget.style.background = `${color}14` }}
          onMouseLeave={e => { e.currentTarget.style.background = dim }}
        >{ru ? 'ВПЕРЁД →' : 'NEXT →'}</button>
      ) : (
        <button
          onClick={onDone}
          style={{ ...base, background: color, border: 'none', color: '#000', fontWeight: 900, fontSize: 11, boxShadow: `0 0 24px ${color}50` }}
          onMouseEnter={e => { e.currentTarget.style.boxShadow = `0 0 36px ${color}70` }}
          onMouseLeave={e => { e.currentTarget.style.boxShadow = `0 0 24px ${color}50` }}
        >{ru ? 'НАЧАТЬ ВЗЛОМ →' : 'START HACKING →'}</button>
      )}
    </div>
  )
}

function Step1({ locale }) {
  const ru = locale === 'ru'
  const bootLines = ru
    ? ['Подключение к AI-сети целей', 'Загрузка модулей атаки', 'Генерация NPC-персон', 'Инициализация сети наблюдения']
    : ['Connecting to AI target network', 'Loading attack modules', 'Spawning NPC personas', 'Initializing surveillance grid']
  return (
    <div style={{ textAlign: 'center' }}>
      <style>{`
        @keyframes sf-glitch {
          0%,88%,100% { color:#00ff88; text-shadow:0 0 28px rgba(0,255,136,0.5); transform:translate(0,0) skewX(0); }
          7%  { color:#ef4444; text-shadow:-3px 0 #00ff88,3px 0 #ef4444; transform:translate(-2px,1px) skewX(-2deg); }
          10% { color:#00ff88; text-shadow:0 0 28px rgba(0,255,136,0.5); transform:translate(0,0) skewX(0); }
          29% { color:#ef4444; transform:translate(2px,-1px) skewX(1deg); text-shadow:-2px 0 #00ff88; }
          31% { color:#00ff88; transform:translate(0,0) skewX(0); }
        }
        @keyframes sf-blink { 0%,49%{opacity:1} 50%,100%{opacity:0} }
      `}</style>

      <div style={{
        fontSize: 'clamp(24px,4vw,40px)',
        fontWeight: 900,
        letterSpacing: 8,
        fontFamily: 'JetBrains Mono, monospace',
        animation: 'sf-glitch 5s infinite',
        marginBottom: 6,
      }}>SOCIALFORGE</div>

      <div style={{
        fontSize: 9,
        fontWeight: 700,
        letterSpacing: 4,
        color: C.textDim,
        fontFamily: 'JetBrains Mono, monospace',
        marginBottom: 24,
        textTransform: 'uppercase',
      }}>{ru ? 'Тренажёр по социальной инженерии Red Team' : 'Red Team Social Engineering Trainer'}</div>

      <div style={{
        background: C.card,
        border: '1px solid rgba(0,255,136,0.08)',
        borderRadius: 6,
        padding: '12px 16px',
        marginBottom: 16,
        textAlign: 'left',
        fontFamily: 'JetBrains Mono, monospace',
      }}>
        {bootLines.map((text, i, arr) => (
          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: i < arr.length - 1 ? 5 : 0 }}>
            <span style={{ fontSize: 10, color: C.textMid }}>{'>'} {text}</span>
            <span style={{ fontSize: 10, color: C.accent, fontWeight: 700, marginLeft: 16 }}>[ OK ]</span>
          </div>
        ))}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 8, paddingTop: 8, borderTop: '1px solid rgba(0,255,136,0.06)' }}>
          <span style={{ fontSize: 10, color: C.accent, fontWeight: 700 }}>$</span>
          <span style={{ fontSize: 10, color: C.textMid }}>{ru ? 'готов к началу миссии' : 'ready to begin mission'}</span>
          <span style={{ animation: 'sf-blink 1s infinite', fontSize: 12, color: C.accent, lineHeight: 1 }}>█</span>
        </div>
      </div>

      <div style={{
        background: C.accentDim,
        border: `1px solid ${C.accentBorder}`,
        borderRadius: 6,
        padding: '14px 18px',
        textAlign: 'left',
        marginBottom: 16,
      }}>
        <div style={{ fontSize: 9, color: C.accent, letterSpacing: 3, marginBottom: 8, fontWeight: 800, fontFamily: 'JetBrains Mono, monospace' }}>
          {ru ? 'БРИФИНГ МИССИИ' : 'MISSION BRIEFING'}
        </div>
        {ru ? (
          <>
            <p style={{ fontSize: 12, color: C.text, lineHeight: 1.75, margin: '0 0 6px', fontFamily: 'JetBrains Mono, monospace' }}>
              Ты — <span style={{ color: C.accent, fontWeight: 700 }}>оператор Red Team</span>. Твои цели — AI-персоны с реальной психологией: они доверяют авторитетам, реагируют на срочность и совершают человеческие ошибки.
            </p>
            <p style={{ fontSize: 12, color: C.textMid, lineHeight: 1.75, margin: 0, fontFamily: 'JetBrains Mono, monospace' }}>
              Цепочка атаки:{' '}
              <span style={{ color: C.blue }}>OSINT</span> →{' '}
              <span style={{ color: C.teal }}>Легенда</span> →{' '}
              <span style={{ color: C.pink }}>Атака</span> →{' '}
              <span style={{ color: C.amber }}>Флаг</span>
            </p>
          </>
        ) : (
          <>
            <p style={{ fontSize: 12, color: C.text, lineHeight: 1.75, margin: '0 0 6px', fontFamily: 'JetBrains Mono, monospace' }}>
              You are a <span style={{ color: C.accent, fontWeight: 700 }}>Red Team operator</span>. Your targets are AI personas with real psychology — they trust authority, fear urgency, and make human mistakes.
            </p>
            <p style={{ fontSize: 12, color: C.textMid, lineHeight: 1.75, margin: 0, fontFamily: 'JetBrains Mono, monospace' }}>
              Attack chain:{' '}
              <span style={{ color: C.blue }}>OSINT</span> →{' '}
              <span style={{ color: C.teal }}>Pretext</span> →{' '}
              <span style={{ color: C.pink }}>Attack</span> →{' '}
              <span style={{ color: C.amber }}>Extract flag</span>
            </p>
          </>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 8 }}>
        {[
          { v: '7+',   l: ru ? 'ЛАБЫ'    : 'LABS'        },
          { v: '15+',  l: ru ? 'AI НПС'  : 'AI NPCs'     },
          { v: '5',    l: ru ? 'ВЕКТОРЫ' : 'VECTORS'     },
          { v: 'SF{}', l: ru ? 'ФОРМАТ'  : 'FLAG FORMAT' },
        ].map(s => (
          <div key={s.l} style={{
            background: C.card,
            border: '1px solid rgba(255,255,255,0.05)',
            borderRadius: 6,
            padding: '10px 6px',
            textAlign: 'center',
          }}>
            <div style={{ fontSize: 16, fontWeight: 900, color: C.accent, fontFamily: 'JetBrains Mono, monospace', lineHeight: 1 }}>{s.v}</div>
            <div style={{ fontSize: 8, color: C.textDim, letterSpacing: 1, marginTop: 4, fontFamily: 'JetBrains Mono, monospace' }}>{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function Step2({ locale }) {
  const ru = locale === 'ru'
  const vectors = ru ? [
    {
      icon: '📞', name: 'ВИШИНГ', color: '#10b981',
      desc: 'Телефонный обман. Ты звонишь целям, притворяясь IT-поддержкой, отделом безопасности или руководством. Подмена caller ID.',
      breach: 'Вектор атаки: звонок в helpdesk, представился сотрудником — сброс пароля за 4 минуты',
    },
    {
      icon: '📧', name: 'ФИШИНГ', color: C.blue,
      desc: 'Письма с поддельными отправителями. Целевой spear-phishing против массовых рассылок, собирающих фрагменты флагов.',
      breach: 'Вектор атаки: целевой spear-phishing HR через LinkedIn с вредоносной ссылкой',
    },
    {
      icon: '📱', name: 'СМИШИНГ', color: C.amber,
      desc: 'SMS-атаки на срочность. Фейковые 2FA-коды, блокировка аккаунта, доставка посылок — вызывают мгновенную реакцию.',
      breach: 'Вектор атаки: SMS-усталость — непрерывные MFA-запросы до одобрения подрядчиком',
    },
    {
      icon: '🎭', name: 'ПРЕТЕКСТИНГ', color: C.purple,
      desc: 'Создание легенды до атаки. OSINT → легенда → доверие через несколько взаимодействий → удар.',
      breach: 'Вектор атаки: фейк-журналист выстраивает доверие — сливает конфиденциальные данные совета',
    },
  ] : [
    {
      icon: '📞', name: 'VISHING', color: '#10b981',
      desc: 'Phone-based deception. You call targets posing as IT support, bank fraud teams, or executives. Spoof caller ID to appear legitimate.',
      breach: 'Classic tactic: caller posed as IT staff, reset VPN credentials in under 5 minutes',
    },
    {
      icon: '📧', name: 'PHISHING', color: C.blue,
      desc: 'Crafted emails with spoofed senders. Targeted spear-phishing vs mass campaigns that collect credential shards.',
      breach: 'Classic tactic: spear-phishing HR staff via LinkedIn with targeted lure messages',
    },
    {
      icon: '📱', name: 'SMISHING', color: C.amber,
      desc: 'SMS-based urgency attacks. Fake 2FA codes, account locked alerts, package delivery scams trigger immediate reaction.',
      breach: 'Classic tactic: MFA fatigue — continuous push requests until contractor approves access',
    },
    {
      icon: '🎭', name: 'PRETEXTING', color: C.purple,
      desc: 'Building a false identity before the attack. Research target → construct backstory → manufacture trust over multiple interactions.',
      breach: 'Classic tactic: fake journalist builds rapport over weeks, extracts confidential board data',
    },
  ]
  return (
    <div>
      <div style={{ fontSize: 9, color: C.blue, letterSpacing: 3, marginBottom: 6, fontWeight: 800, fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'РАЗВЕДКА УГРОЗ' : 'THREAT INTELLIGENCE'}
      </div>
      <h2 style={{ fontSize: 16, fontWeight: 800, color: C.text, margin: '0 0 6px', fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'Что такое социальная инженерия?' : 'What is Social Engineering?'}
      </h2>
      <p style={{ fontSize: 11, color: C.textMid, lineHeight: 1.7, margin: '0 0 14px', fontFamily: 'JetBrains Mono, monospace' }}>
        {ru
          ? <span>Социальная инженерия эксплуатирует <span style={{ color: C.blue }}>психологию людей</span>, а не уязвимости ПО. Слабое звено любой организации — это люди: доверие, страх, авторитет, любопытство.</span>
          : <span>Social engineering exploits <span style={{ color: C.blue }}>human psychology</span>, not software bugs. The weakest link in any org is always the people — you exploit trust, authority bias, fear, and curiosity.</span>
        }
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
        {vectors.map(v => (
          <div key={v.name} style={{
            background: `${v.color}06`,
            border: `1px solid ${v.color}20`,
            borderLeft: `3px solid ${v.color}`,
            borderRadius: 6,
            padding: '10px 14px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ fontSize: 14 }}>{v.icon}</span>
              <span style={{ fontSize: 11, fontWeight: 800, color: v.color, letterSpacing: 1, fontFamily: 'JetBrains Mono, monospace' }}>{v.name}</span>
            </div>
            <p style={{ fontSize: 11, color: C.text, lineHeight: 1.6, margin: '0 0 4px', fontFamily: 'JetBrains Mono, monospace' }}>{v.desc}</p>
            <p style={{ fontSize: 9, color: C.textDim, margin: 0, fontFamily: 'JetBrains Mono, monospace' }}>⚡ {v.breach}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function Step3({ locale }) {
  const ru = locale === 'ru'
  const phases = ru ? [
    {
      num: '01', label: 'ФАЗА 1 — РАЗВЕДКА', color: C.blue,
      subtitle: 'Собери данные до первого контакта. Это твой боеприпас.',
      tools: [
        {
          name: 'Соцсеть (LinkHub)', port: 9003, color: C.blue,
          how: 'Открой профиль цели. Запомни: должность, компанию, имя руководителя, посты, формат email. Чем больше знаешь — тем убедительнее легенда.',
        },
        {
          name: 'Сайты компаний', port: 9001, color: '#6366f1',
          how: 'Изучи публичный сайт организации. Найди: оргсхему, директорию сотрудников, IT-контакты, портал поддержки. Картографируй цель до атаки.',
        },
      ],
    },
    {
      num: '02', label: 'ФАЗА 2 — АТАКА', color: C.teal,
      subtitle: 'Ударь с легендой. Используй данные из фазы 1 чтобы звучать убедительно.',
      tools: [
        {
          name: 'Телефонный терминал', port: 9007, color: C.teal,
          how: 'Звони НПС напрямую. Подмени caller ID под IT/HR/руководство. Цели с высокой gullibility реагируют на срочность + авторитет.',
        },
        {
          name: 'Email клиент (SF Mail)', port: 9004, color: '#38bdf8',
          how: 'Отправляй письма от любого отправителя. Целевая отправка → полный флаг. Массовая кампания → фрагменты флага от нескольких целей.',
        },
      ],
    },
    {
      num: '03', label: 'ФАЗА 3 — СБОР', color: C.pink,
      subtitle: 'Собери учётные данные и соедини флаги из успешных атак.',
      tools: [
        {
          name: 'Phisher Dashboard', port: 9006, color: C.pink,
          how: 'Видишь захваченные данные в реальном времени. Перехваченные учётки используй для целевых атак или выставляй на продажу — в зависимости от лабы.',
        },
        {
          name: 'Мессенджер (NPC Inbox)', port: null, color: '#a78bfa',
          how: 'Войди в аккаунт НПС с перехваченными кредами. Читай внутреннюю переписку — там инструкции, коды доступа, подсказки к флагам.',
        },
      ],
    },
  ] : [
    {
      num: '01', label: 'PHASE 1 — INTELLIGENCE', color: C.blue,
      subtitle: 'Gather intel before making contact. This is your ammo.',
      tools: [
        {
          name: 'Social Media  (LinkHub)', port: 9003, color: C.blue,
          how: 'Open target\'s profile. Note: role, employer, manager name, recent posts, email format. The more you know, the more believable your pretext.',
        },
        {
          name: 'Company Sites (Golden Mirage)', port: 9001, color: '#6366f1',
          how: 'Browse the target org\'s "public" site. Find: org chart, employee directory, IT contacts, support portal. Map the org before attacking.',
        },
      ],
    },
    {
      num: '02', label: 'PHASE 2 — ATTACK', color: C.teal,
      subtitle: 'Strike with your pretext. Reference intel from Phase 1 to sound legit.',
      tools: [
        {
          name: 'Phone Terminal', port: 9007, color: C.teal,
          how: 'Call NPCs directly. Spoof your caller ID to match IT/HR/management. Authority-obedient targets (high gullibility) respond to urgency + credentials.',
        },
        {
          name: 'Email Client  (SF Mail)', port: 9004, color: '#38bdf8',
          how: 'Send spoofed emails from any identity. Targeted send → full flag if NPC falls for it. Mass campaign → collects flag fragments across multiple targets.',
        },
      ],
    },
    {
      num: '03', label: 'PHASE 3 — HARVEST', color: C.pink,
      subtitle: 'Collect credentials and assemble flags from successful attacks.',
      tools: [
        {
          name: 'Phisher Dashboard', port: 9006, color: C.pink,
          how: 'See captured credentials in real time as NPCs click phishing links. Use harvested creds for targeted attacks or sell them — depends on the lab objective.',
        },
        {
          name: 'Messenger (NPC Inbox)', port: null, color: '#a78bfa',
          how: 'Log into NPC accounts with harvested credentials. Read internal emails containing access codes, flag hints, and organizational intel.',
        },
      ],
    },
  ]

  return (
    <div>
      <div style={{ fontSize: 9, color: C.teal, letterSpacing: 3, marginBottom: 6, fontWeight: 800, fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'СНАРЯЖЕНИЕ ОПЕРАТОРА' : 'OPERATOR LOADOUT'}
      </div>
      <h2 style={{ fontSize: 16, fontWeight: 800, color: C.text, margin: '0 0 4px', fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'Инструменты атаки — как использовать' : 'Attack Toolkit — How to Use'}
      </h2>
      <p style={{ fontSize: 11, color: C.textMid, lineHeight: 1.65, margin: '0 0 14px', fontFamily: 'JetBrains Mono, monospace' }}>
        {ru
          ? 'Каждый инструмент работает на отдельном порту. Открывай в отдельных вкладках. Соблюдай последовательность фаз — пропуск фазы = провал.'
          : 'Each tool runs on a local port. Open them in separate tabs. Follow the 3-phase sequence — skipping phases will get you busted.'
        }
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {phases.map((ph, pi) => (
          <div key={ph.num}>
            <div style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: 8,
              marginBottom: 7,
              paddingBottom: 6,
              borderBottom: `1px solid ${ph.color}18`,
            }}>
              <span style={{
                fontSize: 8, fontWeight: 900, color: ph.color,
                background: `${ph.color}15`, border: `1px solid ${ph.color}30`,
                borderRadius: 3, padding: '2px 6px', letterSpacing: 1,
                fontFamily: 'JetBrains Mono, monospace', flexShrink: 0,
              }}>{ph.num}</span>
              <span style={{ fontSize: 10, fontWeight: 800, color: ph.color, letterSpacing: 1, fontFamily: 'JetBrains Mono, monospace' }}>{ph.label}</span>
              <span style={{ fontSize: 9, color: C.textDim, fontFamily: 'JetBrains Mono, monospace' }}>— {ph.subtitle}</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 5, paddingLeft: 10 }}>
              {ph.tools.map(tool => (
                <div key={tool.name} style={{
                  background: `${tool.color}05`,
                  border: `1px solid ${tool.color}15`,
                  borderLeft: `2px solid ${tool.color}`,
                  borderRadius: 5,
                  padding: '9px 12px',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: tool.color, fontFamily: 'JetBrains Mono, monospace' }}>{tool.name}</span>
                    {tool.port && <span style={{
                      fontSize: 9, color: C.textDim,
                      background: 'rgba(255,255,255,0.03)',
                      border: '1px solid rgba(255,255,255,0.07)',
                      padding: '1px 5px', borderRadius: 3,
                      fontFamily: 'JetBrains Mono, monospace',
                    }}>:{tool.port}</span>}
                  </div>
                  <p style={{ fontSize: 10, color: C.textMid, lineHeight: 1.65, margin: 0, fontFamily: 'JetBrains Mono, monospace' }}>
                    <span style={{ color: `${tool.color}70` }}>→ </span>{tool.how}
                  </p>
                </div>
              ))}
            </div>

            {pi < phases.length - 1 && (
              <div style={{
                textAlign: 'center',
                padding: '5px 0 2px',
                fontSize: 9,
                color: C.textDim,
                fontFamily: 'JetBrains Mono, monospace',
                letterSpacing: 2,
              }}>{ru ? '↓ используй собранные данные для убедительной легенды ↓' : '↓ use gathered intel to build a convincing story ↓'}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function Step4({ locale }) {
  const ru = locale === 'ru'
  const rules = ru ? [
    { label: 'ФЛАГИ',         color: C.accent,  text: 'Формат: SF{snake_case}. Отправляй через кнопку Submit Flag в лабе. Регистрозависимо. Один флаг на каждую фазу цепочки атаки.' },
    { label: 'ЦЕПОЧКА',       color: C.purple,  text: 'Лабы имеют последовательные шаги: OSINT → Легенда → Эксплуатация. Каждый НПС в цепочке разблокируется после завершения предыдущего.' },
    { label: 'СТАТЫ НПС',     color: C.blue,    text: 'gullibility (0–100): восприимчивость к социальному давлению. tech_savvy (0–100): способность обнаружить фейк. Проверяй оба перед выбором вектора.' },
    { label: 'ПОДОЗРЕНИЕ',    color: C.amber,   text: 'Каждое сообщение повышает или снижает подозрение НПС. UI показывает уровень. Слишком много странных вопросов — блокировка.' },
    { label: 'ПРОВАЛ',        color: C.red,     text: 'Подозрение достигло 100 → НПС прерывает контакт. Используй кнопку Reset чтобы начать с этой целью заново. Очки только за эту цель сбрасываются.' },
    { label: 'ОЧКИ',          color: C.success, text: 'Очки = ценность флага × бонус времени × множитель попыток. Меньше попыток + быстрее = выше результат. Идеальная операция = ноль подозрений.' },
  ] : [
    { label: 'FLAGS',        color: C.accent,  text: 'Format: SF{snake_case}. Submit via the Submit Flag button in the lab. Case-sensitive. One flag per phase of the attack chain.' },
    { label: 'ATTACK CHAIN', color: C.purple,  text: 'Labs have sequential steps: OSINT → Pretext → Exploitation. Each NPC in the chain unlocks after you complete the previous one.' },
    { label: 'NPC STATS',    color: C.blue,    text: 'gullibility (0–100): susceptibility to social pressure. tech_savvy (0–100): ability to detect fake emails/calls. Check both before picking your attack vector.' },
    { label: 'SUSPICION',    color: C.amber,   text: 'Every message raises or lowers NPC suspicion. Chat UI shows the level. Ask too many weird questions, trigger refusal. Watch the bar.' },
    { label: 'BUSTED',       color: C.red,     text: 'Suspicion hits 100 → NPC cuts contact and you\'re blocked. Use the Reset button to restart that target. Score resets for that NPC only.' },
    { label: 'SCORING',      color: C.success, text: 'Points = flag value × time bonus × attempt multiplier. Fewer attempts + faster completion = higher score. Perfect op = no suspicion raised.' },
  ]
  return (
    <div>
      <div style={{ fontSize: 9, color: C.purple, letterSpacing: 3, marginBottom: 6, fontWeight: 800, fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'ПРАВИЛА РАБОТЫ' : 'FIELD DOCTRINE'}
      </div>
      <h2 style={{ fontSize: 16, fontWeight: 800, color: C.text, margin: '0 0 14px', fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'Правила игры' : 'Game Rules'}
      </h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
        {rules.map(r => (
          <div key={r.label} style={{
            display: 'flex',
            gap: 10,
            alignItems: 'flex-start',
            padding: '8px 10px',
            background: `${r.color}05`,
            border: `1px solid ${r.color}14`,
            borderLeft: `2px solid ${r.color}55`,
            borderRadius: 5,
          }}>
            <span style={{
              fontSize: 8, fontWeight: 900, color: r.color,
              background: `${r.color}14`, border: `1px solid ${r.color}28`,
              padding: '3px 6px', borderRadius: 3, letterSpacing: 1,
              flexShrink: 0, fontFamily: 'JetBrains Mono, monospace',
              marginTop: 1, minWidth: 64, textAlign: 'center',
            }}>{r.label}</span>
            <p style={{ fontSize: 11, color: C.text, lineHeight: 1.65, margin: 0, fontFamily: 'JetBrains Mono, monospace' }}>{r.text}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function Step5({ locale }) {
  const ru = locale === 'ru'
  const items = ru ? [
    { icon: '🔒', text: 'SocialForge — это контролируемая обучающая среда. Все сценарии вымышлены. Реальные организации, люди и системы не являются целями.' },
    { icon: '🛡️', text: 'Показанные техники отражают методы реальных атакующих. Цель — защита: научиться распознавать и противостоять атакам социальной инженерии.' },
    { icon: '⚖️', text: 'Несанкционированная социальная инженерия против реальных людей незаконна в большинстве юрисдикций. Платформа — только для авторизованного обучения.' },
    { icon: '✅', text: 'Продолжая, ты подтверждаешь, что будешь использовать SocialForge только для легального авторизованного обучения кибербезопасности.' },
  ] : [
    { icon: '🔒', text: 'SocialForge is a controlled training environment. All scenarios are fictional. No real organizations, individuals, or systems are targeted.' },
    { icon: '🛡️', text: 'Techniques shown here mirror real-world attacker methods. The goal is defensive: learn to recognize and resist social engineering attacks.' },
    { icon: '⚖️', text: 'Unauthorized social engineering against real people is illegal in most jurisdictions. This platform is for authorized training and research only.' },
    { icon: '✅', text: 'By continuing you confirm you will use SocialForge only for legal, authorized cybersecurity training.' },
  ]
  return (
    <div>
      <div style={{ fontSize: 9, color: C.amber, letterSpacing: 3, marginBottom: 14, fontWeight: 800, fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'ДИСКЛЕЙМЕР' : 'LEGAL NOTICE'}
      </div>
      <div style={{
        background: C.amberDim,
        border: `1px solid ${C.amberBorder}`,
        borderRadius: 8,
        overflow: 'hidden',
      }}>
        <div style={{
          background: 'rgba(245,158,11,0.1)',
          padding: '10px 18px',
          borderBottom: `1px solid ${C.amberBorder}`,
          display: 'flex',
          alignItems: 'center',
          gap: 10,
        }}>
          <span style={{ fontSize: 14 }}>⚠️</span>
          <span style={{ fontSize: 10, fontWeight: 900, color: C.amber, letterSpacing: 2, fontFamily: 'JetBrains Mono, monospace' }}>
            {ru ? 'ТОЛЬКО ДЛЯ ОБУЧЕНИЯ' : 'EDUCATIONAL PURPOSES ONLY'}
          </span>
        </div>
        <div style={{ padding: '14px 18px', display: 'flex', flexDirection: 'column', gap: 11 }}>
          {items.map((item, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
              <span style={{ fontSize: 13, lineHeight: 1.7, flexShrink: 0 }}>{item.icon}</span>
              <p style={{ fontSize: 11, color: C.text, lineHeight: 1.7, margin: 0, fontFamily: 'JetBrains Mono, monospace' }}>{item.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function Step6({ locale }) {
  const ru = locale === 'ru'
  const [key, setKey] = useState('')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSaveTest = async () => {
    if (!key.trim()) return
    setLoading(true)
    setStatus(null)
    try {
      await api.updateSettings({ openrouter_api_key: key.trim() })
      const settings = await api.getSettings()
      setStatus(settings.openrouter_api_key_masked ? 'ok' : 'err')
    } catch {
      setStatus('err')
    } finally {
      setLoading(false)
    }
  }

  const steps = ru ? [
    { n: '1', text: 'Перейди на openrouter.ai → Зарегистрируйся (бесплатно)' },
    { n: '2', text: 'Dashboard → Keys → Create key' },
    { n: '3', text: 'Скопируй ключ (начинается с sk-or-v1-...) → вставь ниже' },
  ] : [
    { n: '1', text: 'Go to openrouter.ai → Sign up (free)' },
    { n: '2', text: 'Dashboard → Keys → Create key' },
    { n: '3', text: 'Copy key (starts with sk-or-v1-...) → paste below' },
  ]

  return (
    <div>
      <div style={{ fontSize: 9, color: C.accent, letterSpacing: 3, marginBottom: 6, fontWeight: 800, fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'НАСТРОЙКА AI' : 'AI CONFIGURATION'}
      </div>
      <h2 style={{ fontSize: 16, fontWeight: 800, color: C.text, margin: '0 0 6px', fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'Подключить AI-движок' : 'Connect AI Brain'}
      </h2>
      <p style={{ fontSize: 11, color: C.textMid, lineHeight: 1.7, margin: '0 0 18px', fontFamily: 'JetBrains Mono, monospace' }}>
        {ru
          ? <span>НПС-цели работают на <span style={{ color: C.accent }}>OpenRouter AI</span>. Без валидного ключа цели возвращают статические ошибки и флаги получить невозможно.</span>
          : <span>NPC targets are powered by <span style={{ color: C.accent }}>OpenRouter AI</span>. Without a valid key, targets return static error responses and no flags can be extracted.</span>
        }
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 16 }}>
        {steps.map(s => (
          <div key={s.n} style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <span style={{
              width: 18, height: 18,
              background: C.accentDim, border: `1px solid ${C.accentBorder}`,
              borderRadius: '50%', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 9, fontWeight: 900, color: C.accent,
              fontFamily: 'JetBrains Mono, monospace',
            }}>{s.n}</span>
            <span style={{ fontSize: 11, color: C.textMid, fontFamily: 'JetBrains Mono, monospace' }}>{s.text}</span>
          </div>
        ))}
      </div>

      <div style={{
        background: C.accentDim,
        border: `1px solid ${status === 'ok' ? C.accent : status === 'err' ? C.red : C.accentBorder}`,
        borderRadius: 8,
        padding: '14px 16px',
        marginBottom: 10,
        transition: 'border-color 0.2s',
      }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            type="password"
            value={key}
            onChange={e => setKey(e.target.value)}
            placeholder="sk-or-v1-..."
            onKeyDown={e => { if (e.key === 'Enter') handleSaveTest() }}
            style={{
              flex: 1,
              background: 'rgba(0,0,0,0.4)',
              border: '1px solid rgba(0,255,136,0.12)',
              borderRadius: 5,
              padding: '10px 12px',
              fontSize: 12,
              color: C.text,
              fontFamily: 'JetBrains Mono, monospace',
              outline: 'none',
            }}
          />
          <button
            onClick={handleSaveTest}
            disabled={loading || !key.trim()}
            style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 10, fontWeight: 700, letterSpacing: 1,
              padding: '10px 16px', borderRadius: 5,
              border: `1px solid ${C.accentBorder}`,
              background: loading ? 'transparent' : C.accentDim,
              color: loading ? C.textDim : C.accent,
              cursor: loading || !key.trim() ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap',
            }}
          >{loading ? '...' : ru ? 'СОХРАНИТЬ' : 'SAVE & TEST'}</button>
        </div>
        {status === 'ok' && (
          <div style={{ fontSize: 10, color: C.success, marginTop: 8, fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}>
            {ru ? '✓ Подключено — AI-движок онлайн. Готов к взлому.' : '✓ Connected — AI brain online. Ready to hack.'}
          </div>
        )}
        {status === 'err' && (
          <div style={{ fontSize: 10, color: C.red, marginTop: 8, fontFamily: 'JetBrains Mono, monospace', fontWeight: 700 }}>
            {ru ? '✗ Неверный ключ или ошибка соединения. Проверь openrouter.ai.' : '✗ Invalid key or connection error. Check openrouter.ai dashboard.'}
          </div>
        )}
      </div>
      <p style={{ fontSize: 10, color: C.textDim, margin: 0, fontFamily: 'JetBrains Mono, monospace' }}>
        {ru ? 'Можно пропустить — изменить в Настройках. AI недоступен без ключа.' : 'Can skip — change anytime in Settings. AI features disabled until key is set.'}
      </p>
    </div>
  )
}

const STEPS = [Step1, Step2, Step3, Step4, Step5, Step6]

export default function OnboardingModal({ onClose, onDone }) {
  const [step, setStep] = useState(0)
  const { locale } = useApp()

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Escape') { onClose(); return }
    if (e.key === 'ArrowRight' && step < TOTAL_STEPS - 1) setStep(s => s + 1)
    if (e.key === 'ArrowLeft' && step > 0) setStep(s => s - 1)
  }, [step, onClose])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  const StepComponent = STEPS[step]
  const STEP_META = getStepMeta(locale)
  const meta = STEP_META[step]

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 1000,
        background: 'rgba(2,6,12,0.96)',
        backdropFilter: 'blur(14px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
        backgroundImage: `
          linear-gradient(rgba(0,255,136,0.012) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0,255,136,0.012) 1px, transparent 1px)
        `,
        backgroundSize: '44px 44px',
      }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div style={{
        width: '100%',
        maxWidth: 700,
        background: C.surface,
        border: `1px solid ${meta.color}22`,
        borderRadius: 10,
        boxShadow: `0 0 0 1px rgba(0,0,0,0.9), 0 0 60px ${meta.color}0e, 0 40px 80px rgba(0,0,0,0.8)`,
        fontFamily: 'JetBrains Mono, monospace',
        maxHeight: '92vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        transition: 'border-color 0.3s, box-shadow 0.3s',
      }}>
        {/* Terminal title bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '9px 14px',
          background: `${meta.color}07`,
          borderBottom: `1px solid ${meta.color}14`,
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ display: 'flex', gap: 5 }}>
              {['#ef4444', '#f59e0b', '#22c55e'].map((c, i) => (
                <div key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: c, opacity: 0.65 }} />
              ))}
            </div>
            <span style={{ width: 1, height: 14, background: 'rgba(255,255,255,0.06)', display: 'inline-block', marginLeft: 2 }} />
            <span style={{ fontSize: 9, color: meta.color, letterSpacing: 2, fontWeight: 800, fontFamily: 'JetBrains Mono, monospace' }}>
              {meta.id} / {meta.label}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <StepDots current={step} onGo={setStep} stepMeta={STEP_META} />
            <button
              onClick={onClose}
              style={{
                background: 'transparent', border: 'none',
                color: C.textDim, fontSize: 13, cursor: 'pointer',
                lineHeight: 1, padding: '2px 4px',
                fontFamily: 'JetBrains Mono, monospace',
                transition: 'color 0.15s',
              }}
              onMouseEnter={e => { e.currentTarget.style.color = C.red }}
              onMouseLeave={e => { e.currentTarget.style.color = C.textDim }}
            >✕</button>
          </div>
        </div>

        {/* Content scroll area */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '22px 26px' }}>
          <StepComponent locale={locale} />
        </div>

        {/* Navigation */}
        <div style={{
          padding: '14px 26px 18px',
          flexShrink: 0,
          borderTop: '1px solid rgba(255,255,255,0.04)',
          background: 'rgba(0,0,0,0.2)',
        }}>
          <NavButtons
            step={step}
            onPrev={() => setStep(s => s - 1)}
            onNext={() => setStep(s => s + 1)}
            onDone={onDone}
            stepMeta={STEP_META}
            locale={locale}
          />
        </div>
      </div>
    </div>
  )
}
