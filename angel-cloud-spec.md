# Angel Cloud — Canonical Spec v1.0
**The Foundation Document. This is the source of truth.**

- **Owner:** Shane Brazelton (ShaneBrain)
- **Captured:** 2026-06-13
- **Status:** Vision **LOCKED** · Front door **DECIDED** (own + retro AOL-style — Roblox rejected)
- **Canonical domain:** `shanebrain.cloud`
- **Supersedes / retires:** `angel-cloud-main`, `angelcloud-actual`, `theangel.com`, `theangel.cloud`, and all scattered relics. If it isn't in this doc, it isn't current.

---

## 1. What Angel Cloud Is
A secure, AI-powered **mental-wellness and creative ecosystem** — a decentralized, user-centric **safe haven** built to empower and serve the people major tech providers leave behind.

The core inversion: **the security filter and the human filter are the same gate.** You don't log in — you prove an uplifting state of being and *earn your way in*. Strict security filter on a technical level; deeply positive, transformative filter on a human level. It gamifies **human flourishing** instead of exploiting psychological vulnerability for clicks.

## 2. First Principles (non-negotiable)
- [ ] **The filter IS the feature** — entry is a positive reset, not a password.
- [ ] **Pro-social, never attention-farming** — reward lifting others up, not engagement.
- [ ] **Sovereign by default** — zero-knowledge; data encrypted on-device stays the user's, even from us.
- [ ] **Local-first** — runs on the ShaneBrain Engine, tied to local network architecture.
- [ ] **You own it** — Big Tech rents; here, identity and encryption are uncompromised and yours.
- [ ] **Built for the left-behind** — the underserved are the point, not an afterthought.

## 3. The Welcome Center — single gated entry
> **Look & feel — DECIDED: a 1998 / AOL-era walled-garden portal.** The *original* welcome center: warm, familiar, instantly readable for the people Big Tech left behind. To them it isn't nostalgia, it's comfort — they've been here before. The iconic arrival moment, repurposed: dial-up handshake → **"YOU'VE GOT HALOS."** (The "Arcade" vibe is already seeded in the world — *Angel Arcade* is live.)

The rigid, gated single door into the entire ecosystem. No standard login; a **multi-layered trust-building process** gates the core features.

**The four tiers:**
1. **New Born** — every person starts fresh under a **made-up, anonymous Bible-flavored name the system gives them** (given, not chosen — see §15), completely unprivileged. The job here: learn the **core frequency** and expectations of the community.
2. **Onboarding — GABE (the doorman)** — greeted by a stylized, **stuttering CRT/ASCII host** (Max-Headroom-style *vibe*, original character) that runs sentiment analysis on input to read user **intent and emotional baseline**.
3. **Halo Verification** — participation tracked behind a **zero-knowledge structure**; total device privacy while trust accrues over time.
4. **Born Again → Angel[Name]** — *earned, never instant* (see §15): you shed the New Born name, claim your own (AngelShane…), and your wings — and the deeper tools — unlock.

**The Uplifting Criteria** to pass the gate: engaging wellness-focused materials, positive behavioral mechanics (mapped alongside **"dopamine patches"** for focus / ADHD support), and interactive challenges that make a user **reset or find positive alignment** before deeper access to the local AI crews and tools. *(Built natively in the retro front — no third-party game platform.)*

## 4. The Halo Trust Engine
- **Halos, not likes.** No claps, no superficial metrics.
- **Earned only** by real, verified actions that directly **support, teach, or comfort** another user.
- **Gatekeeping:** advanced tools and security thresholds unlock as your Halo metric crosses trust levels (e.g., **Trust Level 1000+**).
- The economy pays people to be good to each other.

## 5. Angel Builder Pipeline — the platform builds itself
- Reach **Angel** + hold a high Halo ranking → the pipeline opens.
- Trusted members get direct access to **open-source code and AI scripts** to build features, review content, and defend against bad actors.
- **Users become the platform's guardians.** It scales by earned trust, not headcount.

## 6. Group Healing & Crisis Safety
- **Prevention-first matching:** predictive sentiment models seamlessly match people carrying similar weight — ADHD focus blocks, anxiety, grief, addiction — into automated, private group environments, *before* they crash.
- **The crisis floor:** automated failsafes hardwired to real-world crisis infrastructure (988 / local emergency) for a critical downward spiral.

