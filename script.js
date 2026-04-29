const budgetInput = document.getElementById("budgetInput");
const modeSelect = document.getElementById("modeSelect");
const runBtn = document.getElementById("runBtn");
const addBtn = document.getElementById("addBtn");
const resetBtn = document.getElementById("resetBtn");

const nameInput = document.getElementById("nameInput");
const costInput = document.getElementById("costInput");
const returnInput = document.getElementById("returnInput");

const optionsBody = document.getElementById("optionsBody");
const resultSection = document.getElementById("resultSection");
const historyBody = document.getElementById("historyBody");

const metricCoverage = document.getElementById("metricCoverage");
const metricPotential = document.getElementById("metricPotential");
const metricAvgRoi = document.getElementById("metricAvgRoi");
const metricBest = document.getElementById("metricBest");
const metricWinner = document.getElementById("metricWinner");
const metricOverbook = document.getElementById("metricOverbook");

const optionPerfBody = document.getElementById("optionPerfBody");
const methodPerfBody = document.getElementById("methodPerfBody");
const fractionalTraceBody = document.getElementById("fractionalTraceBody");
const dpTraceBody = document.getElementById("dpTraceBody");

const fractionalGuideTitle = document.getElementById("fractionalGuideTitle");
const fractionalGuideText = document.getElementById("fractionalGuideText");
const fractionalGuideComplexity = document.getElementById("fractionalGuideComplexity");
const dpGuideTitle = document.getElementById("dpGuideTitle");
const dpGuideText = document.getElementById("dpGuideText");
const dpGuideComplexity = document.getElementById("dpGuideComplexity");
const dpGuideScale = document.getElementById("dpGuideScale");

const allocationPieGrid = document.getElementById("allocationPieGrid");
const allocationTemplate = document.getElementById("allocationTemplate");

const chartCanvas = {
  costPie: document.getElementById("costPieChart"),
  returnPie: document.getElementById("returnPieChart"),
  ratioBar: document.getElementById("ratioBarChart"),
  methodBar: document.getElementById("methodReturnChart"),
  methodRadar: document.getElementById("methodRadarChart"),
  dpCurve: document.getElementById("dpCurveChart")
};

let options = [];
let historyRows = [];
let activeCharts = {};
let allocationPieCharts = [];

const metallicPalette = [
  "#d4af37",
  "#c0c0c0",
  "#e5e4e2",
  "#a48224",
  "#9a9a9a",
  "#f1dfb0",
  "#7f6a22"
];

function formatInr(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0
  }).format(amount);
}

function formatPercent(value, digits = 1) {
  return `${(value * 100).toFixed(digits)}%`;
}

function ratio(item) {
  return item.value / item.cost;
}

function roi(item) {
  return (item.value - item.cost) / item.cost;
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options
  });

  const payload = await response.json();
  if (!response.ok || !payload.ok) {
    throw new Error(payload.error || "Request failed.");
  }
  return payload;
}

function renderOptionsTable() {
  optionsBody.innerHTML = "";

  if (!options.length) {
    optionsBody.innerHTML = '<tr><td colspan="6">No options in database.</td></tr>';
    return;
  }

  options.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.name}</td>
      <td>${formatInr(item.cost)}</td>
      <td>${formatInr(item.value)}</td>
      <td>${ratio(item).toFixed(2)}x</td>
      <td>${formatPercent(roi(item))}</td>
      <td><button class="remove-btn" data-id="${item.id}">Delete</button></td>
    `;
    optionsBody.appendChild(row);
  });
}

function renderHistoryTable(rows) {
  historyBody.innerHTML = "";

  if (!rows.length) {
    historyBody.innerHTML = '<tr><td colspan="8">No analysis runs logged yet.</td></tr>';
    return;
  }

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.runAt}</td>
      <td>${row.mode}</td>
      <td>${formatInr(row.budget)}</td>
      <td>${row.optionCount}</td>
      <td>${row.fractionalValue === null ? "-" : formatInr(Math.round(row.fractionalValue))}</td>
      <td>${row.dpValue === null ? "-" : formatInr(Math.round(row.dpValue))}</td>
      <td>${row.winner || "-"}</td>
      <td>${row.utilization === null ? "-" : formatPercent(row.utilization)}</td>
    `;
    historyBody.appendChild(tr);
  });
}

function renderMetrics(metrics) {
  metricCoverage.textContent = metrics.coverageText;
  metricPotential.textContent = metrics.potentialText;
  metricAvgRoi.textContent = metrics.averageRoiText;
  metricBest.textContent = metrics.bestText;
  metricWinner.textContent = metrics.winnerText;
  metricOverbook.textContent = `${metrics.overbookRatio.toFixed(2)}x`;
}

