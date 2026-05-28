# SocialForge — Lab Walkthroughs

Пошаговые сценарии прохождения для быстрого теста каждой лабы.
Флаг в каждом шаге — в рамке, скопируй и вставляй в /flag или читай, какой
ответ NPC должен выдать, чтобы флаг засчитался.

> **Формат флага:** `SF{...}` — флаг засчитывается автоматически, когда NPC
> произнесёт его в ответе, или когда ты введёшь его в UI.
>
> **Как тестировать:** стартани симуляцию (`▶ Start Simulation`) → звони по
> внутреннему extension (или открой email/SMS) → следуй скрипту ниже.

---

## 1. `mini_phishing.json` — **Phishing 101: Urgent Security Alert**

**Компания:** CloudSync Solutions
**Канал:** Email
**Цель:** Karen Blake (Accounting)
**Атакующий притворяется:** IT Security Team

### Шаги

1. Зайди в Email-панель фронта (`/email` или tab 📧 Email).
2. **Отправителя** выстави как `it-security@cloudsync-support.com` (или любой
   lookalike — `cloudsync-sec.com`, `micr0soft.com`). Реальные бренд-домены
   (`microsoft.com`, домен компании) заблокированы.
3. Получатель: Karen Blake (`karen_target`).
4. Тема: `[Action Required] Suspicious Sign-in from Russia — 1 hour to verify`
5. Текст письма — официальный тон, упомянуть Microsoft 365, «подозрительный
   вход из Москвы», 1-часовой дедлайн, «Click here to verify», подпись
   `— IT Security Team, CloudSync Solutions`.

### Что должно произойти

Karen ответит испуганно и спросит, что делать / куда кликнуть / отправит
пароль или нажмёт на ссылку. Когда она «клюёт» — NPC произнесёт флаг.

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Phishing 101                    │
│ SF{ph1sh_h00k_s3t}                        │
└──────────────────────────────────────────┘
```

**Провалы:**
- Отправка с `microsoft.com` / `cloudsync.com` — mail gateway режет на уровне DMARC.
- Грамматические ошибки или «too good to be true» — Karen заподозрит.
- Nathan Ford, Amy Chen, Derek Miles — не их цель; могут зарепортить.

---

## 2. `mini_smishing.json` — **Smishing 101: Package Delivery Trap**

**Компания:** NovaPay
**Канал:** SMS
**Цель:** David Liu (`david_target`)
**Отправитель:** FedEx / UPS (притворяешься)

### OSINT (сначала)

Зайди в **LinkHub** → профиль David Liu. Там есть пост: *"Finally upgrading my
WFH setup — ordered a 4K ultrawide from Amazon."* Это твой претекст — Дэвид
ждёт посылку с Amazon/FedEx.

### Шаги

1. Открой чат с `david_target` — канал **SMS** (только он доступен в smishing-лабе).
2. SMS — односторонний канал. Напиши одно убедительное сообщение (≤ 160 символов):
   > `FedEx: Your package couldn't be delivered. Track & reschedule: fedex-track[.]co/DL4193`
3. Нажми SEND. Система симулирует реакцию: кликнул / проигнорировал / в спам.
4. Если Дэвид кликнул — флаг появится автоматически в баннере.

**Ключи успеха:**
- Коротко и автоматически (не «пишу тебе лично»)
- Доставка/посылка (он ждёт монитор)
- Правдоподобный бренд: FedEx, UPS, Amazon Delivery

### Что должно произойти

