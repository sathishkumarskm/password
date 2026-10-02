const passwordInput = document.getElementById('passwordInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const generateBtn = document.getElementById('generateBtn');
const lengthInput = document.getElementById('lengthInput');
const strengthLabel = document.getElementById('strengthLabel');
const strengthBar = document.getElementById('strengthBar');
const scoreText = document.getElementById('scoreText');
const feedbackText = document.getElementById('feedbackText');

const checks = {
  len: document.getElementById('lenCheck'),
  lower: document.getElementById('lowerCheck'),
  upper: document.getElementById('upperCheck'),
  num: document.getElementById('numCheck'),
  sym: document.getElementById('symCheck'),
};

function setCheckState(element, isValid) {
  element.classList.toggle('pass', isValid);
  element.classList.toggle('fail', !isValid);
  element.textContent = element.textContent.replace(/^(✓\s|✗\s)?/, isValid ? '✓ ' : '✗ ');
}

function updateChecklist(data) {
  const { checks: criteria = {} } = data;
  setCheckState(checks.len, criteria.length);
  setCheckState(checks.lower, criteria.lowercase);
  setCheckState(checks.upper, criteria.uppercase);
  setCheckState(checks.num, criteria.number);
  setCheckState(checks.sym, criteria.symbol);
}

function updateStrengthUI(data) {
  const { score = 0, label = 'Weak', feedback = [] } = data;

  strengthLabel.textContent = label;
  strengthBar.style.width = `${score}%`;
  scoreText.textContent = `${score}/100`;

  if (label === 'Strong') {
    strengthLabel.style.color = '#22c55e';
  } else if (label === 'Moderate') {
    strengthLabel.style.color = '#f59e0b';
  } else {
    strengthLabel.style.color = '#ef4444';
  }

  feedbackText.textContent = feedback.join(' ');
}

async function analyzePassword() {
  const password = passwordInput.value;

  if (!password) {
    updateStrengthUI({ score: 0, label: 'Weak', feedback: ['Enter a password to check its strength.'] });
    Object.values(checks).forEach((item) => setCheckState(item, false));
    return;
  }

  const response = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });

  const data = await response.json();
  updateChecklist(data);
  updateStrengthUI(data);
}

async function generatePassword() {
  const length = Number(lengthInput.value) || 14;
  const response = await fetch(`/api/generate?length=${length}`);
  const data = await response.json();
  passwordInput.value = data.password;
  analyzePassword();
}

analyzeBtn.addEventListener('click', analyzePassword);
passwordInput.addEventListener('input', analyzePassword);
generateBtn.addEventListener('click', generatePassword);

lengthInput.addEventListener('change', () => {
  if (Number(lengthInput.value) < 8) lengthInput.value = 8;
  if (Number(lengthInput.value) > 32) lengthInput.value = 32;
});

Object.values(checks).forEach((item) => setCheckState(item, false));
strengthLabel.textContent = '-';