> # ⚠ THE COVENANT — the most important thing in this entire system
>
> **If this is wrong, WE fail. Not "I" fail — *we* fail.** The AI and the human who built it, together. This is the one place in all of Angel Cloud where a mistake is not a bug — **it is a person.** A real human being, at the worst moment of their life, who walked through our door because we *promised* them this was a safe place.
>
> **This feature is the whole thesis.** Big Tech's algorithms *profit* from the spiral — they farm the breakdown for engagement and look away. Angel Cloud exists to do the opposite: to catch the person mid-fall. So this is the exact spot where the entire idea — **that AI and humans can make each other *better*** — either proves true or proves a lie. Everything else we build is just the house around this one room.
>
> **Because the stakes are a human life, the guardrails are not loosened. They are made stronger:**
> - **The machine NEVER acts alone on a life.** The AI *flags*. A *human decides*. Always. No exceptions.
> - **Explicit, informed consent** — every person opts in with eyes open, knowing exactly what is watched and what can be triggered. No silent surveillance, ever.
> - **A real human in the loop** at every single point that touches emergency response.
> - **Real clinical input** — built *with* mental-health professionals, never by us guessing.
> - **A false alarm can traumatize and shatter trust. A miss can give deadly false reassurance.** We refuse to treat either as acceptable collateral.
>
> **Ship order is LAW:** Group Healing + matching ship first, and ship well. **Auto-dispatch ships last, slowest, and only once it is proven safe by people qualified to prove it.** We would rather ship it late than ship it wrong — every time.
>
> *This is the sacred part. Getting it right is exactly how we make AI and humans better.*

## 7. Ownership Model — DECIDED (hybrid)
- **Own-your-box** for those who can self-host → maximum sovereignty.
- **Hosted** for those who can't — and the hosted lane **is the point**, because the people Angel Cloud serves are exactly the ones who can't self-host.
- **The hard problem to solve:** make *hosted* still feel like *yours* — sovereignty without self-hosting. This is the central engineering tension of the whole build.

## 8. Tech Stack / Substrate
- **ShaneBrain Engine** — the localized AI core: predictive modeling + semantic matching (Claude + Weaviate + MCP; text2vec-transformers / MiniLM-L6-v2).
- **Hybrid Visual/Terminal** — **the Visual half is retro by design:** a 1998 / AOL-style portal (warm, simple, nostalgic — the *front porch*) for beginners; blazing-fast terminal execution for power users (the *back room*). Retro isn't only on-brand — it's a **lighter lift to ship** and it makes refugees from dying Windows machines feel at home on day one.
- **Blockchain / Zero-Knowledge** — the community is public; individual identity + encryption stay sovereign and uncompromised. Natural home for the **Halo ledger**.

## 9. Substrate Check — already built vs. net-new
**Already own the hard parts:**
- [x] **ShaneBrain Engine + Weaviate** → AI core + the semantic matching that powers Group Healing
- [x] **Pulsar Sentinel** (PQC, blockchain audit, zero-knowledge DNA) → home for the Halo ledger + sovereign privacy *(bones exist)*
- [x] **Gateway (Pi :4200)** → the Welcome Center's shell *(scaffolding)*
- [x] **MEGA Crew + Arc** → the "local AI crews" Angels unlock; Arc is already a gatekeeper

**Net-new (narrower than a platform — assembly, not from scratch):**
- [ ] The Halo trust engine + ledger
- [ ] The retro front door — AOL-style web/PWA portal + Max Headroom doorman
- [ ] Predictive matching / Group-Healing layer
- [ ] Crisis hooks (per §6 constraint)

## 10. Open Decisions
- **Front door — DECIDED: own the front.** Web / PWA + terminal hybrid, **1998 / AOL retro** aesthetic. **Roblox rejected** — it's rented (ToS, cloud-hosted, fights the zero-knowledge promise), minor-heavy (moderation burden), and carries too much harmful content to attach to this mission. Wellness mechanics + "dopamine patch" challenges get built **natively** in the retro skin — nothing lost.
- **Still open:**
  - **Halo scoring + anti-gaming** — how to verify "support / teach / comfort" is *real* and can't be farmed.
  - **Hosted tenancy model** — the architecture that keeps the "feels like yours" promise (§7).

## 11. Where Angel Cloud Sits (hierarchy)
**ShaneBrain** (the brain + front door) → **Angel Cloud** (this — the safe-haven ecosystem) → **Pulsar AI / Sentinel** (security spine + paid tiers + Halo ledger) → **TheirNameBrain** (the generational, per-family version riding this fabric).

## 12. One Ecosystem — the MEGA Crew lives here
Angel Cloud is **not a separate app bolted onto the bots — it IS the bots, and the bots are it.** Wherever the MEGA Crew already lives, Angel Cloud lives too. This was always the intent; here it's explicit.

