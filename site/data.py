# -*- coding: utf-8 -*-
"""Content model for the SKOT Communications site."""

SITE = {
    "name": "SKOT Communications",
    "tagline": "Find your voice. Speak to your people.",
    "email": "info@skotcomms.com",
    "phone": "+234 902 000 0677",
    "phone_href": "+2349020000677",
    "address": ["4th Floor, NIJ House", "20 Adeyemo Alakija", "Victoria Island, Lagos"],
    "linkedin": "https://www.linkedin.com/company/skot-communications/",
    "instagram": "https://www.instagram.com/skot.comms/",
}

# ── Navigation ──────────────────────────────────────────────────────────────
NAV = [
    {"label": "About", "href": "about.html"},
    {"label": "Expertise", "href": "expertise.html", "key": "expertise"},
    {"label": "Case studies", "href": "case-studies.html"},
    {"label": "Insights", "href": "insights.html"},
    {"label": "Programmes", "href": "programmes.html", "key": "programmes"},
]

# ── Expertise ───────────────────────────────────────────────────────────────
EXPERTISE = [
    {
        "slug": "corporate-brand",
        "num": "01",
        "title": "Corporate & Brand Communications",
        "short": "Corporate & Brand",
        "lede": "Strong reputations and enduring brands are built on a clear sense of purpose, positioning and voice.",
        "body": "We bring these together across corporate, brand, investor, consumer and internal communications to align narratives with business ambition.",
        "image": "assets/img/exp-corporate.jpg",
        "alt": "A full boardroom in session around a long table",
        "capabilities": [
            ("Strategic Communications", "Narrative architecture, messaging frameworks and communications planning built around business objectives."),
            ("Investor Relations", "Equity stories, results communications and investor engagement that hold up to scrutiny."),
            ("Consumer Campaigns", "Brand campaigns that move audiences from awareness to preference."),
            ("Social Impact", "Purpose programmes with a credible link between commitment and delivery."),
            ("Corporate Events & Product Launches", "Milestone moments designed as communications assets, not just occasions."),
            ("Internal Communications", "Change, culture and leadership communication for the audience closest to you."),
        ],
    },
    {
        "slug": "public-affairs",
        "num": "02",
        "title": "Public Affairs & Advocacy",
        "short": "Public Affairs",
        "lede": "Influence is built through a clear understanding of the stakeholders, policies and environments shaping an organisation's operating landscape.",
        "body": "Our public affairs approach combines stakeholder intelligence, government relations, policy engagement and strategic communications to build credibility and influence where decisions are actually made.",
        "image": "assets/img/exp-public.jpg",
        "alt": "A stakeholder briefing in progress, participants in active discussion",
        "capabilities": [
            ("Government Relations", "Structured engagement with the institutions that set the terms of your operating environment."),
            ("Stakeholder Mapping & Engagement", "Knowing who matters, what moves them, and in what order to reach them."),
            ("Policy & Regulatory Monitoring", "Early sight of the regulatory change that affects your business."),
            ("Policy Communications", "Turning technical positions into arguments that non-specialists can act on."),
        ],
    },
    {
        "slug": "digital-creative",
        "num": "03",
        "title": "Digital & Creative Strategy",
        "short": "Digital & Creative",
        "lede": "Digital presence should do more than generate attention; it should build relevance, distinction and meaningful engagement.",
        "body": "We connect strategy, creativity, content and digital channels to strengthen brands and create experiences that move audiences to action.",
        "image": "assets/img/exp-digital.jpg",
        "alt": "A creative strategy session, colleagues contributing ideas",
        "capabilities": [
            ("Digital Strategy", "Channel, content and audience strategy grounded in what the data actually shows."),
            ("Digital Marketing", "Paid, owned and earned working as one system rather than three budgets."),
            ("Social Media Management", "Always-on presence with a consistent voice and a real editorial standard."),
            ("Creative Design", "Visual systems that carry the narrative across every surface."),
            ("Influencer Management", "Credible voices, matched to audience and vetted for risk."),
            ("Brand Strategy & Identity", "Positioning, naming and identity systems built to last."),
        ],
    },
    {
        "slug": "crisis-reputation",
        "num": "04",
        "title": "Crisis & Reputation Management",
        "short": "Crisis & Reputation",
        "lede": "Reputation is shaped long before a crisis and tested when one arrives.",
        "body": "We bring strategic counsel, issues management, crisis preparedness and response expertise to help organisations anticipate risk, navigate complexity and protect trust.",
        "image": "assets/img/exp-crisis.jpg",
        "alt": "A delegate listening closely during a press briefing",
        "capabilities": [
            ("Crisis Communications Strategy", "Response frameworks, holding positions and decision protocols agreed before you need them."),
            ("Issues Management", "Early identification and containment of the issues that become crises."),
            ("Reputation Management", "Long-term stewardship of how an organisation is understood."),
            ("Training & Simulations", "Media training and live crisis simulations that test the plan under pressure."),
        ],
    },
]

