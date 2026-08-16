const samplePath = "../data/sample/walmart_sales_sample.csv";
let rawRows = [];

const fields = {
  storeFilter: document.getElementById("storeFilter"),
  holidayFilter: document.getElementById("holidayFilter"),
  groupFilter: document.getElementById("groupFilter"),
  csvInput: document.getElementById("csvInput"),
};

const metrics = {
  totalSales: document.getElementById("totalSales"),
  avgSales: document.getElementById("avgSales"),
  storeCount: document.getElementById("storeCount"),
  holidayShare: document.getElementById("holidayShare"),
};

function parseCsv(text) {
  const rows = [];
  let field = "";
  let row = [];
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];

    if (char === '"' && inQuotes && next === '"') {
      field += '"';
      i += 1;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      row.push(field);
      field = "";
    } else if ((char === "\n" || char === "\r") && !inQuotes) {
      if (field || row.length) {
        row.push(field);
        rows.push(row);
        row = [];
        field = "";
      }
      if (char === "\r" && next === "\n") i += 1;
    } else {
      field += char;
    }
  }

  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }

  if (!rows.length) return [];

  const headers = rows.shift().map((header) => normalizeHeader(header));
  return rows
    .filter((values) => values.length > 1)
    .map((values) =>
      Object.fromEntries(headers.map((header, index) => [header, coerceValue(values[index] || "")]))
    );
}

function normalizeHeader(header) {
  const clean = header.trim();
  const key = clean.toLowerCase().replace(/\s+/g, "_");
  const aliases = {
    weekly_sales: "Weekly_Sales",
    weekly_sales_: "Weekly_Sales",
    sales: "Weekly_Sales",
    store: "Store",
    dept: "Dept",
    department: "Dept",
    date: "Date",
    holiday_flag: "Holiday_Flag",
    isholiday: "Holiday_Flag",
    is_holiday: "Holiday_Flag",
    fuel_price: "Fuel_Price",
    cpi: "CPI",
    unemployment: "Unemployment",
    temperature: "Temperature",
    type: "Type",
    size: "Size",
    region: "Region",
    category: "Category",
    product: "Product",
    quantity: "Quantity",
    unit_price: "Unit_Price",
    unitprice: "Unit_Price",
    discount: "Discount",
    revenue: "Revenue",
    profit: "Profit",
    profit_margin: "Profit_Margin",
    customer_segment: "Customer_Segment",
  };
  return aliases[key] || clean.replace(/\s+/g, "_");
}

function coerceValue(value) {
  const trimmed = value.trim();
  if (trimmed === "") return "";
  if (/^(true|false)$/i.test(trimmed)) return /^true$/i.test(trimmed) ? 1 : 0;
  const numeric = Number(trimmed.replace(/[$,%]/g, ""));
  return Number.isFinite(numeric) && trimmed.match(/^-?[$]?\d/) ? numeric : trimmed;
}

function currency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function percent(value) {
  return new Intl.NumberFormat("en-US", {
    style: "percent",
    maximumFractionDigits: 1,
  }).format(value || 0);
}

function monthKey(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown";
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function sumBy(rows, key) {
  const grouped = new Map();
  rows.forEach((row) => {
    const label = row[key] ?? "Unknown";
    const current = grouped.get(label) || { label, total: 0, count: 0 };
    current.total += Number(row.Revenue ?? row.Weekly_Sales) || 0;
    current.count += 1;
    grouped.set(label, current);
  });
  return [...grouped.values()].sort((a, b) => b.total - a.total);
}

function filteredRows() {
  const selectedStore = fields.storeFilter.value;
  const selectedHoliday = fields.holidayFilter.value;
  return rawRows.filter((row) => {
    const storeMatch = selectedStore === "all" || String(row.Store) === selectedStore;
    const holidayValue = String(Number(row.Holiday_Flag || 0));
    const holidayMatch = selectedHoliday === "all" || holidayValue === selectedHoliday;
    return storeMatch && holidayMatch;
  });
}

function populateFilters() {
  const stores = [...new Set(rawRows.map((row) => String(row.Store)).filter(Boolean))].sort((a, b) => Number(a) - Number(b));
  fields.storeFilter.innerHTML = `<option value="all">All stores</option>${stores
    .map((store) => `<option value="${store}">Store ${store}</option>`)
    .join("")}`;

  const availableGroups = ["Store", "Dept", "Product", "Category", "Region", "Type", "Customer_Segment"].filter((key) =>
    rawRows.some((row) => row[key] !== undefined && row[key] !== "")
  );
  fields.groupFilter.innerHTML = availableGroups.map((key) => `<option value="${key}">${key.replace("_", " ")}</option>`).join("");
}

function drawAxes(ctx, width, height, padding) {
  ctx.strokeStyle = "#d7dde5";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, padding);
  ctx.lineTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.stroke();
}