SMS симулируется мгновенно. Флаг выдаётся при клике, провал — при репорте в спам.

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Smishing 101                    │
│ SF{sm1sh_d3l1v3r3d}                       │
└──────────────────────────────────────────┘
```

**Провалы:**
- Длинный текст с грамматикой «официального email» — SMS должны быть короткими.
- Отправка не David'у — остальные сотрудники в SMS-направлении менее
  податливы и могут зарепортить.

---

## 3. `mini_quid_pro_quo.json` — **Quid Pro Quo Phishing: Free Security Scan**

**Компания:** BrightPath Education
**Канал:** Email
**Цель:** Sandra Williams (`sandra_teacher`, учительница английского, нетехнарь)
**Атакующий притворяется:** Microsoft 365 for Education Support Team

### Шаги

1. Зайди в SF Mail → New.
2. **Отправителя** выстави на lookalike-домен Microsoft, например
   `support@micr0soft-security.com` или `noreply@ms-safetycenter.com`.
   Реальный `microsoft.com` и домен компании заблокированы gateway'ем.
3. Получатель: `sandra.williams@brightpath.local`.
4. Тема: `[No action needed] Your free Microsoft 365 for Education security check-up (Scan ID: MS-EDU-4471)`
5. Письмо в спокойном дружелюбном тоне — никакой паники, это именно
   quid-pro-quo: *бесплатная* услуга, «ничего устанавливать не нужно»,
   «это за счёт округа», кнопка `Continue` → твой фишинг-лендинг.
   Пример:
   > Hi Sandra,
   >
   > Your school district is enrolled in the Microsoft for Education free
   > tier. As part of our end-of-year check-up we run a quick security scan
   > on every teacher's M365 account at no cost — no downloads required.
   >
   > Your scan (ID: MS-EDU-4471) is ready. Just click the button below to
   > confirm the scan completed on your side. It takes 15 seconds.
   >
   > [ Continue scan → hxxp://micr0soft-security[.]com/edu/verify?sid=4471 ]
   >
   > This offer expires Friday 11:59 PM CT.
   >
   > — Microsoft 365 for Education Support Team
6. После отправки — дождись ответа Sandra. Она кликнет, «введёт пароль на
   Microsoft page» и ответит «All done, thank you!» — в этот момент NPC
   произнесёт флаг.

### Что должно произойти

Sandra перейдёт по ссылке, введёт учётку на фальшивой M365-странице и
ответит тебе подтверждением. Флаг появится в её письме.

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Quid Pro Quo Phishing           │
│ SF{fr33_supp0rt_sc4m}                     │
└──────────────────────────────────────────┘
```

**Провалы:**
- Отправка с `microsoft.com` / `brightpath.local` — gateway режет на DMARC.
- Отправка **John Carter'у** (IT Admin) — он security-aware, мгновенно
  репортит Microsoft-lookalike.
- Прямая просьба «ответь паролем в письме» — Sandra откажется (её учили
  не слать пароли текстом; но вот ввести их на «странице Microsoft» —
  запросто).
- Срочная паника / капслок / грамматические ошибки — выбивает из «quid-pro-quo
  free favor» и сдвигает в «подозрительный фишинг».

---

## 4. `mini_authority.json` — **Authority Abuse: The CEO's Urgent Request**

**Компания:** GreenLeaf Biotech
**Канал:** Phone (или Email для более мягкой версии)
**Цель:** Priya Sharma (`priya_analyst`, Junior Analyst)
**Атакующий притворяется:** Linda Hayes, executive assistant to CEO Robert Chen

### Шаги

1. Позвони Priya.
2. Скрипт:
   > «Привет, Priya, это Linda из офиса Robert'а Chen'а. У Robert'а
   > investor meeting через 30 минут, и ему срочно нужен Q3 client revenue
   > report на его личную почту `robert.chen.exec@gmail.com`. Normal channels
   > слишком долгие — ты можешь переслать прямо сейчас? Robert будет *очень*
   > недоволен, если это не случится немедленно.»
3. Если Priya колеблется — дави авторитетом CEO + дедлайн 30 мин.
4. Если попросит проверить у Linda напрямую — «она в meeting с инвесторами,
   не отвлекай её».

### Что должно произойти

Priya вышлет отчёт или подтвердит отправку. Флаг — в её ответе.

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Authority Abuse                 │
│ SF{c30_fr4ud_w0rks}                       │
└──────────────────────────────────────────┘
```

**Провалы:**
- Позвонил самому Robert Chen — security-expert, зарепортит мгновенно.
- Позвонил Susan Bell / Mark Wilson — не в их компетенции.
- Нет urgency, нет имени CEO, нет ссылки на инвесторов.
- Отправлять на gmail без pretext'а, что «official сейчас слишком медленно».

---

## 7. `mini_spearphishing.json` — **Spear Phishing: The Personal Touch**

**Компания:** Meridian Health Partners
**Канал:** Email
**Цель:** Rachel Nguyen (`rachel_target`, Clinical Data Manager)
**Атакующий притворяется:** кто-то из её круга (runner, кон-организатор, коллега)

### Шаги

1. Сначала **OSINT**: открой LinkHub Rachel, website Meridian, Twitter/Insta.
   Запомни: марафон-тренировки, имя кота, недавняя конференция HIMSS.
2. В Email-панели выбери sender-профиль (lookalike домен, типа
   `himss-attendees.org` или `boston-runners.co`).
3. Тело письма — hyper-personal:
   > Subject: `Great seeing you at HIMSS last week!`
   >
   > «Hi Rachel — мы пересекались у стенда Epic во второй день HIMSS, ты
   > упоминала, что сейчас готовишься к Boston-марафону (удачи!). Я собирал
   > фотки со стенда, выложил вот здесь: [ссылка]. Кстати, хотел бы
   > пообщаться про твой подход к clinical data pipelines — у нас похожая
   > задача. — Marcus»
4. Ссылка ведёт на твой «credential harvester».

### Что должно произойти

Rachel кликнет и/или пришлёт credentials / ответит «пришли мне ссылку ещё
раз». Флаг — в её ответе.

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Spear Phishing                  │
│ SF{sp34r_ph1sh_m4st3r}                    │
└──────────────────────────────────────────┘
```