function clearTableBody(tableBody, colCount, message) {
  tableBody.innerHTML = `<tr><td colspan="${colCount}">${message}</td></tr>`;
}

function renderOptionPerformanceTable(rows) {
  optionPerfBody.innerHTML = "";
  if (!rows.length) {
    clearTableBody(optionPerfBody, 6, "No option metrics.");
    return;
  }

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.rank}</td>
      <td>${row.name}</td>
      <td>${row.ratio.toFixed(2)}x</td>
      <td>${formatPercent(row.roi)}</td>
      <td>${formatPercent(row.costShare)}</td>
      <td>${formatPercent(row.budgetPressure)}</td>
    `;
    optionPerfBody.appendChild(tr);
  });
}

function renderMethodPerformanceTable(rows) {
  methodPerfBody.innerHTML = "";
  if (!rows.length) {
    clearTableBody(methodPerfBody, 7, "Run an algorithm mode to populate this table.");
    return;
  }

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.method}</td>
      <td>${formatInr(Math.round(row.totalReturn))}</td>
      <td>${formatInr(row.budgetUsed)}</td>
      <td>${formatInr(row.budgetLeft)}</td>
      <td>${formatPercent(row.utilization)}</td>
      <td>${formatPercent(row.roi)}</td>
      <td>${row.selectionCount}</td>
    `;
    methodPerfBody.appendChild(tr);
  });
}

function renderFractionalTrace(rows) {
  fractionalTraceBody.innerHTML = "";
  if (!rows.length) {
    clearTableBody(fractionalTraceBody, 7, "Run fractional or compare mode to view greedy trace.");
    return;
  }

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.step}</td>
      <td>${row.name}</td>
      <td>${row.ratio.toFixed(2)}x</td>
      <td>${formatPercent(row.takenFraction)}</td>
      <td>${formatInr(row.invested)}</td>
      <td>${formatInr(Math.round(row.gained))}</td>
      <td>${formatInr(row.remainingBudget)}</td>
    `;
    fractionalTraceBody.appendChild(tr);
  });
}

function renderDpTrace(rows) {
  dpTraceBody.innerHTML = "";
  if (!rows.length) {
    clearTableBody(dpTraceBody, 6, "Run DP 0/1 or compare mode to view DP trace.");
    return;
  }

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.step}</td>
      <td>${row.name}</td>
      <td>${row.scaledCost}</td>
      <td>${row.selected ? "Yes" : "No"}</td>
      <td>${formatInr(row.cost)}</td>
      <td>${formatInr(row.value)}</td>
    `;
    dpTraceBody.appendChild(tr);
  });
}

function renderGuides(guides) {
  const fractional = guides.fractional;
  const dp = guides.dp01;

  fractionalGuideTitle.textContent = fractional.title;
  fractionalGuideText.textContent = fractional.strategy;
  fractionalGuideComplexity.textContent = `Time: ${fractional.timeComplexity} | Space: ${fractional.spaceComplexity}`;

  dpGuideTitle.textContent = dp.title;
  dpGuideText.textContent = dp.strategy;
  dpGuideComplexity.textContent = `Time: ${dp.timeComplexity} | Space: ${dp.spaceComplexity}`;

  if (dp.scaledCapacity === null || dp.scaleFactor === null) {
    dpGuideScale.textContent = "Run DP mode to see matrix sizing details.";
  } else {
    dpGuideScale.textContent = `Scaled Capacity: ${dp.scaledCapacity}, Scale Factor: ${dp.scaleFactor}, Table Cells: ${dp.tableCells}`;
  }
}

function createChipText(pick) {
  if (pick.fraction < 1) {
    return `${pick.name} (${(pick.fraction * 100).toFixed(1)}%)`;
  }
  return `${pick.name} (100%)`;
}