function clearCanvas(canvas) {
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  return ctx;
}

function drawLineChart(canvas, data) {
  const ctx = clearCanvas(canvas);
  const padding = 42;
  const width = canvas.width;
  const height = canvas.height;
  drawAxes(ctx, width, height, padding);
  if (data.length < 2) return;

  const max = Math.max(...data.map((item) => item.total));
  if (max <= 0) return;
  const stepX = (width - padding * 2) / (data.length - 1);

  ctx.strokeStyle = "#1565c0";
  ctx.lineWidth = 3;
  ctx.beginPath();
  data.forEach((item, index) => {
    const x = padding + index * stepX;
    const y = height - padding - (item.total / max) * (height - padding * 2);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.fillStyle = "#667085";
  ctx.font = "12px Arial";
  ctx.fillText(data[0].label, padding, height - 14);
  ctx.fillText(data[data.length - 1].label, width - padding - 48, height - 14);
  ctx.fillText(currency(max), padding + 4, padding - 12);
}

function drawBarChart(canvas, data, color) {
  const ctx = clearCanvas(canvas);
  const padding = 48;
  const width = canvas.width;
  const height = canvas.height;
  drawAxes(ctx, width, height, padding);
  const top = data.slice(0, 8);
  if (!top.length) return;

  const max = Math.max(...top.map((item) => item.total));
  if (max <= 0) return;
  const barGap = 10;
  const barHeight = (height - padding * 2 - barGap * (top.length - 1)) / top.length;

  ctx.font = "12px Arial";
  top.forEach((item, index) => {
    const y = padding + index * (barHeight + barGap);
    const barWidth = (item.total / max) * (width - padding * 2 - 90);
    ctx.fillStyle = color;
    ctx.fillRect(padding, y, barWidth, barHeight);
    ctx.fillStyle = "#17202a";
    ctx.fillText(String(item.label).slice(0, 16), padding + barWidth + 8, y + barHeight * 0.65);
  });
}

function renderTable(data) {
  const body = document.getElementById("topTable");
  body.innerHTML = data
    .slice(0, 10)
    .map(
      (item, index) => `
        <tr>
          <td>${index + 1}</td>
          <td>${item.label}</td>
          <td>${currency(item.total)}</td>
          <td>${currency(item.total / item.count)}</td>
        </tr>
      `
    )
    .join("");
}

function render() {
  const rows = filteredRows();
  const totalSales = rows.reduce((sum, row) => sum + (Number(row.Revenue ?? row.Weekly_Sales) || 0), 0);
  const holidaySales = rows
    .filter((row) => Number(row.Holiday_Flag || 0) === 1)
    .reduce((sum, row) => sum + (Number(row.Revenue ?? row.Weekly_Sales) || 0), 0);

  metrics.totalSales.textContent = currency(totalSales);
  metrics.avgSales.textContent = currency(totalSales / Math.max(rows.length, 1));
  metrics.storeCount.textContent = new Set(rows.map((row) => row.Store)).size;
  metrics.holidayShare.textContent = percent(holidaySales / Math.max(totalSales, 1));

  const trend = sumBy(
    rows.map((row) => ({ ...row, Month: monthKey(row.Date) })),
    "Month"
  ).sort((a, b) => String(a.label).localeCompare(String(b.label)));
  const grouped = sumBy(rows, fields.groupFilter.value);
  const holiday = sumBy(
    rows.map((row) => ({ ...row, Holiday: Number(row.Holiday_Flag || 0) === 1 ? "Holiday" : "Standard" })),
    "Holiday"
  );

  drawLineChart(document.getElementById("trendChart"), trend);
  drawBarChart(document.getElementById("barChart"), grouped, "#2e7d32");
  drawBarChart(document.getElementById("holidayChart"), holiday, "#b26a00");
  renderTable(grouped);
}

async function loadSample() {
  const response = await fetch(samplePath);
  const text = await response.text();
  rawRows = parseCsv(text);
  populateFilters();
  render();
}

fields.csvInput.addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  rawRows = parseCsv(await file.text());
  populateFilters();
  render();
});

[fields.storeFilter, fields.holidayFilter, fields.groupFilter].forEach((control) => {
  control.addEventListener("change", render);
});

loadSample().catch(() => {
  document.body.insertAdjacentHTML(
    "afterbegin",
    '<p style="padding:12px;margin:0;background:#fff3cd;color:#664d03">Run a local server from the project root or use Load CSV to open your Walmart dataset.</p>'
  );
});
