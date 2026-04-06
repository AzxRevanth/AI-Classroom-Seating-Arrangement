const DEMO = `A and B are friends
C wants front
D and E are not friends
F needs teacher visibility
G wants back`;

function loadDemo() {
  document.getElementById("constraints").value = DEMO;
}

function showPage(id) {
  document.getElementById("page-input").style.display = id === "input" ? "" : "none";
  document.getElementById("page-result").style.display = id === "result" ? "" : "none";
}

function renderRow(containerId, students) {
  const el = document.getElementById(containerId);
  el.innerHTML = students.map(s => `<div class="seat">${s}</div>`).join("");
}

function renderExplanations(items) {
  const el = document.getElementById("explanations");
  if (!items.length) {
    el.innerHTML = "<p style='color:#8a9e8d'>No constraints entered.</p>";
    return;
  }
  el.innerHTML = items.map(e => `
    <div class="exp-item ${e.satisfied ? "pass" : "fail"}">
      <span>${e.satisfied ? "✅" : "❌"}</span>
      <div>
        <div>${e.text}</div>
        <div class="detail">${e.detail}</div>
      </div>
    </div>
  `).join("");
}

async function generate() {
  const text = document.getElementById("constraints").value.trim();
  const btn = document.getElementById("btn-generate");
  btn.textContent = "Thinking…";
  btn.disabled = true;

  try {
    const res = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ constraints: text })
    });
    const data = await res.json();

    renderRow("front-row", data.grid[0]);
    renderRow("back-row", data.grid[1]);
    renderExplanations(data.explanations);

    const tag = document.getElementById("score-tag");
    tag.textContent = `Penalty: ${data.score}`;
    tag.className = "score-tag " + (data.score === 0 ? "score-good" : data.score <= 6 ? "score-ok" : "score-bad");

    showPage("result");
  } catch (err) {
    alert("Error: " + err.message);
  } finally {
    btn.textContent = "Generate Seating";
    btn.disabled = false;
  }
}
