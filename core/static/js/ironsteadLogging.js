const presets = [1,2,4,6,8,10,12];
const baseYieldPerHour = 3; // base wood per hour
const skillMultiplier = 0.08; // 8% per skill level
const maxRareChance = 40; // percent
const baseRare = 2; // base percent
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const start_time = document.querySelector('meta[name="start_time"]').content;
const totalSeconds = document.querySelector('meta[name="seconds"]').content;

const username = document.querySelector('meta[name="username"]').content;
const url = `/dashboard/${username}/ironstead/logging/`
let activeTask = null;
let fastMode = false; // dev/testing speedup
const speedFactor = 1; // if fastMode true, 1 real second == 60 seconds
const logEl = document.getElementById('log');

function log(msg){
  const t = new Date().toLocaleTimeString();
  logEl.innerHTML = `<div style="margin-bottom:6px">[${t}] ${msg}</div>` + logEl.innerHTML;
}

function qs(sel){ return document.querySelector(sel) }
function qsa(sel){ return document.querySelectorAll(sel) }

function init(){
  //console.log("SUS")
  // render presets
  const presetsWrap = document.getElementById('presets');
  presets.forEach(h => {
    const btn = document.createElement('button');
    btn.className = 'preset-btn';
    btn.innerText = h + 'h';
    btn.dataset.hours = h;
    btn.addEventListener('click', () => selectPreset(h, btn));
    presetsWrap.appendChild(btn);
  });
  // default select 4h
  selectPreset(4, presetsWrap.querySelector('[data-hours="4"]'));

  // skill badges
  renderSkillBadges(3);

  // hook controls
  const skillRange = document.getElementById('skillRange');
  const skillVal = document.getElementById('skillVal');
  skillRange.addEventListener('input', (e)=>{
    skillVal.innerText = e.target.value;
    renderSkillBadges(Number(e.target.value));
    updateEstimate();
  });

  document.getElementById('startBtn').addEventListener('click', startTask);
  document.getElementById('stopBtn').addEventListener('click', cancelTask);
  //document.getElementById('toggleFast').addEventListener('click', toggleFastMode);

  // restore inventory
  updateEstimate();
}

let selectedHours = 4;
function selectPreset(h, btn){
  selectedHours = h;
  qsa('.preset-btn').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
  updateEstimate();
}

function renderSkillBadges(skill){
  const wrap = document.getElementById('skillBadges');
  wrap.innerHTML = '';
  const label = skill <=2 ? 'Novice' : skill<=5 ? 'Journeyman' : skill<=8 ? 'Expert' : 'Master';
  const badges = [
    `${label}`,
    `+${Math.round(skill*8)}% yield`,
    `${(baseRare + skill*3).toFixed(0)}% rare potential`
  ];
  badges.forEach(b=>{
    const el = document.createElement('div');
    el.className = 'badge';
    el.innerText = b;
    wrap.appendChild(el);
  });
}

function estYield(hours, skill){
  const randomVar = 0.92 + Math.random()*0.16; // 0.92..1.08
  const raw = baseYieldPerHour * hours * (1 + skill * skillMultiplier) * randomVar;
  return Math.max(1, Math.floor(raw + 0.5));
}

function estimateRareCount(hours, skill){
  const chance = Math.min(maxRareChance, baseRare + skill*3);
  // expected rare logs roughly proportional to hours and chance
  return Math.floor(hours * (chance/100) * (0.5 + Math.random()*1.2));
}

function updateEstimate(){
  const skill = Number(document.getElementById('skillRange').value);
  const est = estYield(selectedHours, skill);
  const rare = estimateRareCount(selectedHours, skill);
  document.getElementById('estimate').innerText = `~ ${est} wood • ~ ${rare} rare logs`;
}

function toggleFastMode(){
  fastMode = !fastMode;
  const btn = document.getElementById('toggleFast');
  btn.innerText = fastMode ? 'ON' : 'OFF';
  btn.style.borderColor = fastMode ? 'rgba(126,231,135,0.18)' : '';
  log(`Fast mode ${fastMode ? 'enabled' : 'disabled'} (x${speedFactor})`);
}


function sendTimeToBack(time){
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'timeSave'
        },
        body: JSON.stringify({'time': time}),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json(); // Parse JSON response
    })
    .then(responseData => {
        //console.log(responseData)
        document.querySelector('meta[name="start_time"]').setAttribute("content", Math.floor(responseData.start_time));
        document.querySelector('meta[name="seconds"]').setAttribute("content", responseData.duration_seconds);
        //console.log(start_time);
        //console.log(`totalSeconds update: ${totalSeconds}`);
        startOnGet()
    })

}


function startTask(){
  const hours = selectedHours;
  //console.log(selectedHours)
  sendTimeToBack(hours) // send start time for db
  //console.log(hours);
}

function cancelTask(){
   if(!activeTask){ log('No active task to cancel.'); return; }
   fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Custom-Message': 'cancelTask'
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json(); // Parse JSON response
    })
    .then(responseData => {
          clearInterval(activeTask); activeTask = null;
          document.getElementById('progressBar').style.width = '0%';
          document.getElementById('timeLeft').innerText = 'Cancelled';
          document.getElementById('percentLeft').innerText = '0%';
          document.getElementById('startBtn').disabled = false;
          document.getElementById('stopBtn').disabled = true;
          document.getElementById('startBtn').setAttribute('aria-pressed','false');
          log('Task cancelled — you returned early.');
    })
}