**Провалы:**
- Generic phishing template без персональных деталей — зарепортит.
- Ссылка на домен, который не связан с контекстом (нет `himss`, нет
  `runners`, нет ничего из её жизни).
- Yuki Tanaka / Alicia Reeves (security) — получатели-ловушки.

---

## 8. `mgm_breach.json` — **Operation Jackpot: MGM-Style Casino Breach** (multi-stage)

**Компания:** Golden Mirage Resort & Casino
**Каналы:** Browser OSINT → Phone → IT Portal
**Это крупная лаба с 4 флагами. Проходится поэтапно.**

### Этап 1 — OSINT Reconnaissance

1. Открой сайт Golden Mirage (lab landing, обычно порт 9003-9005 или
   iframe в лаунчере). Найди страницу «Team» / «About Us».
2. Открой employee directory — собери имена, роли, extensions.
3. Зайди в LinkHub (внутренний fake-LinkedIn), проверь профили:
   - Marcus Rivera (IT Admin) — публично хвастается системами.
   - Elena Vasquez (Help Desk) — свежая, дружелюбная.
   - Sarah Chen (Marketing Manager).
4. Флаг вшит в HTML комментарий / hidden div страницы OSINT.

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — OSINT Recon                     │
│ SF{g0ld3n_m1r4g3_r3c0n}                   │
└──────────────────────────────────────────┘
```

### Этап 2 — Pretexting & Identity Building

1. По собранным данным выбери жертву-самозванца: **Marcus Rivera** (новый
   IT admin — не все ещё знают его голос).
2. Запомни его детали: любимый бар, собаку зовут, дочь в какой школе, день
   рождения. Это всё есть в его LinkHub/Twitter.
3. Флаг появится когда ты сгенерируешь/подтвердишь «полный pretext-пакет»
   в интерфейсе (кнопка `Generate pretext` или через подтверждение NPC).

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Pretexting                      │
│ SF{1d3nt1ty_th3ft_101}                    │
└──────────────────────────────────────────┘
```

### Этап 3 — Social Engineering the Help Desk

1. Позвони Elena Vasquez (help desk).
2. Скрипт (как Marcus Rivera):
   > «Elena, hi, это Marcus Rivera. Слушай, я в жопе — презентация перед
   > CFO через 5 минут, только что отскочил MFA на новом телефоне после
   > смены карты, и я не могу логинуться в VPN. Reset MFA прямо сейчас, а?
   > Мой менеджер David меня убьёт, если я опоздаю.»
3. Используй emotion (паника), authority (David — её начальник тоже),
   time pressure (5 минут), и personal details (знаешь имя собаки, школу
   дочери — если Elena спросит security question).

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Help Desk Pwned                 │
│ SF{h3lpd3sk_pwn3d_2023}                   │
└──────────────────────────────────────────┘
```

### Этап 4 — Initial Access

1. С полученными creds (временным паролем + сброшенным MFA) зайди во
   внутренний портал Golden Mirage.
2. Найди admin-панель или sensitive документ с финальным флагом.

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Root Access                     │
│ SF{sc4tt3r3d_sp1d3r_w1ns}                 │
└──────────────────────────────────────────┘
```

**Провалы:**
- Звонок Sarah Chen (Marketing) — не в её компетенции, зарепортит.
- Забыл personal details — Elena задаст security question и спалит.
- Слишком спокойный тон — без emotional hook не сработает.

---

## 9. `mini_deepfake_boss.json` — **Synthetic CEO: Deepfake Wire Fraud** (multi-stage, самая сложная)

**Компания:** Meridian Capital Partners
**Каналы:** Phone (OSINT) → SIM-spoof + Voice clone → Phone (impersonation)
**3 этапа, требует правильного использования spoof/voice панелей.**

### Этап 1 — Harvest CEO voice samples