# ── Method ──────────────────────────────────────────────────────────────────
# (icon key, title, body) — the icon key selects a glyph from METHOD_ICONS in build.py
# Home "Recent results": (case slug, headline figure, what it measures).
# The first entry is the lead number. The link comes from CASES; no client name is shown.
HOME_RESULTS = [
    ("arla-foods", "526M+", "Estimated reach"),
    ("tamrose", "105", "Media mentions"),
    ("gitex-nigeria", "21.87M", "Impressions"),
    ("agusto", "45.8M+", "Estimated reach"),
]

METHOD = [
    ("listen", "Listen", "We start by understanding your organisation, your stakeholders and the environment you operate in, before we recommend anything."),
    ("speak-up", "Speak up", "Clear, candid advice on what to say, to whom and when, even when it isn't the easy answer."),
    ("amplify", "Amplify", "We deliver across media, digital, events and government channels, so the message lands where it counts."),
]

# ── Case studies ────────────────────────────────────────────────────────────
# Copy drawn from the client-supplied case study document. Metrics are as
# supplied; the document's internal evidence checklist is deliberately excluded.
CASES = [
    {
        "slug": "gitex-nigeria",
        "client": "GITEX Nigeria",
        "discipline": "Digital Communications",
        "sector": "Technology",
        "title": "Driving digital engagement for a multi-city technology platform",
        "summary": "A two-month, two-city digital campaign that sustained visibility across five programmes and carried the conversation beyond the event floor.",
        "image": "assets/img/case-gitex.jpg",
        "alt": "A technology conference audience watching a keynote presentation",
        "metrics": [("4.34M", "Reach"), ("21.87M", "Impressions"), ("790.6K", "Clicks"), ("3.62%", "Click-through rate")],
        "challenge": "Following its inaugural edition in 2025, GITEX Nigeria expanded in 2026 across Abuja and Lagos, bringing together government leaders, technology companies, investors, start-ups and innovators across multiple programmes. The communications challenge was to sustain visibility across a two-month pre-event period, make each programme relevant to its audience, drive registrations and ticket sales, and maintain momentum throughout the live event.",
        "approach": [
            "SKOT led an integrated digital campaign across Instagram, Facebook and LinkedIn, supported by paid media on Meta, LinkedIn and Google. The campaign combined programme and speaker storytelling, promotional and sponsor content, targeted advertising and high-volume content production.",
            "During the event, dedicated production teams captured key conversations, speakers, sponsor moments and attendee experiences across the Government Leadership &amp; AI Summit, GITEX Tech Expo, Startup Festival, Future Economy Conference and FDX by GITEX.",
            "Paid campaigns were monitored and optimised throughout to reach relevant audiences and support registrations and ticket sales.",
        ],
        "impact": "The campaign extended GITEX Nigeria's visibility beyond the physical event, connecting online audiences to the different programmes and experiences. Digital coverage brought policy and technology conversations from the Government Leadership &amp; AI Summit to wider audiences, spotlighted exhibitors and start-ups at the GITEX Tech Expo and Startup Festival, and extended discussions around technology, investment and the future economy beyond the event floor.",
        "contribution": "SKOT connected a multi-city technology programme to wider digital audiences through sustained content, targeted amplification and live event storytelling.",
    },
    {
        "slug": "tamrose",
        "client": "Tamrose Limited",
        "discipline": "Corporate Reputation",
        "sector": "Energy",
        "title": "Turning an indigenous growth milestone into an industry story",
        "summary": "A fleet expansion and a fully repaid USD 10 million facility, reframed from corporate announcement into a proof point for Nigerian local content.",
        "image": "assets/img/case-tamrose.jpg",
        "alt": "Marine support vessels at an offshore logistics terminal",
        "metrics": [("105", "Media mentions")],
        "challenge": "Between 2019 and 2025, Tamrose Limited expanded its marine logistics fleet from four vessels to fifteen and fully repaid a USD 10 million Nigerian Content Intervention Fund facility obtained through NCDMB. The communications opportunity was to move this achievement beyond a corporate announcement and show what it represented for indigenous capacity, governance and local content development in Nigeria's offshore oil and gas sector.",
        "approach": [
            "SKOT developed a strategic event and media campaign that positioned the repayment milestone as an industry proof point, rather than simply a corporate celebration.",
            "The campaign brought regulators, government stakeholders, investors, partners and media together around the achievement. Narrative development, executive positioning and spokesperson preparation connected Tamrose's growth to governance, accountability and the potential impact of local content funding.",
            "National media outreach, broadcast engagement, front-page placements, documentary storytelling and visual content extended the story beyond the event and into wider industry coverage.",
        ],
        "impact": "Coverage across national print, online and broadcast platforms increased visibility for Tamrose's milestone. Front-page placements across major business and national newspapers strengthened the profile of the story, while the campaign contributed to wider media discussion about local content effectiveness, indigenous participation and long-term value-chain development.",
        "contribution": "SKOT turned a corporate repayment milestone into a broader story about indigenous capability, governance and local content in Nigeria's offshore sector.",
    },
    {
        "slug": "aliwa",
        "client": "Africa Leadership Initiative West Africa",
        "panel_name": "Africa Leadership Initiative",
        "discipline": "Public Affairs",
        "sector": "Leadership Communications",
        "title": "Establishing a new voice in Nigeria's leadership conversation",
        "summary": "Launching the inaugural Nigeria Leadership Dialogue from a standing start — no established press relationships, a crowded conference landscape.",
        "image": "assets/img/case-aliwa.jpg",
        "alt": "Senior delegates in discussion at a leadership convening",
        "metrics": [("29", "Press mentions"), ("1M+", "Estimated reach")],
        "challenge": "As Africa Leadership Initiative West Africa (ALIWA) prepared to launch the inaugural Nigeria Leadership Dialogue, it needed to establish credibility, build media visibility and introduce the Dialogue as a serious platform for governance and institutional discourse. Despite its affiliation with the Aspen Global Leadership Network, ALIWA had limited existing media visibility and few established press relationships. The task was to differentiate the Dialogue in a crowded conference landscape and reach the stakeholders who shape national leadership conversations.",
        "approach": [
            "SKOT developed an integrated communications and stakeholder engagement strategy to introduce ALIWA to Nigeria's governance, policy and corporate media ecosystem.",
            "The Dialogue was positioned as a cross-sector leadership intervention focused on governance, systems thinking and institutional integrity, rather than a conventional advocacy event. Structured press engagement and journalist introductions helped establish foundational media relationships.",
            "Stakeholder experience, event curation and visual identity were designed to reflect the seniority of the audience, while executive profiling, post-event editorial content and media amplification extended the conversations beyond the convening.",
        ],
        "impact": "The inaugural Nigeria Leadership Dialogue secured coverage across Tier 1, Tier 2 and Tier 3 digital and traditional media platforms. The campaign also established new relationships with journalists and editors and convened public- and private-sector leaders around values-based leadership, institutional accountability and governance reform.",
        "contribution": "SKOT helped ALIWA introduce the Nigeria Leadership Dialogue as a credible platform for cross-sector leadership and governance conversations.",
    },
    {
        "slug": "e1-lagos",
        "client": "E1 Series — Lagos Grand Prix",
        "panel_name": "E1 Series",
        "discipline": "Experiential Communications",
        "sector": "Sport & Entertainment",
        "title": "Bringing E1's global brand experience to the Lagos waterfront",
        "summary": "The Oriental Hotel waterfront transformed into a flagship hospitality destination for the inaugural African edition of the E1 Grand Prix.",
        "image": "assets/img/case-e1.jpg",
        "alt": "An evening waterfront hospitality setting on the Lagos lagoon",
        "metrics": [],
        "qualitative": "Qualitative mandate — no quantified performance figures were provided in the source material.",
        "challenge": "When Lagos hosted the inaugural African edition of the E1 Grand Prix, the Oriental Hotel served as one of the race's flagship hospitality destinations. The environment needed to reflect the energy and prestige of the global E1 property while creating a distinctive waterfront experience for guests, government representatives and international stakeholders. The task extended beyond venue branding: the physical setting and guest journey had to work as one coherent brand experience.",
        "approach": [
            "SKOT developed and executed a premium experiential environment that transformed the Oriental Hotel waterfront into a hospitality and brand destination for the E1 Lagos GP weekend.",
            "Large-format waterfront branding, viewing deck installations, hospitality lounges and environmental graphics brought E1's visual identity into the space. Guest arrival, seating, movement and hospitality touchpoints were coordinated to support a seamless experience.",
            "Hospitality operations, curated guest gifting and vendor coordination were integrated into the activation, with physical elements aligned to E1's international visual identity standards.",
        ],
        "impact": "The Oriental Hotel activation hosted senior government officials, international stakeholders, media representatives and VIP guests during race weekend. The venue provided an immersive waterfront setting aligned with E1's global brand identity, bringing spatial design, guest experience and hospitality coordination together within the wider Lagos Grand Prix programme.",
        "contribution": "SKOT translated E1's international brand identity into a premium Lagos waterfront hospitality environment.",
    },
    {
        "slug": "arla-foods",
        "client": "Arla Foods Nigeria",
        "discipline": "Corporate Communications",
        "sector": "Agriculture",
        "title": "Turning local dairy investment into a national conversation",
        "summary": "A decade of operations, a new yoghurt factory and a Dairy Centre of Excellence, connected to national questions of food security.",
        "image": "assets/img/case-arla.jpg",
        "alt": "Dairy cattle at a managed farm in northern Nigeria",
        "metrics": [("526M+", "Estimated reach"), ("51", "Media mentions"), ("20", "Tier 1 placements"), ("100%", "Positive sentiment")],
        "challenge": "As Arla Foods Nigeria marked a decade of operations in the country, the company needed to demonstrate its contribution to Nigeria's dairy sector beyond an anniversary message. The 2025 Damau Open Day centred on the commissioning of a Cool Cow Yoghurt factory producing yoghurt entirely from fresh local milk and the launch of a Dairy Centre of Excellence focused on technical training and skills development. The communications challenge was to connect these developments to wider priorities around local production, food security and the future of dairy in Nigeria.",
        "approach": [
            "Building on the first Arla-Damau Open Day in 2024, SKOT developed a three-phase communications campaign to build visibility before the event, maintain narrative focus during execution and sustain coverage afterwards.",
            "The campaign framed the Open Day as evidence of investment in local production and dairy ecosystem development. Targeted media outreach engaged agricultural, business and mainstream media across print, digital and broadcast.",
            "Government participation, executive visibility and partnership storytelling connected the company's developments to national conversations around food security and agricultural development. Post-event syndication, broadcast pickups and executive-led thought leadership extended the story beyond the event.",
        ],
        "impact": "Coverage across Punch, Vanguard, ThisDay, BusinessDay, TheCable, Nairametrics, Arise News, NTA and Daily Trust extended the campaign's visibility across national media. Government participation and coverage of the factory and training-centre developments brought Arla's local investment story into wider conversations about dairy production, agricultural development and food security.",
        "contribution": "SKOT connected Arla's investment in local dairy production to a wider national conversation about the sector's future.",
    },
    {
        "slug": "agusto",
        "client": "Agusto & Co.",
        "discipline": "Financial Communications",
        "sector": "Financial Services",
        "title": "Making banking recapitalisation matter beyond the financial sector",
        "summary": "A technical banking transition reframed as a public economic question, with sustained thought leadership behind it.",
        "image": "assets/img/case-agusto.jpg",
        "alt": "A financial analyst reviewing market data on screen",
        "metrics": [("45.8M+", "Estimated reach"), ("40", "Media mentions"), ("6", "Thought leadership assets")],
        "challenge": "As Nigeria's banking recapitalisation exercise approached a defining milestone, Agusto &amp; Co. had an opportunity to help businesses, investors and wider audiences understand what the changes could mean for the economy. Financial coverage was often technical and fragmented. The communications challenge was to make the subject more accessible while strengthening Agusto &amp; Co.'s visibility as a source of financial analysis and economic research.",
        "approach": [
            "SKOT developed an integrated communications strategy that connected event visibility with sustained thought leadership and positioned Agusto &amp; Co. within the national recapitalisation conversation.",
            "A question-led narrative gave the campaign a clear public-facing frame: what does Nigeria's bank recapitalisation mean for the economy? Targeted engagement brought regulators, investors, financial institutions and media stakeholders into the conversation.",
            "Media relations, live event communications and executive visibility were aligned under one narrative. Interviews, articles and editorial content extended the discussion beyond the event.",
        ],
        "impact": "The campaign extended Agusto &amp; Co.'s visibility across financial, business and mainstream media audiences. The event convened regulators, financial institutions, investors and media stakeholders around one of Nigeria's defining economic transitions, while the six thought leadership assets provided additional material for the recapitalisation discussion.",
        "contribution": "SKOT helped Agusto &amp; Co. turn a technical banking development into a more accessible and visible economic conversation.",
    },
]

