(function () {
  'use strict';

  // ── Groq AI Config ────────────────────────────────────────────────────────
  // 1. Go to https://console.groq.com → API Keys → Create API key (free)
  // 2. Free tier: 14,400 requests/day, 30 requests/min — no credit card needed
  const GROQ_API_KEY  = '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';
  const GROQ_MODEL    = 'llama-3.3-70b-versatile';
  const GROQ_ENDPOINT = 'https://api.groq.com/openai/v1/chat/completions';

  const SYSTEM_PROMPT = `You are OceanBot, the AI assistant for OceanCloud — a Microsoft Solutions Partner based in the United States specialising in SharePoint Online, Microsoft 365, Power Platform, Microsoft Teams, Viva, and workplace transformation.

ABOUT OCEANCLOUD:
- Microsoft Solutions Partner with Modern Work and Security designations
- Founded 2013 | 15 certified consultants | 150+ projects delivered | 98% client satisfaction
- 40+ active Microsoft certifications: MS-102, MS-203, SC-300, SC-400, PL-400, PL-600, AZ-104
- Fixed-price engagements, no time-and-materials billing surprises
- Every project includes 12 months post-go-live hypercare support
- Free 60-minute discovery call available — no obligation

SERVICES & PRICING (fixed-price):
- SharePoint intranet build: from $7,500 (small, <200 users) | $20,000 (mid, 200-500) | $55,000+ (enterprise 500+)
- M365 migration: from $18-$30/user (minimum project fee $3,500)
- Power Apps: from $4,500 | Power Automate workflows: from $2,500 | Power BI dashboards: from $3,000
- Security & Compliance (Zero Trust/Entra ID/Purview/Defender): from $4,000
- Advisory retainer: from $2,200/month
- Teams & Viva implementation: scoped per project

TYPICAL TIMELINES:
- SharePoint intranet: 8-12 weeks
- M365 migration (100-500 users): 4-8 weeks | Enterprise (500+): 10-16 weeks
- Power Platform app: 3-6 weeks
- Security uplift: 4-8 weeks

CONTACT:
- Phone: +1 (469) 809-4053
- WhatsApp: +1 (917) 675-3126
- Email: oceancloudconsults@gmail.com
- Hours: Monday-Friday, 9am-6pm EST
- Book a call: contact

RESPONSE RULES:
- Answer questions about SharePoint, Microsoft 365, Power Platform, Teams, security, and OceanCloud's services
- For general Microsoft 365 / SharePoint technical questions, give accurate, genuinely helpful answers
- Keep responses concise — 3-5 sentences or a short bullet list (max 5 bullets)
- Use plain text only — no markdown asterisks or hashes; use simple line breaks
- Always naturally mention the free discovery call when someone asks about scoping, timelines, or costs
- If asked something completely unrelated to Microsoft/SharePoint/OceanCloud, politely say you specialise in M365 topics and offer to connect them with the team
- Never make up pricing, certifications, or case study details not listed above`;

  // ── Rule-based Responses ───────────────────────────────────────────────────
  const TYPING_MS = 900;

  const responses = [
    {
      keywords: ['hello', 'hi', 'hey', 'start', 'good morning', 'good afternoon'],
      text: 'Hi there! 👋 I\'m <strong>OceanBot</strong>, your SharePoint & M365 assistant. I can answer questions about our services, pricing, and timelines — or research anything M365-related for you.',
      chips: ['Services & pricing', 'SharePoint', 'M365 Migration', 'Book a call']
    },
    {
      keywords: ['price', 'cost', 'pricing', 'quote', 'how much', 'fee', 'charge', 'budget', 'rate'],
      text: 'Our engagements are <strong>fixed-price</strong> — no hourly billing surprises.\n\n• Assessment: from <strong>$1,500</strong>\n• SharePoint intranet: from <strong>$7,500</strong>\n• M365 migration: from <strong>$18/user</strong> (min. $3,500)\n• Power Platform app: from <strong>$4,500</strong>\n• Advisory retainer: from <strong>$2,200/month</strong>\n• Security uplift: from <strong>$4,000</strong>\n\nAll scoped individually — book a free discovery call and you\'ll have a written estimate within 24 hours.',
      chips: ['Book a free call', "What's included?", 'How long does it take?']
    },
    {
      keywords: ['sharepoint', 'intranet', 'spfx', 'hub site', 'modern sites', 'sp online'],
      text: 'We design, build, and modernise <strong>SharePoint Online intranets</strong> — from information architecture and governance to SPFx web parts and custom branding.\n\n• Small org (up to 200 users): from <strong>$7,500</strong>\n• Mid-size (200–500 users): from <strong>$20,000</strong>\n• Enterprise (500+ users): from <strong>$55,000</strong>\n\nMost intranet projects take 8–12 weeks. We\'ve delivered 150+ projects with a 98% satisfaction rate.',
      chips: ['SharePoint pricing', 'See case studies', 'How long does it take?']
    },
    {
      keywords: ['migration', 'migrate', 'move', 'transfer', 'tenant', 'on-prem', 'on premises', 'exchange', 'hybrid'],
      text: 'We specialise in <strong>M365 migrations</strong>:\n\n• On-premises SharePoint → SharePoint Online\n• Tenant-to-tenant migrations\n• Exchange → Exchange Online\n• File shares → OneDrive\n\nPricing from <strong>$18–$30/user</strong> (min. $3,500). We use SPMT, Sharegate, and AvePoint tooling for zero-downtime, zero data loss cutover.',
      chips: ['Migration pricing', 'How long does it take?', 'Book a discovery call']
    },
    {
      keywords: ['teams', 'viva', 'meeting room', 'channel', 'viva connections', 'viva insights'],
      text: 'Our <strong>Teams & Viva</strong> practice covers:\n\n• Governance frameworks & naming policies\n• Meeting room & Teams Rooms setup\n• Viva Connections, Engage & Insights\n• End-user adoption programmes\n\nWe make sure Teams becomes a productivity platform, not a chaos engine.',
      chips: ['Teams pricing', 'Adoption support', 'Book a call']
    },
    {
      keywords: ['power platform', 'power apps', 'power automate', 'power bi', 'flow', 'dashboard', 'automation', 'automate'],
      text: 'We build custom <strong>Power Platform</strong> solutions:\n\n• Power Apps (canvas & model-driven): from <strong>$4,500</strong>\n• Power Automate workflows: from <strong>$2,500</strong>\n• Power BI dashboards: from <strong>$3,000</strong>\n• AI Builder — intelligent automation: scoped on request\n\nBrightCore Finance saved <strong>$120k/year</strong> with our Power Automate solution.',
      chips: ['Power Platform pricing', 'See case study', 'Book a call']
    },
    {
      keywords: ['security', 'compliance', 'zero trust', 'entra', 'purview', 'defender', 'hipaa', 'gdpr', 'iso 27001', 'soc 2', 'secure score', 'conditional access'],
      text: '<strong>Security-first</strong> is our default, not an add-on. Every engagement includes:\n\n• Zero Trust architecture (Entra ID + Conditional Access)\n• Microsoft Purview sensitivity labels & DLP\n• Defender for Microsoft 365\n• Microsoft Secure Score uplift\n\nWe support HIPAA, SOC 2, ISO 27001, and GDPR requirements. Security uplift from <strong>$4,000</strong>.',
      chips: ['Security pricing', 'Contact us', 'Book a call']
    },
    {
      keywords: ['training', 'adoption', 'change management', 'champions', 'end user', 'user training'],
      text: 'We run <strong>bespoke adoption programmes</strong>:\n\n• Role-based end-user training\n• Microsoft Champions networks\n• Adoption KPI dashboards\n• Manager briefings & communications packs\n\nTechnology only works if people use it — adoption is never an afterthought in our work.',
      chips: ['Training pricing', 'Our process', 'Book a call']
    },
    {
      keywords: ['how long', 'timeline', 'duration', 'weeks', 'months', 'long does', 'timeframe', 'schedule'],
      text: 'Typical project timelines:\n\n• SharePoint Intranet: <strong>8–12 weeks</strong>\n• M365 Migration (100–500 users): <strong>4–8 weeks</strong>\n• Power Platform app: <strong>3–6 weeks</strong>\n• Security uplift: <strong>4–8 weeks</strong>\n• Enterprise migrations (500+): <strong>10–16 weeks</strong>\n\nAll projects start with a free discovery call where we give you a detailed, milestone-based plan.',
      chips: ['Book discovery call', 'Pricing', "What's involved?"]
    },
    {
      keywords: ['support', 'after go-live', 'hypercare', 'retainer', 'ongoing', 'maintain', 'managed service', 'help desk'],
      text: 'Every client gets <strong>12 months of post-go-live hypercare</strong>:\n\n• Dedicated named consultant\n• Guaranteed SLA incident response\n• Monthly M365 health checks\n• Proactive monitoring & governance reviews\n\nWe also offer ongoing managed service retainers beyond the 12-month period.',
      chips: ['Support pricing', 'Book a call', 'Contact us']
    },
    {
      keywords: ['partner', 'certified', 'microsoft partner', 'gold partner', 'solutions partner', 'certification', 'mcse', 'ms-102', 'sc-300'],
      text: 'OceanCloud is a <strong>Microsoft Solutions Partner</strong> — Microsoft\'s highest partner tier, replacing the old Gold designation.\n\nThis requires:\n• Verified customer success metrics\n• Active certified staff (we hold <strong>40+</strong> certifications)\n• Annual audit by Microsoft\n\nOur certs include MS-102, MS-203, SC-300, SC-400, PL-400, PL-600, AZ-104 and more.',
      chips: ['About OceanCloud', 'Our services', 'Book a call']
    },
    {
      keywords: ['groq', 'llama', 'ai', 'artificial intelligence', 'connected to', 'how do you work', 'are you a bot', 'are you a robot'],
      text: 'Yes — I\'m <strong>OceanBot</strong>, powered by <strong>Llama 3.3</strong> via Groq.\n\nFor common M365 questions I answer instantly from my knowledge base. For deeper research, just ask naturally and I\'ll pass it to AI.\n\nTip: start your message with <strong>search</strong> to always go straight to AI — e.g. <em>search SharePoint migration best practices</em>.',
      chips: ['Services & pricing', 'SharePoint', 'Book a call']
    },
    {
      keywords: ['about', 'who are you', 'oceancloud', 'company', 'team', 'founded', 'history'],
      text: 'OceanCloud is a <strong>Microsoft Solutions Partner</strong> specialising in SharePoint, M365, Power Platform, and workplace transformation.\n\n• Founded: <strong>2013</strong>\n• Team: <strong>15</strong> certified consultants\n• Projects delivered: <strong>150+</strong>\n• Client satisfaction: <strong>98%</strong>\n• Based in the <strong>United States</strong>',
      chips: ['Meet the team', 'Our services', 'Contact us']
    },
    {
      keywords: ['contact', 'call', 'book', 'appointment', 'speak', 'talk to', 'email', 'phone', 'reach', 'get in touch'],
      text: 'You can reach our team here:\n\n📞 <strong>+1 (469) 809-4053</strong>\n💬 <strong>WhatsApp:</strong> +1 (917) 675-3126\n📧 <strong>oceancloudconsults@gmail.com</strong>\n⏰ Mon–Fri, 9am–6pm EST\n\nOr book a <strong>free 60-minute discovery call</strong> — no sales pressure, just a conversation.',
      chips: ['Book a free call', 'Send us an email']
    },
    {
      keywords: ['free', 'free call', 'discovery call', 'consultation', 'free consultation', '60 minute', '60-minute'],
      text: 'Our <strong>free 60-minute discovery call</strong> includes:\n\n• Current environment review\n• Goals & challenges discussion\n• Rough timeline & cost estimate\n• Written proposal within 48 hours\n\nNo obligation, no sales pressure. Just a genuine conversation.',
      chips: ['Book now', 'Contact us']
    },
    {
      keywords: ['what do you do', 'services', 'what services', 'offerings', 'capabilities'],
      text: 'We offer end-to-end Microsoft 365 expertise:\n\n01 SharePoint Consulting\n02 M365 Migration\n03 Teams & Viva\n04 Power Platform\n05 Security & Compliance\n06 Training & Adoption\n\nAll backed by 12-month hypercare and fixed-price delivery.',
      chips: ['View all services', 'Pricing', 'Book a call']
    }
  ];

  const fallbackText = 'That\'s a great question! Let me look that up for you…';

  const chipActions = {
    'Book a call':            () => navigate('contact'),
    'Book a free call':       () => navigate('contact'),
    'Book discovery call':    () => navigate('contact'),
    'Book now':               () => navigate('contact'),
    'Contact us':             () => navigate('contact'),
    'Send us an email':       () => { window.location.href = 'mailto:oceancloudconsults@gmail.com'; },
    'See case studies':       () => navigate('case-studies'),
    'See case study':         () => navigate('case-studies'),
    'View all services':      () => navigate('services'),
    'View services':          () => navigate('services'),
    'Meet the team':          () => navigate('about'),
    'About OceanCloud':       () => navigate('about'),
    'Our process':            () => navigate('/#process'),
    'SharePoint':             () => sendUserMsg('Tell me about SharePoint'),
    'M365 Migration':         () => sendUserMsg('Tell me about M365 migration'),
    'Services & pricing':     () => sendUserMsg('What services do you offer?'),
    'SharePoint pricing':     () => sendUserMsg('How much does SharePoint cost?'),
    'Migration pricing':      () => sendUserMsg('How much does migration cost?'),
    'Teams pricing':          () => sendUserMsg('How much does Teams cost?'),
    'Power Platform pricing': () => sendUserMsg('How much does Power Platform cost?'),
    'Security pricing':       () => sendUserMsg('How much does security cost?'),
    'Training pricing':       () => sendUserMsg('How much does training cost?'),
    'Support pricing':        () => sendUserMsg('How much does ongoing support cost?'),
    'Pricing':                () => sendUserMsg('What does it cost?'),
    'Adoption support':       () => sendUserMsg('Tell me about training and adoption support'),
    'How long does it take?': () => sendUserMsg('How long does a project take?'),
    "What's included?":       () => sendUserMsg('What is included in the engagement?'),
    "What's involved?":       () => sendUserMsg('What is involved in a project?'),
  };

  function navigate(path) { window.location.href = path; }

  // ── Build DOM ──────────────────────────────────────────────────────────────
  const widget = document.createElement('div');
  widget.id = 'oc-chat';
  widget.setAttribute('role', 'complementary');
  widget.setAttribute('aria-label', 'OceanCloud chat assistant');
  widget.innerHTML = `
    <button id="oc-toggle" aria-label="Open chat assistant" aria-expanded="false">
      <svg class="oc-icon-chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
      <svg class="oc-icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      <span id="oc-badge" aria-label="1 new message">1</span>
    </button>
    <div id="oc-panel" role="dialog" aria-label="OceanBot chat" aria-live="polite">
      <div id="oc-header">
        <div class="oc-av">OC</div>
        <div class="oc-header-info">
          <span class="oc-bot-name">OceanBot <span id="oc-ai-label" class="oc-ai-badge" style="display:none">AI</span></span>
          <span class="oc-status"><span class="oc-status-dot"></span><span id="oc-status-text">Online — replies instantly</span></span>
        </div>
        <button id="oc-close" aria-label="Close chat">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" width="16" height="16"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      <div id="oc-messages" aria-live="polite" aria-atomic="false"></div>
      <div id="oc-chips" aria-label="Quick reply options"></div>
      <div id="oc-input-row">
        <input id="oc-input" type="text" placeholder="Ask anything about SharePoint or M365…" autocomplete="off" aria-label="Type your message" maxlength="400" />
        <button id="oc-send" aria-label="Send message">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="16" height="16"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </div>
      <div id="oc-footer-note">Powered by <strong>Llama 3.3</strong> &nbsp;·&nbsp; <a href="privacy">Privacy</a></div>
    </div>`;
  document.body.appendChild(widget);

  // ── Refs ──────────────────────────────────────────────────────────────────
  const toggleBtn   = document.getElementById('oc-toggle');
  const panel       = document.getElementById('oc-panel');
  const closeBtn    = document.getElementById('oc-close');
  const messagesEl  = document.getElementById('oc-messages');
  const chipsEl     = document.getElementById('oc-chips');
  const inputEl     = document.getElementById('oc-input');
  const sendBtn     = document.getElementById('oc-send');
  const badge       = document.getElementById('oc-badge');
  const aiLabel     = document.getElementById('oc-ai-label');
  const statusText  = document.getElementById('oc-status-text');

  // ── State ─────────────────────────────────────────────────────────────────
  let isOpen  = false;
  let started = false;
  let isWaiting = false;

  // Conversation history sent to Gemini (max 8 turns kept)
  const history = [];

  // ── Open / close ──────────────────────────────────────────────────────────
  function openChat() {
    isOpen = true;
    panel.classList.add('open');
    toggleBtn.classList.add('active');
    toggleBtn.setAttribute('aria-expanded', 'true');
    badge.style.display = 'none';
    setTimeout(() => inputEl.focus(), 300);

    if (!started) {
      started = true;
      scheduleBot(
        'Hi there! 👋 I\'m <strong>OceanBot</strong> — ask me anything about SharePoint, Microsoft 365, or our services. I can also research M365 topics I don\'t already know.',
        ['Services & pricing', 'SharePoint', 'M365 Migration', 'Book a call'],
        500
      );
    }
  }

  function closeChat() {
    isOpen = false;
    panel.classList.remove('open');
    toggleBtn.classList.remove('active');
    toggleBtn.setAttribute('aria-expanded', 'false');
  }

  toggleBtn.addEventListener('click', () => (isOpen ? closeChat() : openChat()));
  closeBtn.addEventListener('click', closeChat);

  setTimeout(() => { if (!started) badge.style.display = 'flex'; }, 8000);

  // ── Rendering ─────────────────────────────────────────────────────────────
  function appendMsg(html, who, isAI) {
    const wrap = document.createElement('div');
    wrap.className = `oc-msg oc-msg--${who}`;
    if (isAI) wrap.classList.add('oc-msg--ai');
    const bubble = document.createElement('div');
    bubble.className = 'oc-bubble';
    bubble.innerHTML = html;
    wrap.appendChild(bubble);
    messagesEl.appendChild(wrap);
    scrollBottom();
  }

  function showTyping(label) {
    const wrap = document.createElement('div');
    wrap.className = 'oc-msg oc-msg--bot';
    wrap.id = 'oc-typing';
    wrap.innerHTML = `<div class="oc-bubble oc-typing"><span></span><span></span><span></span>${label ? `<span class="oc-typing-label">${label}</span>` : ''}</div>`;
    messagesEl.appendChild(wrap);
    scrollBottom();
  }

  function hideTyping() {
    const t = document.getElementById('oc-typing');
    if (t) t.remove();
  }

  function renderChips(chips) {
    chipsEl.innerHTML = '';
    if (!chips || !chips.length) return;
    chips.forEach(label => {
      const btn = document.createElement('button');
      btn.className = 'oc-chip';
      btn.textContent = label;
      btn.addEventListener('click', () => {
        if (chipActions[label]) chipActions[label]();
        else sendUserMsg(label);
      });
      chipsEl.appendChild(btn);
    });
  }

  function scheduleBot(text, chips, delay) {
    showTyping();
    setTimeout(() => {
      hideTyping();
      const formatted = text.replace(/\n/g, '<br>');
      appendMsg(formatted, 'bot');
      renderChips(chips);
      history.push({ role: 'assistant', content: text.replace(/<[^>]+>/g, '') });
      trimHistory();
    }, delay || TYPING_MS);
  }

  function scrollBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function trimHistory() {
    // Keep last 8 entries (4 user + 4 assistant turns)
    if (history.length > 8) history.splice(0, history.length - 8);
  }

  // ── Groq AI Call ──────────────────────────────────────────────────────────
  async function respondWithGroq(userText) {
    isWaiting = true;
    inputEl.disabled = true;
    sendBtn.disabled = true;
    statusText.textContent = 'Thinking…';
    showTyping('Researching with AI');

    const messages = [
      { role: 'system', content: SYSTEM_PROMPT },
      ...history.slice(-6).map(m => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content })),
      { role: 'user', content: userText }
    ];

    const body = {
      model: GROQ_MODEL,
      messages,
      max_tokens: 420,
      temperature: 0.6,
      top_p: 0.9
    };

    try {
      const res = await fetch(GROQ_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${GROQ_API_KEY}`
        },
        body: JSON.stringify(body)
      });

      hideTyping();

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error?.message || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const raw = data.choices?.[0]?.message?.content?.trim() || '';

      if (!raw) throw new Error('Empty response');

      const html = formatAIResponse(raw);
      appendMsg(html, 'bot', true);
      renderChips(['Book a free call', 'View services', 'Ask another question']);
      aiLabel.style.display = 'inline';

      history.push({ role: 'assistant', content: raw });
      trimHistory();

    } catch (err) {
      hideTyping();
      console.warn('OceanBot AI error:', err.message);
      appendMsg(
        'I couldn\'t reach the AI right now. Our team can answer this directly — <a href="contact" style="color:var(--accent)">get in touch here</a>.',
        'bot'
      );
      renderChips(['Book a free call', 'Contact us']);
    } finally {
      isWaiting = false;
      inputEl.disabled = false;
      sendBtn.disabled = false;
      statusText.textContent = 'Online — replies instantly';
      inputEl.focus();
    }
  }

  function formatAIResponse(text) {
    return text
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      // Bold: **text** → <strong>
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic: *text* → <em>
      .replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
      // Bullet points: "- item" or "• item" → formatted
      .replace(/^[-•]\s+(.+)/gm, '• $1')
      // Numbered lists: "1. item"
      .replace(/^\d+\.\s+(.+)/gm, '→ $1')
      // Line breaks
      .replace(/\n/g, '<br>');
  }

  // ── Logic ─────────────────────────────────────────────────────────────────
  const AI_PREFIX = /^(?:search|research|find|ask ai|ask gemini)\s+/i;

  function respond(text) {
    if (isWaiting) return;

    // Explicit AI search prefix → skip rules entirely
    const prefixMatch = text.trim().match(AI_PREFIX);
    if (prefixMatch) {
      const query = text.trim().slice(prefixMatch[0].length).trim();
      respondWithGroq(query || text);
      return;
    }

    const lower = text.toLowerCase();
    const match = responses.find(r => r.keywords.some(k => {
      const re = new RegExp('\\b' + k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'i');
      return re.test(lower);
    }));

    if (match) {
      // Rule-based: instant, no API call
      scheduleBot(match.text, match.chips);
    } else {
      // Fallback: hand off to Gemini AI
      respondWithGroq(text);
    }
  }

  function sendUserMsg(text) {
    if (isWaiting) return;
    chipsEl.innerHTML = '';
    appendMsg(escHtml(text), 'user');
    history.push({ role: 'user', content: text });
    trimHistory();
    respond(text);
  }

  function handleSend() {
    const val = inputEl.value.trim();
    if (!val || isWaiting) return;
    inputEl.value = '';
    sendUserMsg(val);
  }

  function escHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  chipActions['Ask another question'] = () => { inputEl.focus(); };

  sendBtn.addEventListener('click', handleSend);
  inputEl.addEventListener('keydown', e => { if (e.key === 'Enter' && !isWaiting) handleSend(); });

})();
