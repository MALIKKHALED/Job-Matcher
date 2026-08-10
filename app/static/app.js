const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function mdToHtml(src) {
  const lines = esc(src).split(/\r?\n/);
  let html = "", inList = false;
  const close = () => { if (inList) { html += "</ul>"; inList = false; } };
  const strong = (s) => s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (!line.trim()) { close(); continue; }
    if (/^###\s+/.test(line)) { close(); html += "<h3>" + line.replace(/^###\s+/, "") + "</h3>"; }
    else if (/^##\s+/.test(line)) { close(); html += "<h2>" + line.replace(/^##\s+/, "") + "</h2>"; }
    else if (/^#\s+/.test(line)) { close(); html += "<h1>" + line.replace(/^#\s+/, "") + "</h1>"; }
    else if (/^\s*[-*]\s+/.test(line)) {
      if (!inList) { html += "<ul>"; inList = true; }
      html += "<li>" + strong(line.replace(/^\s*[-*]\s+/, "")) + "</li>";
    } else { close(); html += "<p>" + strong(line) + "</p>"; }
  }
  close();
  return html;
}

function download(name, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

function chips(list) {
  return (list || []).map((s) => `<span class="chip">${esc(s)}</span>`).join("");
}

function card(title, inner) {
  return `<h2>${title}</h2>${inner}`;
}

function render(r) {
  const ats = r.ats_report;
  const match = r.match_report;
  const badge = match.recommendation === "Apply now" ? "ok"
    : match.recommendation === "Improve then apply" ? "warn" : "bad";

  $("score-cards").innerHTML = `
    <div class="card score">
      <h2>ATS Score</h2>
      <div class="big">${ats.total_score}<span>/${ats.max_score}</span></div>
      <div class="bar"><div style="width:${ats.total_score}%"></div></div>
      <ul class="small">
        ${(ats.deductions || []).map((d) => `<li>- ${esc(d)}</li>`).join("") || "<li>No deductions</li>"}
      </ul>
    </div>
    <div class="card score">
      <h2>Job Match</h2>
      <div class="big">${match.match_percentage}<span>%</span></div>
      <span class="badge ${badge}">${esc(match.recommendation)}</span>
      <h3>Matched</h3><div class="chips">${chips(match.matched_skills)}</div>
      <h3>Missing</h3><div class="chips muted">${chips(match.missing_skills)}</div>
      <h3>Gaps</h3>
      <ul class="small">${(match.gaps || []).map((g) => `<li>${esc(g)}</li>`).join("")}</ul>
    </div>`;

  const miss = r.optimized_resume.missing_info_report;
  if (miss && miss.length) {
    $("missing-check").hidden = false;
    $("missing-check").innerHTML = card("Missing Info — add these to your resume",
      `<ul class="small">${miss.map((m) => `<li>${esc(m)}</li>`).join("")}</ul>`);
  }

  const changes = r.optimized_resume.changes || [];
  $("changes-card").hidden = false;
  $("changes-card").innerHTML =
    card("Changes Applied (no-invention audit)",
      changes.length
        ? `<ul class="small">${changes.map((c) => `<li>${esc(c)}</li>`).join("")}</ul>`
        : `<p class="small">No changes — resume already optimized.</p>`);

  $("resume-card").hidden = false;
  $("resume-card").innerHTML =
    card("Optimized Resume",
      `<button onclick="download('optimized_resume.md', window.__resume)">Download .md</button>
       <div class="markdown">${mdToHtml(r.optimized_resume.markdown)}</div>`);
  window.__resume = r.optimized_resume.markdown;

  $("cover-card").hidden = false;
  $("cover-card").innerHTML =
    card("Cover Letter",
      `<button onclick="download('cover_letter.md', window.__cover)">Download .md</button>
       <p class="subject">${esc(r.cover_letter.subject)}</p>
       <div class="markdown">${mdToHtml(r.cover_letter.body)}</div>
       ${r.cover_letter.notes && r.cover_letter.notes.length
         ? `<h3>Before sending</h3><ul class="small">${r.cover_letter.notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul>`
         : ""}`);
  window.__cover = `Subject: ${r.cover_letter.subject}\n\n${r.cover_letter.body}`;

  const j = r.job_details;
  $("job-card").innerHTML = `
    <h3>${esc(j.job_title)} — ${esc(j.company_name)}</h3>
    <p><a href="${esc(j.page_url)}" target="_blank">${esc(j.page_url)}</a></p>
    <h4>Requirements</h4><p>${esc(j.job_requirements)}</p>
    <h4>Responsibilities</h4><p>${esc(j.job_responsibilities)}</p>
    <h4>Skills</h4><div class="chips">${chips(j.required_skills)}</div>`;
}

async function run() {
  const url = $("job_url").value.trim();
  const text = $("resume_text").value.trim();
  if (!url || !text) { alert("Enter both a job URL and resume text."); return; }

  $("run-btn").disabled = true;
  $("results").hidden = true;
  const st = $("status");
  st.hidden = false;
  st.textContent = "Starting pipeline...";

  try {
    const res = await fetch("/api/pipeline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_url: url,
        resume_text: text,
        user_supplied_info: $("user_supplied_info").value.trim(),
      }),
    });
    if (!res.ok) throw new Error("Failed to start pipeline: " + (await res.text()));
    const { job_id } = await res.json();

    for (;;) {
      const poll = await fetch(`/api/pipeline/${job_id}`);
      const data = await poll.json();
      if (data.status === "done") {
        st.textContent = "Done.";
        $("results").hidden = false;
        render(data.result);
        break;
      }
      if (data.status === "error") { throw new Error(data.error || "Pipeline failed"); }
      st.textContent = "Running agents... (this takes 1–3 min)";
      await new Promise((r) => setTimeout(r, 3000));
    }
  } catch (err) {
    st.textContent = "Error: " + err.message;
  } finally {
    $("run-btn").disabled = false;
  }
}

$("run-btn").addEventListener("click", run);