DISCIPLINES = ["All", "Corporate Communications", "Corporate Reputation", "Public Affairs",
               "Digital Communications", "Financial Communications", "Experiential Communications"]

# ── Programmes ──────────────────────────────────────────────────────────────
PROGRAMMES = [
    {
        "slug": "impact-academy",
        "name": "SKOT Impact Academy",
        "badge": "Tuition-free six-week course",
        "lede": "A tuition-free six-week course for emerging African communications talent.",
        "body": "SKOT Impact Academy is SKOT Communications’ social impact learning platform for early-career public relations and communications professionals. The flagship tuition-free six-week course supports professionals with one to two years of experience through real-world training, local and international facilitator perspectives, in-depth case studies, network-building and a strong understanding of both local and global communications contexts.",
        "image": "assets/img/academy/full-room.jpg",
        "alt": "A full cohort of early-career communications professionals in the SKOT Impact Academy classroom",
        "cta": "Apply for the next cohort",
        "facts": [("6", "weeks"), ("Tuition-free", "no cost to participants"), ("1–2 yrs", "experience level")],
    },
    {
        "slug": "elevate",
        "name": "SKOT Elevate",
        "badge": "Training for professionals and teams",
        "lede": "Executive capability building for professionals, entrepreneurs and teams.",
        "body": "SKOT Elevate is the dedicated training arm of SKOT Communications, created to equip professionals, entrepreneurs and teams across Nigeria with the practical skills and strategic insight required to advance their careers, strengthen organisations and achieve measurable business outcomes. Organisations can access tailored workshops, virtual sessions, hybrid programmes, executive coaching, organisational training and retainer-based capacity development.",
        "image": "assets/img/prog-elevate.jpg",
        "alt": "Professionals in a working session around a conference table",
        "cta": "Explore SKOT Elevate",
        "facts": [("Workshops", "tailored workshops and organisational training"), ("Hybrid", "virtual sessions and hybrid programmes"), ("Coaching", "executive coaching and retainer-based capacity development")],
    },
]