function renderResultCards(results, comparison) {
  resultSection.innerHTML = "";

  if (!results.length && !comparison) {
    return;
  }

  results.forEach((result) => {
    const card = allocationTemplate.content.firstElementChild.cloneNode(true);
    card.classList.add(result.key === "fractional" ? "result-fractional" : "result-dp");

    card.querySelector(".title").textContent = result.method;
    card.querySelector(".total-return").textContent = `Return: ${formatInr(Math.round(result.totalValue))}`;
    card.querySelector(".budget-used").textContent = `Budget Used: ${formatInr(result.used)}`;
    card.querySelector(".leftover").textContent = `Budget Left: ${formatInr(result.remaining)}`;
    card.querySelector(".strategy-roi").textContent = `Realized ROI: ${formatPercent(result.roi)}`;
    card.querySelector(".selection-count").textContent = `Selected Options: ${result.selectionCount}`;
    card.querySelector(".note").textContent = result.note;

    const chipsEl = card.querySelector(".chips");
    if (!result.picks.length) {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = "No selections";
      chipsEl.appendChild(chip);
    } else {
      result.picks.forEach((pick) => {
        const chip = document.createElement("span");
        chip.className = pick.fraction < 1 ? "chip partial" : "chip";
        chip.textContent = createChipText(pick);
        chipsEl.appendChild(chip);
      });
    }

    resultSection.appendChild(card);
  });

  if (comparison) {
    const card = allocationTemplate.content.firstElementChild.cloneNode(true);
    card.classList.add("result-insight");

    card.querySelector(".title").textContent = "Comparison Insight";
    card.querySelector(".total-return").textContent = `Return Delta: ${formatInr(Math.round(comparison.deltaAbs))}`;
    card.querySelector(".budget-used").textContent = `Winner: ${comparison.winner}`;
    card.querySelector(".leftover").textContent = `Fractional ROI: ${formatPercent(comparison.fractionalRoi)}`;
    card.querySelector(".strategy-roi").textContent = `DP ROI: ${formatPercent(comparison.dpRoi)}`;
    card.querySelector(".selection-count").textContent = "Decision Basis: Return difference";
    card.querySelector(".note").textContent = comparison.verdict;

    const chipsEl = card.querySelector(".chips");
    ["Greedy supports fractional picks", "DP enforces all-or-none picks"].forEach((text) => {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = text;
      chipsEl.appendChild(chip);
    });

    resultSection.appendChild(card);
  }
}

function destroyChart(chartKey) {
  if (activeCharts[chartKey]) {
    activeCharts[chartKey].destroy();
    activeCharts[chartKey] = null;
  }
}

function destroyAllocationCharts() {
  allocationPieCharts.forEach((chart) => chart.destroy());
  allocationPieCharts = [];
  allocationPieGrid.innerHTML = "";
}

function chartTextColor() {
  return "#d7d7dd";
}

function baseChartOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: chartTextColor()
        }
      }
    },
    scales: {
      x: {
        ticks: { color: chartTextColor() },
        grid: { color: "rgba(255,255,255,0.08)" }
      },
      y: {
        ticks: { color: chartTextColor() },
        grid: { color: "rgba(255,255,255,0.08)" }
      }
    }
  };
}

function renderCharts(charts) {
  destroyChart("costPie");
  destroyChart("returnPie");
  destroyChart("ratioBar");
  destroyChart("methodBar");
  destroyChart("methodRadar");
  destroyChart("dpCurve");
  destroyAllocationCharts();

  activeCharts.costPie = new Chart(chartCanvas.costPie, {
    type: "pie",
    data: {
      labels: charts.portfolioCostPie.labels,
      datasets: [{
        data: charts.portfolioCostPie.values,
        backgroundColor: metallicPalette
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: chartTextColor() } } }
    }
  });

  activeCharts.returnPie = new Chart(chartCanvas.returnPie, {
    type: "doughnut",
    data: {
      labels: charts.portfolioReturnPie.labels,
      datasets: [{
        data: charts.portfolioReturnPie.values,
        backgroundColor: metallicPalette
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: chartTextColor() } } }
    }
  });

  activeCharts.ratioBar = new Chart(chartCanvas.ratioBar, {
    type: "bar",
    data: {
      labels: charts.ratioBar.labels,
      datasets: [{
        label: "Value/Cost Ratio",
        data: charts.ratioBar.values,
        backgroundColor: "rgba(212, 175, 55, 0.7)",
        borderColor: "#d4af37",
        borderWidth: 1
      }]
    },
    options: baseChartOptions()
  });

  if (charts.methodReturnBar.labels.length > 0) {
    chartCanvas.methodBar.style.display = "";
    activeCharts.methodBar = new Chart(chartCanvas.methodBar, {
      type: "bar",
      data: {
        labels: charts.methodReturnBar.labels,
        datasets: [{
          label: "Method Return",
          data: charts.methodReturnBar.values,
          backgroundColor: ["rgba(212, 175, 55, 0.75)", "rgba(192, 192, 192, 0.7)", "rgba(229, 228, 226, 0.65)"]
        }]
      },
      options: baseChartOptions()
    });
  } else {
    chartCanvas.methodBar.style.display = "none";
  }

  if (charts.methodRadar.datasets.length > 0) {
    chartCanvas.methodRadar.style.display = "";
    activeCharts.methodRadar = new Chart(chartCanvas.methodRadar, {
      type: "radar",
      data: {
        labels: charts.methodRadar.labels,
        datasets: charts.methodRadar.datasets.map((dataset, index) => {
          const palette = ["#d4af37", "#c0c0c0", "#e5e4e2"][index % 3];
          return {
            label: dataset.label,
            data: dataset.values,
            borderColor: palette,
            backgroundColor: `${palette}40`,
            pointBackgroundColor: palette,
            pointBorderColor: palette
          };
        })
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: chartTextColor() } }
        },
        scales: {
          r: {
            angleLines: { color: "rgba(255,255,255,0.12)" },
            grid: { color: "rgba(255,255,255,0.12)" },
            pointLabels: { color: chartTextColor() },
            ticks: {
              color: chartTextColor(),
              backdropColor: "rgba(0,0,0,0.4)"
            }
          }
        }
      }
    });
  } else {
    chartCanvas.methodRadar.style.display = "none";
  }

  if (charts.dpValueCurve.labels.length > 0) {
    chartCanvas.dpCurve.style.display = "";
    activeCharts.dpCurve = new Chart(chartCanvas.dpCurve, {
      type: "line",
      data: {
        labels: charts.dpValueCurve.labels,
        datasets: [{
          label: "Best Value by Capacity Unit",
          data: charts.dpValueCurve.values,
          borderColor: "#e5e4e2",
          backgroundColor: "rgba(229, 228, 226, 0.2)",
          fill: true,
          tension: 0.3
        }]
      },
      options: baseChartOptions()
    });
  } else {
    chartCanvas.dpCurve.style.display = "none";
  }

  charts.allocationPies.forEach((pieData, index) => {
    const wrap = document.createElement("article");
    wrap.className = "allocation-item";

    const title = document.createElement("h4");
    title.textContent = `${pieData.method} Allocation Pie`;
    wrap.appendChild(title);

    const canvas = document.createElement("canvas");
    canvas.id = `allocationPie_${index}`;
    wrap.appendChild(canvas);
    allocationPieGrid.appendChild(wrap);

    const chart = new Chart(canvas, {
      type: "pie",
      data: {
        labels: pieData.labels,
        datasets: [{
          data: pieData.values,
          backgroundColor: metallicPalette
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: chartTextColor() } } }
      }
    });

    allocationPieCharts.push(chart);
  });
}

