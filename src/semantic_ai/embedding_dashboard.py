from html import escape
import json
from pathlib import Path

import pandas as pd


TEXT_COLUMNS = ["label", "district", "pressureLevel"]
NUMERIC_COLUMNS = [
    "listingCount",
    "hutCount",
    "incomeEur",
    "tourismAssetScore",
    "hutListingRatio",
    "bedsPerHut",
    "kmeansCluster",
    "hierarchicalCluster",
    "pca1",
    "pca2",
]
DASHBOARD_COLUMNS = TEXT_COLUMNS + NUMERIC_COLUMNS


def dashboard_records(df: pd.DataFrame) -> list[dict]:
    data = df.copy()
    for column in TEXT_COLUMNS:
        if column not in data:
            data[column] = ""
        data[column] = data[column].fillna("").astype(str).map(escape)
    for column in NUMERIC_COLUMNS:
        if column not in data:
            data[column] = 0
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)

    data = data[DASHBOARD_COLUMNS].sort_values(["kmeansCluster", "district", "label"])
    return data.to_dict(orient="records")


def build_dashboard_html(df: pd.DataFrame) -> str:
    records = dashboard_records(df)
    data_json = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>KG Embedding Clusters Dashboard</title>
  <style>
    :root {{
      --bg: #f7f8fa;
      --panel: #ffffff;
      --text: #20242a;
      --muted: #5f6b7a;
      --border: #d9dee7;
      --accent: #1769aa;
      --accent-soft: #e8f2fb;
      --shadow: 0 1px 3px rgba(32, 36, 42, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}
    header {{
      padding: 24px 32px 16px;
      border-bottom: 1px solid var(--border);
      background: var(--panel);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      font-weight: 700;
    }}
    .subtitle {{
      max-width: 920px;
      color: var(--muted);
      margin: 0;
      font-size: 15px;
    }}
    main {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 20px;
      padding: 20px 32px 32px;
    }}
    section, aside {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    .visual-panel {{
      min-width: 0;
    }}
    .toolbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 16px;
      border-bottom: 1px solid var(--border);
    }}
    .toolbar h2, aside h2, .table-panel h2 {{
      margin: 0;
      font-size: 18px;
    }}
    label {{
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }}
    select {{
      min-width: 190px;
      margin-left: 8px;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fff;
      color: var(--text);
    }}
    .chart-wrap {{
      padding: 16px;
      overflow: hidden;
    }}
    svg {{
      display: block;
      width: 100%;
      height: 520px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fbfcfe;
    }}
    .axis {{
      stroke: #aab3bf;
      stroke-width: 1;
    }}
    .axis-label {{
      fill: var(--muted);
      font-size: 12px;
    }}
    circle {{
      stroke: #ffffff;
      stroke-width: 2;
      cursor: pointer;
    }}
    circle:hover, circle.active {{
      stroke: #111827;
      stroke-width: 3;
    }}
    aside {{
      padding: 16px;
      align-self: start;
    }}
    .detail-title {{
      margin: 12px 0 4px;
      font-size: 22px;
    }}
    .detail-meta {{
      margin: 0 0 14px;
      color: var(--muted);
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 18px;
    }}
    .metric {{
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 10px;
      background: #fbfcfe;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    .metric strong {{
      display: block;
      margin-top: 4px;
      font-size: 17px;
    }}
    .legend, #cluster-summary {{
      display: grid;
      gap: 8px;
      margin-top: 12px;
    }}
    .legend-item, .summary-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fbfcfe;
      font-size: 13px;
    }}
    .swatch {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 8px;
      vertical-align: middle;
    }}
    .table-panel {{
      grid-column: 1 / -1;
      padding: 16px;
    }}
    .table-scroll {{
      overflow-x: auto;
      margin-top: 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 980px;
      background: #fff;
    }}
    th, td {{
      padding: 9px 10px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      font-size: 13px;
      white-space: nowrap;
    }}
    th {{
      background: var(--accent-soft);
      color: #153b59;
      font-weight: 700;
    }}
    tr:hover td {{
      background: #f4f8fc;
    }}
    @media (max-width: 980px) {{
      header, main {{
        padding-left: 16px;
        padding-right: 16px;
      }}
      main {{
        grid-template-columns: 1fr;
      }}
      svg {{
        height: 420px;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>KG Embedding Clusters Dashboard</h1>
    <p class="subtitle">Visual inspection of the graph-derived neighborhood embeddings. Each point is a Barcelona neighborhood projected with PCA; colors can switch between KMeans and Agglomerative clustering.</p>
  </header>
  <main>
    <section class="visual-panel" aria-labelledby="scatter-title">
      <div class="toolbar">
        <h2 id="scatter-title">PCA scatter</h2>
        <label for="cluster-method">Cluster method
          <select id="cluster-method">
            <option value="kmeansCluster">KMeans</option>
            <option value="hierarchicalCluster">Agglomerative</option>
          </select>
        </label>
      </div>
      <div class="chart-wrap">
        <svg id="scatter" role="img" aria-label="PCA scatter plot of neighborhood embeddings"></svg>
      </div>
    </section>

    <aside>
      <h2>Selected neighborhood</h2>
      <div id="detail"></div>
      <h2>Cluster summary</h2>
      <div id="cluster-summary"></div>
      <h2 style="margin-top: 18px;">Legend</h2>
      <div id="legend" class="legend"></div>
    </aside>

    <section class="table-panel" aria-labelledby="table-title">
      <h2 id="table-title">Neighborhood values</h2>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Neighborhood</th>
              <th>District</th>
              <th>Pressure</th>
              <th>KMeans</th>
              <th>Agglomerative</th>
              <th>Listings</th>
              <th>HUT licenses</th>
              <th>HUT/listing</th>
              <th>Beds/HUT</th>
              <th>Income</th>
              <th>Tourism assets</th>
            </tr>
          </thead>
          <tbody id="values-table"></tbody>
        </table>
      </div>
    </section>
  </main>

  <script type="application/json" id="embedding-data">{data_json}</script>
  <script>
    const data = JSON.parse(document.getElementById("embedding-data").textContent);
    const colors = ["#1769aa", "#c43e1c", "#2f855a", "#805ad5", "#b7791f", "#2c7a7b", "#b83280", "#4a5568"];
    const svg = document.getElementById("scatter");
    const methodSelect = document.getElementById("cluster-method");
    const detail = document.getElementById("detail");
    const summary = document.getElementById("cluster-summary");
    const legend = document.getElementById("legend");
    const valuesTable = document.getElementById("values-table");
    let selectedIndex = 0;

    function fmt(value, digits = 0) {{
      const number = Number(value);
      if (!Number.isFinite(number)) return "-";
      return number.toLocaleString("en-US", {{ maximumFractionDigits: digits, minimumFractionDigits: digits }});
    }}

    function clusterColor(cluster) {{
      const index = Math.abs(Number(cluster) || 0) % colors.length;
      return colors[index];
    }}

    function extent(values) {{
      const nums = values.map(Number).filter(Number.isFinite);
      let min = Math.min(...nums);
      let max = Math.max(...nums);
      if (min === max) {{
        min -= 1;
        max += 1;
      }}
      return [min, max];
    }}

    function scale(value, sourceMin, sourceMax, targetMin, targetMax) {{
      return targetMin + ((Number(value) - sourceMin) / (sourceMax - sourceMin)) * (targetMax - targetMin);
    }}

    function renderScatter() {{
      const method = methodSelect.value;
      const width = svg.clientWidth || 900;
      const height = svg.clientHeight || 520;
      const pad = 54;
      const [xMin, xMax] = extent(data.map((d) => d.pca1));
      const [yMin, yMax] = extent(data.map((d) => d.pca2));
      svg.setAttribute("viewBox", `0 0 ${{width}} ${{height}}`);
      svg.innerHTML = "";

      const xAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
      xAxis.setAttribute("x1", pad);
      xAxis.setAttribute("x2", width - pad);
      xAxis.setAttribute("y1", height - pad);
      xAxis.setAttribute("y2", height - pad);
      xAxis.setAttribute("class", "axis");
      svg.appendChild(xAxis);

      const yAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
      yAxis.setAttribute("x1", pad);
      yAxis.setAttribute("x2", pad);
      yAxis.setAttribute("y1", pad);
      yAxis.setAttribute("y2", height - pad);
      yAxis.setAttribute("class", "axis");
      svg.appendChild(yAxis);

      const xLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
      xLabel.setAttribute("x", width / 2);
      xLabel.setAttribute("y", height - 16);
      xLabel.setAttribute("text-anchor", "middle");
      xLabel.setAttribute("class", "axis-label");
      xLabel.textContent = "PCA 1";
      svg.appendChild(xLabel);

      const yLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
      yLabel.setAttribute("x", 18);
      yLabel.setAttribute("y", height / 2);
      yLabel.setAttribute("transform", `rotate(-90 18 ${{height / 2}})`);
      yLabel.setAttribute("text-anchor", "middle");
      yLabel.setAttribute("class", "axis-label");
      yLabel.textContent = "PCA 2";
      svg.appendChild(yLabel);

      data.forEach((d, index) => {{
        const x = scale(d.pca1, xMin, xMax, pad, width - pad);
        const y = scale(d.pca2, yMin, yMax, height - pad, pad);
        const r = Math.max(5, Math.min(15, 5 + Math.sqrt(Number(d.listingCount) || 0) / 4));
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", x);
        circle.setAttribute("cy", y);
        circle.setAttribute("r", r);
        circle.setAttribute("fill", clusterColor(d[method]));
        circle.setAttribute("data-index", index);
        circle.classList.toggle("active", index === selectedIndex);
        circle.addEventListener("click", () => {{
          selectedIndex = index;
          renderAll();
        }});
        const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
        title.textContent = `${{d.label}} | cluster ${{d[method]}} | listings ${{fmt(d.listingCount)}}`;
        circle.appendChild(title);
        svg.appendChild(circle);
      }});
    }}

    function renderDetail() {{
      const d = data[selectedIndex] || data[0];
      if (!d) {{
        detail.innerHTML = "<p>No data available.</p>";
        return;
      }}
      detail.innerHTML = `
        <h3 class="detail-title">${{d.label}}</h3>
        <p class="detail-meta">${{d.district}} | pressure: ${{d.pressureLevel || "-"}}</p>
        <div class="metric-grid">
          <div class="metric"><span>Listings</span><strong>${{fmt(d.listingCount)}}</strong></div>
          <div class="metric"><span>HUT licenses</span><strong>${{fmt(d.hutCount)}}</strong></div>
          <div class="metric"><span>HUT/listing</span><strong>${{fmt(d.hutListingRatio, 2)}}</strong></div>
          <div class="metric"><span>Beds/HUT</span><strong>${{fmt(d.bedsPerHut, 2)}}</strong></div>
          <div class="metric"><span>Income</span><strong>${{fmt(d.incomeEur)}} EUR</strong></div>
          <div class="metric"><span>Tourism assets</span><strong>${{fmt(d.tourismAssetScore, 1)}}</strong></div>
        </div>`;
    }}

    function renderSummary() {{
      const method = methodSelect.value;
      const groups = new Map();
      data.forEach((d) => {{
        const key = String(d[method]);
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(d);
      }});
      summary.innerHTML = Array.from(groups.entries())
        .sort((a, b) => Number(a[0]) - Number(b[0]))
        .map(([cluster, rows]) => {{
          const listings = rows.reduce((sum, d) => sum + Number(d.listingCount || 0), 0);
          const huts = rows.reduce((sum, d) => sum + Number(d.hutCount || 0), 0);
          return `<div class="summary-row"><span><span class="swatch" style="background:${{clusterColor(cluster)}}"></span>Cluster ${{cluster}}</span><strong>${{rows.length}} neighborhoods | ${{fmt(listings)}} listings | ${{fmt(huts)}} HUTs</strong></div>`;
        }})
        .join("");
    }}

    function renderLegend() {{
      const method = methodSelect.value;
      const clusters = Array.from(new Set(data.map((d) => String(d[method])))).sort((a, b) => Number(a) - Number(b));
      legend.innerHTML = clusters
        .map((cluster) => `<div class="legend-item"><span><span class="swatch" style="background:${{clusterColor(cluster)}}"></span>Cluster ${{cluster}}</span></div>`)
        .join("");
    }}

    function renderTable() {{
      valuesTable.innerHTML = data
        .map((d, index) => `
          <tr data-index="${{index}}">
            <td>${{d.label}}</td>
            <td>${{d.district}}</td>
            <td>${{d.pressureLevel || "-"}}</td>
            <td>${{d.kmeansCluster}}</td>
            <td>${{d.hierarchicalCluster}}</td>
            <td>${{fmt(d.listingCount)}}</td>
            <td>${{fmt(d.hutCount)}}</td>
            <td>${{fmt(d.hutListingRatio, 2)}}</td>
            <td>${{fmt(d.bedsPerHut, 2)}}</td>
            <td>${{fmt(d.incomeEur)}}</td>
            <td>${{fmt(d.tourismAssetScore, 1)}}</td>
          </tr>`)
        .join("");
      valuesTable.querySelectorAll("tr").forEach((row) => {{
        row.addEventListener("click", () => {{
          selectedIndex = Number(row.getAttribute("data-index"));
          renderAll();
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }});
      }});
    }}

    function renderAll() {{
      renderScatter();
      renderDetail();
      renderSummary();
      renderLegend();
      renderTable();
    }}

    methodSelect.addEventListener("change", renderAll);
    window.addEventListener("resize", renderScatter);
    renderAll();
  </script>
</body>
</html>
"""


def build_embedding_dashboard(csv_path: Path, out_path: Path) -> Path:
    df = pd.read_csv(csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_dashboard_html(df), encoding="utf-8")
    return out_path