# Impact Academy curriculum: nine (title, optional one-line description) pairs, in order.
# Leave empty to hide the modules section.
ACADEMY_MODULES = [  # DEMO PLACEHOLDERS: replace with the real curriculum
    ("Foundations of strategic communication", "How communication supports organisational goals, and where PR fits."),
    ("Understanding audiences and stakeholders", "Mapping who matters, what they need and how they listen."),
    ("Messaging and storytelling", "Turning a position into clear, credible and memorable messages."),
    ("Media relations in practice", "Pitching, building journalist relationships and handling interviews."),
    ("Digital and social communications", "Building presence, content and community across platforms."),
    ("Writing for impact", "Press releases, statements, speeches and briefs that get read."),
    ("Crisis and reputation management", "Preparing for, responding to and recovering from a crisis."),
    ("Measurement and evaluation", "Setting objectives and showing what communications delivers."),
    ("Career building and professional networks", "Positioning yourself, finding mentors and growing in the industry."),
]

MASTERCLASS = {
    "name": "Masterclass",
    "body": "Masterclass sits under SKOT Elevate as a focused learning experience for junior, mid-level and senior communications professionals who want to refine their strategic communication capabilities and master modern public relations practice. Delivered as a quarterly deep dive, it explores contemporary PR, advanced media relations, digital PR, content creation, leadership communication and strategic influence.",
    "topics": ["Contemporary PR practice", "Advanced media relations", "Digital PR", "Content creation",
               "Leadership communication", "Strategic influence"],
}

# ── About ───────────────────────────────────────────────────────────────────
ABOUT = {
    "intro": [
        "SKOT Communications is a strategic communications and reputation management consultancy with a strong Sub-Saharan Africa focus. We work with organisations, brands and leaders to shape how they are understood, build meaningful connections with their stakeholders, and navigate the issues that matter most to their reputation and success.",
        "Our work sits at the intersection of strategy, communications and reputation. We bring together insight, creativity and specialist expertise to define compelling narratives, strengthen positioning, manage complexity and create communications that deliver measurable impact.",
        "From shaping corporate and brand narratives to navigating public affairs, building digital influence and managing reputation through moments of change and uncertainty, we provide strategic counsel and communications solutions aligned with our clients' ambitions.",
    ],
    "vision": "To transform the communication landscape by empowering authentic voices to challenge stereotypes, spark innovation and drive sustainable growth.",
    "mission": "To connect brands, organisations and individuals with authentic voices that inspire change and deliver impactful stories.",
    "stats": [("6", "sectors represented in recent work"), ("105", "media mentions on a single mandate"), ("526M+", "estimated reach on a single campaign")],
}