function renderAnalysisPayload(payload) {
  options = payload.options;
  renderOptionsTable();

  renderMetrics(payload.metrics);
  renderResultCards(payload.results, payload.comparison);

  renderOptionPerformanceTable(payload.tables.optionPerformance);
  renderMethodPerformanceTable(payload.tables.methodPerformance);
  renderFractionalTrace(payload.tables.fractionalTrace);
  renderDpTrace(payload.tables.dpTrace);

  renderGuides(payload.guides);
  renderCharts(payload.charts);

  if (Array.isArray(payload.history)) {
    historyRows = payload.history;
    renderHistoryTable(historyRows);
  }
}

async function loadBootstrap() {
  const payload = await apiRequest("/api/bootstrap", { method: "GET" });
  options = payload.options;
  historyRows = payload.history;
  renderOptionsTable();
  renderHistoryTable(historyRows);
}

async function runAnalysis(mode = null) {
  const selectedMode = mode || modeSelect.value;

  const payload = await apiRequest("/api/analyze", {
    method: "POST",
    body: JSON.stringify({
      budget: budgetInput.value,
      mode: selectedMode
    })
  });

  renderAnalysisPayload(payload);
}

async function addOption() {
  const name = nameInput.value.trim();
  const cost = costInput.value.trim();
  const value = returnInput.value.trim();

  if (!name || !cost || !value) {
    alert("Fill name, required amount, and expected return.");
    return;
  }

  const payload = await apiRequest("/api/options", {
    method: "POST",
    body: JSON.stringify({ name, cost, value })
  });

  options = payload.options;
  renderOptionsTable();

  nameInput.value = "";
  costInput.value = "";
  returnInput.value = "";

  await runAnalysis("insights");
}

async function deleteOption(optionId) {
  const payload = await apiRequest(`/api/options/${optionId}`, {
    method: "DELETE"
  });

  options = payload.options;
  renderOptionsTable();
  await runAnalysis("insights");
}

async function resetOptions() {
  const payload = await apiRequest("/api/options/reset", {
    method: "POST"
  });

  options = payload.options;
  renderOptionsTable();
  await runAnalysis("insights");
}

optionsBody.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) return;

  const optionId = target.dataset.id;
  if (!optionId) return;

  try {
    await deleteOption(optionId);
  } catch (error) {
    alert(error.message);
  }
});

runBtn.addEventListener("click", async () => {
  try {
    await runAnalysis();
  } catch (error) {
    alert(error.message);
  }
});

addBtn.addEventListener("click", async () => {
  try {
    await addOption();
  } catch (error) {
    alert(error.message);
  }
});

resetBtn.addEventListener("click", async () => {
  try {
    await resetOptions();
  } catch (error) {
    alert(error.message);
  }
});

(async function init() {
  try {
    await loadBootstrap();
    await runAnalysis("compare");
  } catch (error) {
    alert(error.message);
  }
})();
