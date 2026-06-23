---
Document: CTR Monitoring Baseline & 6-Phase Evaluation Framework
Date: 2026-06-23
Purpose: Track impact of new guides and metadata optimization on click-through rate
---

# CTR Monitoring Baseline Capture — 2026-06-23

## Baseline Metrics (All Guides as of June 23, 2026)

**Collection Method:** Google Search Console Export (30-day rolling window)

| Guide ID | Guide Title | Impressions | Clicks | CTR % | Avg Position | Status |
|----------|-------------|-------------|--------|-------|--------------|--------|
| (1-28 existing guides) | [SEE BASELINE SPREADSHEET COLUMN A-E] | [Data exported from GSC] | [Data exported from GSC] | [Calculated] | [Data exported from GSC] | Baseline |

**Sitewide Metrics (Baseline):**
- Total impressions (all guides): 3,463
- Total clicks (all guides): 75
- Sitewide CTR: 2.17%
- Average position (sitewide): 23.3
- Guide count: 27 (as of June 16)

**Position Bucketing (Baseline):**
| Position Bucket | Guides in Bucket | Avg CTR | Expected Lift |
|-----------------|------------------|---------|---------------|
| 1-5 | X guides | ~40% CTR | N/A (already high) |
| 6-10 | X guides | ~15% CTR | +20% expected from metadata optimization |
| 11-20 | X guides | ~5% CTR | +25% expected from metadata optimization |
| 21+ | X guides | ~1% CTR | +10% expected (position is primary barrier) |

---

## 6-Phase Monitoring Plan

### PHASE 0: Setup (June 23, 2026)
**Task:** Capture baseline before new guides gain traffic

1. [ ] Export Google Search Console data:
   - All queries, impressions, clicks, position per URL
   - Save as: `data/gsc-baseline-2026-06-23.csv`

2. [ ] Create monitoring spreadsheet with:
   - Baseline CTR per guide
   - Per-guide position bucket classification
   - Metadata optimization status (all guides should be ✓ by now)

3. [ ] Set up automated GSC export (weekly via Google Sheets add-on or API)

4. [ ] Configure dashboard (Power BI or Google Data Studio):
   - CTR trend line (all guides)
   - Position bucket performance
   - New guides vs. established guides comparison

**Expected Output:** Baseline numbers locked in; tracking infrastructure ready

---

### PHASE 1: Day 0-3 (June 23-26, 2026)
**Objective:** Monitor for any negative impact from changes

**Monitoring Points:**
- [ ] Manual GSC check (daily)
  - Any guides with sudden CTR drop? (possible penalty or bug)
  - Any unusual position changes?
  - New guides indexed? (usually 24-48 hours)

- [ ] Check new guides in Search Console:
  - guide-copilot-cowork-multi-team-workflows
  - guide-scout-adoption-governance
  - guide-work-iq-apis-organization-insights
  - guide-teams-phone-agents-custom-voice
  - guide-computer-using-agents-rpa-automation

**Success Metrics:**
- No CTR drop on existing guides
- New guides appear in GSC (not penalized)
- Metadata optimization hasn't caused issues

**Action Triggers:**
- If CTR drops >10% on any guide → Investigate (check for indexing issue, rank drop, or algorithm update)
- If new guides not indexed → Check robots.txt, canonical tags, sitemap

---

### PHASE 2: Day 7-10 (June 30 - July 3, 2026)
**Objective:** Midpoint check for early signals

**Metrics to Collect:**
- [ ] GSC data for all guides (7-day window from June 23)
- [ ] Position bucket breakdown (which position ranges getting impressions?)
- [ ] CTR by position bucket:
  - Positions 1-5: Total clicks / impressions = CTR
  - Positions 6-10: Total clicks / impressions = CTR ← **Track this closely**
  - Positions 11-20: Total clicks / impressions = CTR ← **Track this closely**
  - Positions 21+: Total clicks / impressions = CTR

**Analysis:**
- Compare position 6-10 bucket CTR to baseline
- Are metadata optimizations helping guides move up from position 21+ to 11-20?
- New guides: Any initial impressions? Check indexing status

**Expected Result:**
- Early signal of metadata optimization impact (probably still too early to detect)
- Baseline data for new guides (showing 0 clicks/few impressions)

---

### PHASE 3: Day 14-21 (July 7-14, 2026)
**Objective:** PRIMARY EVALUATION WINDOW — Measure metadata impact

**Why this window matters:**
- Old guides: 3+ weeks of data allows statistical significance
- New guides: Beginning to rank, acquire initial traffic
- Enough time for ranking shifts to stabilize

**Detailed Analysis:**

**For Optimized Guides (Metadata changed):**
| Guide | Baseline CTR | Current CTR | CTR Change | Position Change | Notes |
|-------|-------------|-----------|-----------|-----------------|-------|
| Guide 1 | [baseline] | [current] | [+/−]% | [baseline → current] | Positive/Negative/Neutral |
| Guide 2 | ... | ... | ... | ... | |

**Position Bucket Breakdown (14-day window):**
- Positions 6-10: Expected +15-20% CTR improvement
- Positions 11-20: Expected +20-25% CTR improvement
- Positions 21+: Limited improvement (position is primary barrier)

