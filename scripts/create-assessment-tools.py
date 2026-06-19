#!/usr/bin/env python3
"""Create Interactive Assessment Tools

These are interactive scoring tools that calculate readiness scores
and provide recommendations based on user responses.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "lead-magnets"

ASSESSMENTS = {
    "sharepoint-copilot-ready": {
        "title": "SharePoint Copilot Readiness Assessment",
        "filename": "assessment-copilot-readiness.html",
        "html": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SharePoint Copilot Readiness Assessment</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: Segoe UI, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
    .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
    .header { background: linear-gradient(135deg, #0077b6 0%, #0096d6 100%); color: white; padding: 30px; text-align: center; }
    .header h1 { font-size: 24px; margin-bottom: 8px; }
    .header p { opacity: 0.9; }
    .content { padding: 30px; }
    .question { margin-bottom: 24px; }
    .question-text { font-weight: 600; color: #333; margin-bottom: 12px; font-size: 15px; }
    .options { display: flex; flex-direction: column; gap: 8px; }
    .option { display: flex; align-items: center; }
    .option input { margin-right: 10px; width: 18px; height: 18px; cursor: pointer; }
    .option label { cursor: pointer; flex: 1; }
    .button-group { display: flex; gap: 12px; margin-top: 30px; }
    button { padding: 12px 24px; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; }
    .btn-primary { background: #0077b6; color: white; flex: 1; }
    .btn-primary:hover { background: #0059a6; }
    .btn-reset { background: #e0e0e0; color: #333; }
    .btn-reset:hover { background: #d0d0d0; }
    #results { display: none; text-align: center; padding: 30px; background: #f5f5f5; }
    #results.show { display: block; }
    .score { font-size: 48px; font-weight: bold; color: #0077b6; margin: 20px 0; }
    .score-label { font-size: 14px; color: #666; margin-bottom: 20px; }
    .recommendation { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: left; border-left: 4px solid #0077b6; }
    .recommendation h3 { color: #0077b6; margin-bottom: 10px; }
    .recommendation p { color: #666; line-height: 1.6; }
    .footer { text-align: center; padding: 20px 30px; border-top: 1px solid #eee; font-size: 12px; color: #999; }
    .footer a { color: #0077b6; text-decoration: none; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🚀 SharePoint Copilot Readiness Assessment</h1>
      <p>5 questions • ~2 minutes • Free</p>
    </div>

    <div class="content" id="quiz">
      <div class="question">
        <div class="question-text">1. What is your organization's current SharePoint maturity level?</div>
        <div class="options">
          <div class="option"><input type="radio" name="q1" value="1"> Just started with SharePoint (legacy/on-prem)</div>
          <div class="option"><input type="radio" name="q1" value="2"> Modern SharePoint but limited governance</div>
          <div class="option"><input type="radio" name="q1" value="3"> Well-structured with clear governance</div>
          <div class="option"><input type="radio" name="q1" value="4"> Enterprise-grade with advanced features</div>
        </div>
      </div>

      <div class="question">
        <div class="question-text">2. How much Microsoft 365 training have your users received?</div>
        <div class="options">
          <div class="option"><input type="radio" name="q2" value="1"> Minimal/none</div>
          <div class="option"><input type="radio" name="q2" value="2"> Basic training (quick onboarding)</div>
          <div class="option"><input type="radio" name="q2" value="3"> Regular training (quarterly updates)</div>
          <div class="option"><input type="radio" name="q2" value="4"> Comprehensive program (ongoing upskilling)</div>
        </div>
      </div>

      <div class="question">
        <div class="question-text">3. What is your organization's data governance posture?</div>
        <div class="options">
          <div class="option"><input type="radio" name="q3" value="1"> No formal data governance</div>
          <div class="option"><input type="radio" name="q3" value="2"> Basic naming conventions and retention</div>
          <div class="option"><input type="radio" name="q3" value="3"> Formal policies with some enforcement</div>
          <div class="option"><input type="radio" name="q3" value="4"> Rigorous governance with full compliance</div>
        </div>
      </div>

      <div class="question">
        <div class="question-text">4. Do you have a dedicated M365 governance team?</div>
        <div class="options">
          <div class="option"><input type="radio" name="q4" value="1"> No dedicated team (ad-hoc)</div>
          <div class="option"><input type="radio" name="q4" value="2"> Part-time (1 person)</div>
          <div class="option"><input type="radio" name="q4" value="3"> Full-time (2-3 people)</div>
          <div class="option"><input type="radio" name="q4" value="4"> Dedicated team (3+ people)</div>
        </div>
      </div>

      <div class="question">
        <div class="question-text">5. How comfortable are you adopting AI/automation for workflows?</div>
        <div class="options">
          <div class="option"><input type="radio" name="q5" value="1"> Cautious (skeptical of AI tools)</div>
          <div class="option"><input type="radio" name="q5" value="2"> Open (willing to pilot)</div>
          <div class="option"><input type="radio" name="q5" value="3"> Active (already using Power Platform)</div>
          <div class="option"><input type="radio" name="q5" value="4"> Advanced (extensive automation)</div>
        </div>
      </div>

      <div class="button-group">
        <button class="btn-primary" onclick="calculateScore()">See Your Readiness Score</button>
        <button class="btn-reset" onclick="resetQuiz()">Reset</button>
      </div>
    </div>

    <div id="results">
      <h2>Your Copilot Readiness Score</h2>
      <div class="score-label">You can adopt SharePoint Copilot effectively in</div>
      <div class="score" id="scoreValue">0</div>

      <div id="scoreMessage"></div>

      <div class="recommendation">
        <h3>Next Steps</h3>
        <p id="nextSteps">Complete the assessment to see recommendations.</p>
      </div>

      <button class="btn-primary" onclick="resetQuiz()" style="width: 100%; margin-top: 20px;">Take Assessment Again</button>
    </div>

    <div class="footer">
      <p>This assessment is part of "SharePoint Copilot Readiness Guide" by OceanCloud</p>
      <p><a href="https://oceancloudconsults.com/contact">Book a consultation</a> to discuss your Copilot roadmap</p>
    </div>
  </div>

  <script>
    function calculateScore() {
      const q1 = document.querySelector('input[name="q1"]:checked');
      const q2 = document.querySelector('input[name="q2"]:checked');
      const q3 = document.querySelector('input[name="q3"]:checked');
      const q4 = document.querySelector('input[name="q4"]:checked');
      const q5 = document.querySelector('input[name="q5"]:checked');

      if (!q1 || !q2 || !q3 || !q4 || !q5) {
        alert('Please answer all questions');
        return;
      }

      const total = parseInt(q1.value) + parseInt(q2.value) + parseInt(q3.value) + parseInt(q4.value) + parseInt(q5.value);
      const percentage = Math.round((total / 20) * 100);
      let timeline, message, nextSteps;

      if (percentage < 40) {
        timeline = '9-12 months';
        message = '<strong>Foundation Phase Required</strong><p>Your organization needs foundational work in governance and user training before Copilot adoption.</p>';
        nextSteps = '<strong>1. Establish data governance</strong> - Clear naming, retention, and access policies<br><strong>2. User training program</strong> - Build M365 confidence across the org<br><strong>3. Pilot approach</strong> - Start with small group, test Copilot features<br><strong>4. Expert guidance</strong> - Work with OceanCloud on readiness roadmap';
      } else if (percentage < 70) {
        timeline = '4-6 months';
        message = '<strong>Some Preparation Needed</strong><p>You have a good foundation but need targeted improvements before full Copilot rollout.</p>';
        nextSteps = '<strong>1. Strengthen governance</strong> - Formalize policies, implement retention<br><strong>2. Expand training</strong> - Ongoing M365 upskilling<br><strong>3. Plan pilot</strong> - 50-100 power users, measure adoption<br><strong>4. Optimize infrastructure</strong> - Ensure search works well for Copilot';
      } else {
        timeline = '2-3 months';
        message = '<strong>Ready for Deployment</strong><p>Your organization is well-positioned for SharePoint Copilot adoption.</p>';
        nextSteps = '<strong>1. Change management</strong> - Communicate Copilot benefits to users<br><strong>2. Pilot deployment</strong> - Roll out to early adopters<br><strong>3. Monitor & optimize</strong> - Track usage, gather feedback, iterate<br><strong>4. Scale gradually</strong> - Expand to broader user base';
      }

      document.getElementById('scoreValue').textContent = percentage + '%';
      document.querySelector('.score-label').innerHTML = `You can adopt SharePoint Copilot effectively in<br><strong>${timeline}</strong>`;
      document.getElementById('scoreMessage').innerHTML = message;
      document.getElementById('nextSteps').innerHTML = nextSteps;

      document.getElementById('quiz').style.display = 'none';
      document.getElementById('results').classList.add('show');
    }

    function resetQuiz() {
      document.querySelectorAll('input[type="radio"]').forEach(r => r.checked = false);
      document.getElementById('quiz').style.display = 'block';
      document.getElementById('results').classList.remove('show');
    }
  </script>
</body>
</html>
''',
    },
}

def create_assessments():
    """Create all assessment tool HTML files."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("CREATING INTERACTIVE ASSESSMENT TOOLS")
    print("=" * 70)
    
    created = 0
    for assess_id, assess_data in ASSESSMENTS.items():
        filepath = ASSETS / assess_data["filename"]
        filepath.write_text(assess_data["html"], encoding='utf-8')
        print(f"✅ {assess_data['title']}")
        print(f"   Saved to: {filepath}")
        created += 1
    
    print("\n" + "=" * 70)
    print(f"Created {created} interactive assessment tools")
    print("=" * 70)

if __name__ == "__main__":
    create_assessments()