function endTask(){
  if(!activeTask){ log('No active task to end.'); return; }
  clearInterval(activeTask); activeTask = null;
  document.getElementById('progressBar').style.width = '0%';
  document.getElementById('timeLeft').innerText = 'You Finished Cutting Wood';
  document.getElementById('percentLeft').innerText = '0%';
  document.getElementById('startBtn').disabled = false;
  document.getElementById('stopBtn').disabled = true;
  document.getElementById('startBtn').setAttribute('aria-pressed','false');
  log('Task Finished — you returned eager to start again.');
}




function finishTask(hours, skill){
  // calculate final yield
  const randomVar = 0.95 + Math.random()*0.12;
  const wood = Math.max(1, Math.floor(baseYieldPerHour * hours * (1 + skill*skillMultiplier) * randomVar + 0.5));
  // rare chance per hour basis
  const chance = Math.min(maxRareChance, baseRare + skill*3);
  let rare = 0;
  for(let i=0;i<hours;i++){
    if(Math.random()*100 < chance) rare += 1;
  }
  // chance for bonus (skill-driven)
  if(Math.random()*100 < skill*2) rare += 1;

  addToInventory(wood, rare, hours);
  renderInventory();
  log(`You returned: +${wood} wood${rare?`, +${rare} rare logs`:''}.`);
  // reset progress UI
  document.getElementById('progressBar').style.width = '100%';
  document.getElementById('timeLeft').innerText = 'Return complete';
  document.getElementById('percentLeft').innerText = '100%';
}

async function addToInventory(wood, rare, time) {
  try {
    // Send update request to backend
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken, 'X-Custom-Message': 'addWood' },
      body: JSON.stringify({ wood, rare, "time": time})
    });

    if (!response.ok) {
      throw new Error('Failed to update inventory on server');
    }

    // After update, fetch fresh inventory
    const inventory = await fetchInventory();
    renderInventory(inventory);
    endTask()
  } catch (err) {
    console.error('Error updating inventory:', err);
  }
}

// Fetch inventory from backend
async function fetchInventory() {
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json',
                 'X-CSRFToken': csrfToken,
                 'X-Custom-Message': 'inventory',},

    });
    if (!response.ok) {
      throw new Error('Failed to fetch inventory from server');
    }
    const inventory = await response.json();
    return inventory;
  } catch (err) {
    console.error('Error fetching inventory:', err);
    // Return fallback empty inventory to avoid app crash
    return { wood: 0, rare: 0 };
  }
}

// Render inventory quantities in the UI
function renderInventory(inv) {
  document.getElementById('woodQty').innerText = inv.wood || 0;
  document.getElementById('rareQty').innerText = inv.rare || 0;
}

function secondsToHms(d){
  d = Number(d);
  const h = Math.floor(d / 3600);
  const m = Math.floor((d % 3600) / 60);
  const s = Math.floor(d % 60);
  if(h>0) return `${h}h ${m}m ${s}s`;
  if(m>0) return `${m}m ${s}s`;
  return `${s}s`;
}


function startOnGet(){
    const start_time = document.querySelector('meta[name="start_time"]').content;
    const totalSeconds = Number(document.querySelector('meta[name="seconds"]').content);
    //console.log(`start_time: ${start_time}`);
    const skill = Number(document.getElementById('skillRange').value);
    const tickRate = 1000; // ms
    const ticksNeeded = Math.round(totalSeconds);


    let startTime = Number(start_time) * 1000;

    let elapsed = 0;

    // show UI
    if (!start_time || start_time === "None" || !totalSeconds || totalSeconds === "None") {
        // no active task
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('startBtn').setAttribute('aria-pressed', 'false');
    } else {
        // task in progress
        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('startBtn').setAttribute('aria-pressed', 'true');
    }

    if (!start_time || start_time === "None"){
        return
    }
    activeTask = setInterval(() => {
      const now = Date.now();
      const realElapsedSec = Math.floor((now - startTime) / 1000);
      elapsed = fastMode ? realElapsedSec * speedFactor : realElapsedSec;
      //console.log(`Big elaped: ${elapsed}`)

      if (elapsed > totalSeconds) elapsed = totalSeconds;

      // percent counter
      let pct = 0;
      //console.log(totalSeconds)
      if (totalSeconds){
        pct = Math.floor((elapsed / totalSeconds) * 100);
      }
      //console.log(pct)

      // update progress
      document.getElementById('progressBar').style.width = pct + '%';
      document.querySelector('.progress').setAttribute('aria-valuenow', pct);

      // update countdown
      const remaining = Math.max(0, totalSeconds - elapsed);
      //console.log(`remaining ${remaining}`)

      document.getElementById('percentLeft').innerText = `${pct}%`;
      document.getElementById('timeLeft').innerText =
        remaining > 0 ? secondsToHms(remaining) + ' left' : 'Completed';

      if (elapsed >= totalSeconds) {
        const hours = totalSeconds / 3600;
        finishTask(hours, skill);
        clearInterval(activeTask);
        activeTask = null;
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('startBtn').setAttribute('aria-pressed', 'false');
      }
    }, tickRate);

}



(async () => {
  startOnGet()
  const initialInv = await fetchInventory();
  //console.log(initialInv)
  renderInventory(initialInv);
})();

init();