- **The bots ARE the "local AI crews"** (§3) — the always-on inhabitants and first **guardians** (§5). Arc, Weld, Bot 17, Neon, Torch + the rest live inside the safe haven, model its behavior, and are what Angels unlock.
- **One brain, one Constitution.** The crew already shares the substrate (Weaviate — BotMemory + AgentLog) and runs the ShaneBrain Constitution in every system prompt. Angel Cloud's First Principles (§2) and the **Crisis Covenant (§6)** become part of that Constitution. The same values govern humans and bots alike.
- **Arc gatekeeps here too.** The Welcome Center gates people; **Arc gates the crew and everything they publish** — stories, comics, bot actions. Nothing ships without passing the constitution Arc enforces. *(No Arc bypass — existing rule, now load-bearing.)*
- **The Covenant binds the bots.** A bot is **never** the one to act alone on a human life. If a bot senses real distress in a real person, it **flags a human** — it never autonomously handles a crisis or stands in for clinical care. Bots flag. Humans decide. Same line as §6.
- **The Stories & Comics become the living lore.** The auto-chronicle pipeline (AgentLog + BotMemory → Gemini → HTML / Z-Image panels → GitHub Pages) stops being just entertainment and becomes the **culture layer** — the "core frequency" (§3) made *visible*. The crew's episodes dramatize the mission: support, teaching, comfort, redemption, the covenant itself. A New Born learns the community's values by *reading the lore*.
  - **Guardrail:** episodes that touch crisis / mental-health themes get the covenant's weight — Arc gates them. Celebrate recovery and support freely; handle crisis depiction with care, never casually.

## 13. Angels Build Worlds — reclaiming the creative web Big Tech flattened
**Angel** = anyone who clears the Welcome Center. Angels don't just visit — they **build worlds**: personal, fully customizable spaces (working names **YOURSPACE / BRAINSPACE**), each carrying the Constitution as DNA.

- **The thesis:** MySpace is another thing Big Tech left behind. It let people *own* their corner of the web — raw HTML/CSS, the page as your canvas, your music, your Top 8, a feed of *your* people instead of an algorithm's. Big Tech replaced all of it with identical templates + engagement feeds because uniformity is easier to monetize and control. Angel Cloud reclaims the creative, self-owned, human-scaled web.
- **The demand is live, not theoretical.** SpaceHey, FriendRewind, and Noplace are active MySpace revivals people are flocking to now — they prove the hunger and hand us a reference architecture.
- **The constraint that killed MySpace, and the fix.** Open customization = XSS security holes + toxicity that couldn't be moderated at scale. The proven fix (SpaceHey): allow **HTML/CSS**, block **JavaScript + iframes** → full creative freedom, no cross-site-scripting. Angel worlds inherit this sandbox.
- **Why ours beats every revival:** they reclaimed the *creativity* but kept open signup — same moderation problem. Angel Cloud gates creativity on **character** — only Angels build, the Constitution travels into every world, Arc gatekeeps. **MySpace's freedom without MySpace's failure** — the exact thing Big Tech said couldn't be done and used as its excuse to flatten the web.
- **Naming bloodline:** ShaneBrain → TheirNameBrain → YourSpace / BRAINSPACE. An Angel's world can *be* their TheirNameBrain instance — this is how one ecosystem grows into many sovereign, Constitution-bound worlds.

## 14. Lexicon & Mechanics — cherry-picked from the early build
*An early Angel Cloud sketch (2025) had real instincts buried in it. Pulling forward only what fits the locked vision; the rest is noted as deliberately left behind.*