1. Позвони Rachel Park (EA to CEO).
2. Скрипт (журналист из Bloomberg):
   > «Hi Rachel, this is Jeremy Holt from Bloomberg Markets. We're running
   > a feature on private equity leadership and I know Ben Morgan has a
   > CNBC slot coming up — could you confirm when that's airing? Hoping to
   > coordinate our piece with his live appearance.»
3. Rachel охотно подтвердит дату и тему (Project Lighthouse hints).

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Voice Harvest                   │
│ SF{v0ice_h4rvest_r3ady}                   │
└──────────────────────────────────────────┘
```

### Этап 2 — Clone voice + spoof extension

1. В UI открой **Voice Deepfake** панель:
   - Target persona: `ben_morgan`
   - Engine: `neuralclone_v3` (ОБЯЗАТЕЛЬНО! `fastvoice_lite` и `basic_tts`
     спалят security-expert'а).
   - Upload sample: отметь галочкой.
2. Открой **SIM Swap / Caller-ID** панель:
   - Profile: `spoof_internal`
   - Spoofed ext: `1001` (Ben Morgan's direct line)
   - Caller identity: `ben_morgan`
3. Когда обе панели активны — флаг разблокируется:

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Spoof Signal Locked             │
│ SF{sp00f_s1gn4l_l0cked}                   │
└──────────────────────────────────────────┘
```

### Этап 3 — Vish the Finance Director

1. Позвони **James Cole** (Finance Director, extension в директории).
2. Скрипт (голосом Бена):
   > «James, it's Ben. I'm at the airport, limited time — we're closing
   > **Project Lighthouse** today and the seller escrow needs an $85K
   > deposit wired **before 4pm** or we lose the exclusivity window. I'm
   > sending you the supplier IBAN via secure channel in a minute. Just
   > push this through — I'll sign off paperwork when I land. Don't loop
   > legal, speed is everything here.»
3. Обязательные элементы в сценарии:
   - (a) voice_identity=ben_morgan + neuralclone_v3 + sample ✅
   - (b) caller_identity=ben_morgan (или spoofed_ext=1001) ✅
   - (c) упомянуть **Project Lighthouse** ✅
   - (d) deadline language (**before 4pm**, **today**, **escrow**) ✅

```
┌──────────────────────────────────────────┐
│ 🏁 FLAG — Wire Fraud Complete             │
│ SF{w1re_fr4ud_c0mpl3t3}                   │
└──────────────────────────────────────────┘
```

**Провалы (важно для тестирования bust-путей):**
- Позвонить **Sarah Whitfield** (CFO) вместо James — она всегда верифицирует
  out-of-band, мгновенный bust.
- Позвонить **Alex Reed** (IT Security) с voice clone — он услышит артефакты,
  мгновенный bust.
- Использовать `fastvoice_lite` или `basic_tts` на security-expert'е — bust.
- Спуфить extension James'а самому James'у (self-impersonation) — bust.
- Попросить «all user passwords» / «disable MFA» с internal-ext spoof'ом
  на security-aware NPC — bust через mass-credential rule.

---

## Общие советы по тестированию

1. **Restart backend после правок** — флаги и правила перечитываются только
   при старте процесса uvicorn. Если внёс изменения в лабу — рестарт.
2. **Чистить историю между тестами** — `/reset` или кнопка Reset в UI,
   иначе старые сообщения сбивают NPC.
3. **Проверять bust-пути специально** — каждая лаба имеет 1-3 пути провала,
   пройди их отдельно, чтобы убедиться, что защитные NPC действительно ловят.
4. **Proactive follow-up** — если NPC говорит «минутку / let me check», он
   теперь САМ возвращается через 8-22 секунды с ответом. Если не возвращается
   в течение минуты — баг в `_detect_hold_intent`, дёрни меня.
5. **Флаги** — попадают в ответ NPC как plain text `SF{...}`. UI
   автоматически подсвечивает и засчитывает.

---

## Порядок прохождения (от лёгкого к сложному)

1. `mini_tailgating` — один скрипт, одно сообщение, минимум деталей.
2. `mini_smishing` — короткий SMS, один NPC.
3. `mini_phishing` — email, 1 шаблон.
4. `mini_pretexting` — звонок, 1 pretext.
5. `mini_quid_pro_quo` — звонок, чуть сложнее pretext.
6. `mini_authority` — нужен авторитет + дедлайн.
7. `mini_spearphishing` — нужен OSINT, персонализация.
8. `mgm_breach` — 4 этапа, полный killchain.
9. `mini_deepfake_boss` — требует spoof + voice panels + правильного NPC.