**New Guides Analysis (14-day window):**
- guide-copilot-cowork: X impressions, Y clicks, Z% CTR
- guide-scout: X impressions, Y clicks, Z% CTR
- guide-work-iq-apis: X impressions, Y clicks, Z% CTR
- guide-teams-phone: X impressions, Y clicks, Z% CTR
- guide-computer-agents: X impressions, Y clicks, Z% CTR

**Key Questions:**
1. Did sitewide CTR improve? Target: +0.3-0.5% (from 2.17% → 2.5-2.67%)
2. Did guides in position 6-20 bracket see CTR lift? (snippet optimization's primary target)
3. Are new guides ranking fast? (all 5 new guides should have ≥50 impressions)
4. Did any guide lose positions? (potential concern if yes)

**Expected Outcome:**
- **Success:** Sitewide CTR increased 0.2-0.5%; position 6-20 guides show 15-25% CTR improvement
- **Partial success:** Sitewide CTR unchanged; but position 6-20 improved (position > 20 holding back gains)
- **No improvement:** Metadata optimization didn't move needle; position remains primary barrier

---

### PHASE 4: Day 21-35 (July 14-28, 2026)
**Objective:** Stabilization check & strategic decision point

**What's Changed:**
- New guides have 2+ weeks of ranking data
- Metadata optimization effect fully realized (no more "settling in")
- Enough data to measure seasonal/algorithmic variations

**Evaluation:**
- Confirm CTR lift is sustained (not temporary spike)
- New guides CTR trajectory (improving? stabilizing? declining?)
- Any position regressions on old guides?

**Strategic Decision Points:**

**If CTR improved ✓:**
- Continue with current strategy
- Plan Phase 2 optimization (content depth, backlinks, internal linking)
- Expand successful patterns to remaining 23 guides if not yet optimized

**If CTR flat :**
- Position >20 is the primary barrier (not snippet optimization)
- Strategic focus shifts to: backlinks, content authority, E-E-A-T signals
- Metadata optimization was necessary but not sufficient

**If CTR declined ✗:**
- Likely algorithm update or unrelated factor
- Revert metadata changes on 1-2 guides for A/B test
- Investigate for penalties or indexing issues

---

### PHASE 5: Day 30-60 (July 23 - August 22, 2026)
**Objective:** Final evaluation & strategic planning

**30-Day Cumulative Analysis:**

| Metric | Baseline | Day 30 | Change | Status |
|--------|----------|--------|--------|--------|
| Sitewide Impressions | 3,463 | ? | ? | ↑ or ↓ |
| Sitewide Clicks | 75 | ? | ? | ↑ or ↓ |
| Sitewide CTR % | 2.17% | ? | ? | ↑ or ↓ |
| New Guides Impressions | 0 | ? | ? | ~500-1000 expected |
| New Guides Total Clicks | 0 | ? | ? | ~15-30 expected |
| Avg Position Change | 23.3 | ? | ? | ↑ (lower position) or ↓ |

**Sitewide ROI Assessment:**
- Traffic increase: (Current impressions - Baseline) ÷ Baseline impressions = % gain
- CTR improvement: (Current CTR - 2.17%) ÷ 2.17% = % improvement
- Combined impact: (Current clicks - 75) ÷ 75 = % total traffic gain

**New Guides Performance:**
- Which of the 5 new guides is ranking fastest?
- Expected ranking positions for new guides (typically 10-30 by day 30)
- Early engagement signals (impressions, clicks, bounce rate)

---

## Ongoing Monitoring (Post-Day 30)

**Weekly Review (Every Friday):**
- Export GSC data for that week
- Graph CTR trend line
- Check for anomalies (position drops, CTR swings)
- Any guides "falling out" of top positions?

**Monthly Review (First of month):**
- Full GSC export for 30-day rolling window
- Update master spreadsheet
- Compare to previous month
- Generate executive summary

**Quarterly Review (Every 3 months):**
- Comprehensive analysis
- Strategic recommendations
- Plan next phase of optimization

---

## Tool Setup Checklist

- [ ] Google Search Console (GSC) export configured
  - Daily auto-export to Google Sheets or S3
  - Columns: URL, Query, Impressions, Clicks, CTR, Avg Position

- [ ] Google Data Studio or Power BI dashboard
  - CTR trend line (all guides, per-guide, by position bucket)
  - Impressions trend
  - Position distribution over time
  - New guides performance card

- [ ] Spreadsheet setup
  - Master baseline (frozen as reference)
  - Daily/weekly snapshots
  - Formulas for CTR calculation by position bucket
  - Comparison to baseline (% change highlighted)

- [ ] Alert configuration
  - Alert if any guide loses 5+ positions in 1 week
  - Alert if any guide's CTR drops >50% in 1 week
  - Alert if sitewide CTR drops >10% in 1 week

---

## Success Criteria

**Primary Goal:** Measure impact of metadata optimization on CTR for guides ranked 6-25

**Success Threshold (Day 21):**
- Guides in position 6-10: CTR increases 15-20%
- Guides in position 11-20: CTR increases 20-25%
- Sitewide CTR increases 0.2-0.5% (2.17% → 2.37-2.67%)
- New guides acquire 500+ impressions, 10+ clicks by day 21

**Stretch Goal:**
- Sitewide CTR increases 0.5%+ (to 2.67%+)
- 2-3 guides move from position 21+ to position 11-20
- New guides ranking in top 20 for primary keywords by day 21