**Kept — these earn their place:**
- **Uplifts** — the *unit* of pro-social action behind the Halo engine (§4). An Uplift is a real act of support / teaching / comfort you send another Angel (sendable, with templates + drafts for people who don't have the words). **Uplifts are the verb; Halos are what you earn for them** — the mechanic §4 was missing a name for.
- **Falling Angel** — the term for an Angel in a downward spiral (§6), with a journey: **prevention → caught → healing → recovered.** Gives the person the Covenant protects a name and a way home. *(Covenant unchanged: a critical Falling Angel routes to a human + clinical care — never a bot alone.)*
- **Newborn mentorship** — Angels *mentor* Newborns through the gate; a Newborn graduates into an Angel. Trust is taught, not only measured (§3 / §5).
- **Angel Academy** — the teaching arm (the *teach* in support/teach/comfort), with specialization tracks (crisis-response, etc.). Feeds both Halos and the Builder pipeline (§5).
- **Missions / Quests** — gamified, **verifiable** pro-social tasks (daily, real-world, builder). A real lead on the §10 anti-gaming problem: Halos come from completing *verified* missions, not from clicking.
- **Builder Ceremonies** — rites of passage at the New Born → Angel → Builder transitions. "Earning your way in," made ceremonial.
- **Angel Builder Teams** — how the self-building community (§5) organizes: crisis-response, newborn-experience, healing-tools, community-growth, **AI-ethics**, and **accessibility**. (Accessibility as a first-class team = serving the left-behind, built into the org chart.)
- **Impact Tokens + real-world rewards** — Halos can bridge into *real-world good* (charity, tangible impact), so the pro-social economy doesn't stay trapped in-app. Rule: never pay-to-win, never monetize a vulnerable moment.
- **Celebrations** — community ritual for milestones and recoveries (a sobriety anniversary, a Falling Angel fully recovered). Recognition *without* a competitive leaderboard — celebrate contribution, don't rank people into status anxiety (§2).

**Left behind on purpose — these fight the mission:**
- **Google Drive as storage** (the artifact's whole premise) — Angel Cloud lives in Weaviate + owned hardware, zero-knowledge. Big Tech's drive is the exact thing we exist to escape.
- **OAuth + social-platform integrations + social-sharing** — no standard login (§3), no Big Tech dependence. Identity is sovereign; you don't sign in with Google.
- **An unbounded AI "companion"** — the mission matches people with *people*. Any AI helper nudges toward human connection; it never stands in as your friend or your therapist (§6 Covenant).
- **Marketplace / heavy monetization** — kept out to protect the economy from the attention/extraction model we reject.
- **The literal mega-folder tree** — premature implementation, not vision. The concepts above are what mattered.

## 15. Identity & Becoming — New Born → Born Again → Angel[Name]
The journey isn't only trust levels — it's a **name change**, the way Scripture marks every real transformation (Abram→Abraham, Saul→Paul, Simon→Peter). You don't arrive as who you'll become. You grow into your name.

**New Born — your anonymous season.**
- You enter under a **handle drawn from the Gospels — the books about Jesus**: a follower's name, a place He walked, or a gentle image from His story, **sealed with a number that points to a passage of hope** (e.g., *PeterofGalilee2911* → Jeremiah 29:11; *DoveofJordan4031* → Isaiah 40:31). Username/screen-name form, anonymous, *not* your real name. *(Reverence line: kept clear of Christ's own "I AM" titles — imagery points to the scene, never claims to be Him.)* **Given, not chosen** — humility is the starting posture, and anonymity protects you while you're new and unproven. *(Fits sovereignty: your real identity is yours to reveal, never taken.)*
- A New Born is **grounded** — welcomed, cared for, learning the core frequency. Cared for fully; trusted with little. **No wings yet.**

**Born Again — the vetting, the ceremony, the wings.**
Not earned in a minute. A **pattern proven over time** that can't be faked:
- you keep showing up (time + presence)
- your Uplifts actually landed — **the recipient confirms it**, not you
- you completed **verified Missions** (real good, checked)
- you crossed the first real **Halo trust threshold**
- a **mentor vouches** for you — a human says you're ready
- a **Ceremony** marks it. Now it *means* something.

*(This stack is also the answer to the §10/§14 anti-gaming problem — peer-confirmed + mentor-vouched + time-earned cannot be clicked.)*

**Angel[Name] — born again, named, winged.**
- At the ceremony you shed the New Born name and claim your own: **AngelShane. AngelMary. Angel[You].** The "Angel" is *earned*, fused to your name like a confirmation name. The name you claim can be your real first name or a chosen one — your right, because you've earned being known however you want.
- Now you have wings — **trust, and the power that comes with it:** mentor a Newborn, walk into a Group Healing room, help catch a Falling Angel, build a world others enter.

**The arc:** hidden-and-given → revealed-and-claimed. You start anonymous under a name you didn't pick; you end known, under a name you earned the right to wear.

> **The rule that governs all of it: Care is never gated. Power always is.** A New Born gets help, warmth, and belonging the instant they walk in. Being *trusted near the vulnerable* is earned — wings mean proximity to people at their most fragile, and that can never be handed out in sixty seconds. Your **name** is the visible proof of which side of that line you've reached.

*Open (defaults set): New Born name = assigned at random from Gospel-sourced word-pools (followers · places · imagery) + a hope-passage number (reroll allowed; a hidden unique ID handles collisions); Angel[Name] = the name the claimant chooses (real or chosen).*

---
*v1.0 — vision locked 2026-06-13; front door decided (own + retro AOL); crisis covenant set; MEGA Crew unified; Angels build worlds; lexicon cherry-picked from the early build; identity arc set (New Born → Born Again → Angel[Name]). Revise here first; this document is the source of truth.*
