/**
 * GCC Omnichannel Retail Control Tower - Haute Horlogerie Visual Charts Engine
 * Refined 2D Diagnostic Matrix (Zero-Collision Luxury Telemetry) & Sensitivity Chart
 */

/** Escapes HTML entities to prevent XSS */
function escapeHtml(str) {
  if (typeof str !== 'string') return str;
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

export function renderSensitivityChart(data) {
  const svg = document.getElementById('sim-chart-svg');
  if (!svg) return;

  const width = 640;
  const height = 185;
  const padLeft = 45;
  const padRight = 20;
  const padTop = 20;
  const padBottom = 32;
  
  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  const maxVal = Math.max(...data.map(d => Math.max(d.baselineGM, d.simGM, d.capReleased))) * 1.12;
  const groupW = chartW / data.length;
  const barW = Math.min(20, groupW * 0.32);

  let html = `
    <defs>
      <linearGradient id="grad-base-gm" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#334155" />
        <stop offset="100%" stop-color="#0F172A" />
      </linearGradient>
      <linearGradient id="grad-sim-gm" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#3B82F6" />
        <stop offset="100%" stop-color="#1D4ED8" />
      </linearGradient>
      <filter id="glow-amber" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#D97706" flood-opacity="0.3" />
      </filter>
    </defs>
  `;

  // Gridlines
  [0, 0.5, 1].forEach(ratio => {
    const y = padTop + chartH * (1 - ratio);
    const valK = Math.round((maxVal * ratio) / 1000);
    html += `
      <line x1="${padLeft}" y1="${y}" x2="${width - padRight}" y2="${y}" stroke="#F1F5F9" stroke-width="1" />
      <text x="${padLeft - 8}" y="${y + 3.5}" fill="#94A3B8" font-size="9" font-family="var(--font-mono)" text-anchor="end">${valK}k</text>
    `;
  });

  // Base axis line
  html += `<line x1="${padLeft}" y1="${padTop + chartH}" x2="${width - padRight}" y2="${padTop + chartH}" stroke="#E2E8F0" stroke-width="1.2" />`;

  let linePoints = [];

  data.forEach((d, idx) => {
    const cx = padLeft + idx * groupW + groupW / 2;
    const hBase = Math.max(4, (d.baselineGM / maxVal) * chartH);
    const hSim = Math.max(4, (d.simGM / maxVal) * chartH);
    const hCap = (d.capReleased / maxVal) * chartH;

    const yBase = padTop + chartH - hBase;
    const ySim = padTop + chartH - hSim;
    const yCap = padTop + chartH - hCap;

    const xBase = cx - barW - 2;
    const xSim = cx + 2;

    // Baseline bar
    html += `
      <rect x="${xBase}" y="${yBase}" width="${barW}" height="${hBase}" fill="url(#grad-base-gm)" rx="3" class="transition-all duration-300 hover:opacity-90 cursor-pointer">
        <title>${d.subcat} Baseline GM: AED ${Math.round(d.baselineGM).toLocaleString()}</title>
      </rect>
    `;

    // Simulated bar
    html += `
      <rect x="${xSim}" y="${ySim}" width="${barW}" height="${hSim}" fill="url(#grad-sim-gm)" rx="3" class="transition-all duration-300 hover:opacity-90 cursor-pointer">
        <title>${d.subcat} Simulated GM: AED ${Math.round(d.simGM).toLocaleString()}</title>
      </rect>
    `;

    linePoints.push({ x: cx, y: yCap, val: d.capReleased, subcat: d.subcat });

    // Category Label
    html += `
      <text x="${cx}" y="${padTop + chartH + 18}" fill="#64748B" font-size="9.5" font-weight="600" text-anchor="middle">
        ${d.subcat.split(' ')[0]}
      </text>
    `;
  });

  // Smooth bezier curve for Capital Released
  if (linePoints.length > 0) {
    let dPath = `M ${linePoints[0].x} ${linePoints[0].y}`;
    for (let i = 0; i < linePoints.length - 1; i++) {
      const p0 = linePoints[i];
      const p1 = linePoints[i + 1];
      const mx = (p0.x + p1.x) / 2;
      dPath += ` C ${mx} ${p0.y}, ${mx} ${p1.y}, ${p1.x} ${p1.y}`;
    }

    html += `<path d="${dPath}" fill="none" stroke="#D97706" stroke-width="2.5" stroke-linecap="round" />`;

    linePoints.forEach(pt => {
      html += `
        <circle cx="${pt.x}" cy="${pt.y}" r="4.5" fill="#D97706" stroke="#FFFFFF" stroke-width="2" class="cursor-pointer transition-transform hover:scale-150" filter="url(#glow-amber)">
          <title>${pt.subcat} Capital Released: AED ${Math.round(pt.val).toLocaleString()}</title>
        </circle>
      `;
    });
  }

  svg.innerHTML = html;
}

export function renderScatterPlot(filteredPositions, selectedSkuHighlight, onBubbleClick) {
  const g = document.getElementById('scatter-points-group');
  if (!g) return;

  const width = 760;
  const height = 280;
  const padLeft = 45;
  const padRight = 30;
  const padTop = 25;
  const padBottom = 35;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  let pointsHtml = '';

  filteredPositions.forEach((pos) => {
    const boundedWos = Math.min(20, Math.max(0, pos.wos));
    const cx = padLeft + (boundedWos / 20) * chartW;
    const cy = padTop + chartH - (pos.str / 100) * chartH;

    let fill = '#059669'; // Emerald
    let stroke = '#047857';
    let ringColor = 'rgba(5, 150, 105, 0.2)';

    if (pos.status === 'CRITICAL_STOCKOUT_RISK') {
      fill = '#E11D48'; // Rose
      stroke = '#BE123C';
      ringColor = 'rgba(225, 29, 72, 0.2)';
    } else if (pos.status === 'OVERSTOCK_CASH_TRAP') {
      fill = '#D97706'; // Amber
      stroke = '#B45309';
      ringColor = 'rgba(217, 119, 6, 0.2)';
    }

    const radius = Math.min(14, Math.max(8, Math.sqrt(pos.onHand + 4) * 2.2));
    const isSelected = selectedSkuHighlight === pos.sku;

    const storeShort = pos.storeCode.split('-')[1];
    const skuShort = pos.sku.split('-')[0];

    // Clutter-free labeling: Only display permanent labels on isolated points (> 6W cover)
    // or when the SKU is explicitly selected. All others reveal full details on hover!
    const isIsolated = pos.wos > 6.0;
    const showPermanentLabel = isIsolated || isSelected;

    let labelHtml = '';
    if (showPermanentLabel) {
      const labelY = cy - radius - 5;
      labelHtml = `
        <text x="${cx}" y="${labelY}" 
              fill="#1E293B" 
              font-size="9" 
              font-weight="700" 
              text-anchor="middle" 
              class="svg-text-halo select-none pointer-events-none">
          ${storeShort} • ${skuShort}
        </text>
      `;
    }

    pointsHtml += `
      <g class="scatter-node cursor-pointer" 
         id="scatter-g-${pos.sku}"
         data-sku="${pos.sku}"
         data-store="${pos.storeName}"
         data-storecode="${pos.storeCode}"
         data-str="${pos.str}"
         data-wos="${pos.wos}"
         data-onhand="${pos.onHand}"
         data-directive="${pos.directive.replace(/"/g, '&quot;')}">
        
        <!-- Outer pulse ring on hover/selected -->
        <circle cx="${cx}" cy="${cy}" r="${radius + 4}" fill="${ringColor}" class="transition-all duration-200 opacity-0 group-hover:opacity-100 ${isSelected ? 'opacity-100' : ''}" />
        
        <!-- Core Bubble -->
        <circle cx="${cx}" cy="${cy}" r="${radius}" 
                fill="${fill}" 
                fill-opacity="${isSelected ? 0.95 : 0.85}" 
                stroke="${isSelected ? '#0F172A' : '#FFFFFF'}" 
                stroke-width="${isSelected ? 3.5 : 2}" 
                style="filter: drop-shadow(0 2px 4px rgba(15, 23, 42, 0.12));" />
        
        ${labelHtml}
      </g>
    `;
  });

  g.innerHTML = pointsHtml;

  // Event delegation on parent container for hover and click
  g.onmouseover = null; g.onmouseout = null; g.onclick = null;
  g.addEventListener('mouseover', (e) => {
    const elem = e.target.closest('g[data-sku]');
    if (!elem) return;
    const store = elem.getAttribute('data-store');
    const storeCode = elem.getAttribute('data-storecode');
    const sku = elem.getAttribute('data-sku');
    const str = parseFloat(elem.getAttribute('data-str'));
    const wos = parseFloat(elem.getAttribute('data-wos'));
    const onHand = parseInt(elem.getAttribute('data-onhand'));
    const directive = elem.getAttribute('data-directive');
    showScatterTip(e, store, storeCode, sku, str, wos, onHand, directive);
  });

  g.addEventListener('mouseout', (e) => {
    const related = e.relatedTarget;
    if (!related || !g.contains(related)) hideScatterTip();
  });

  g.addEventListener('click', (e) => {
    const elem = e.target.closest('g[data-sku]');
    if (!elem) return;
    const sku = elem.getAttribute('data-sku');
    if (typeof onBubbleClick === 'function') {
      onBubbleClick(sku);
    }
  });
}

export function showScatterTip(e, store, storeCode, sku, str, wos, onHand, directive) {
  const tooltip = document.getElementById('scatter-tooltip');
  const container = document.getElementById('scatter-container');
  if (!tooltip || !container) return;

  const rect = container.getBoundingClientRect();
  const x = e.clientX - rect.left + 16;
  const y = e.clientY - rect.top - 20;

  let directiveBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">OPTIMAL</span>`;
  if (wos < 2.5) {
    directiveBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">STOCKOUT DEFICIT</span>`;
  } else if (wos > 6.0) {
    directiveBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">CASH TRAP</span>`;
  }

  tooltip.innerHTML = `
    <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 mb-2">
      <div>
        <div class="font-bold text-slate-900 text-xs">${escapeHtml(store)}</div>
        <div class="font-mono text-[10px] text-slate-400 font-semibold">${escapeHtml(storeCode)}</div>
      </div>
      <span class="font-mono text-[10px] bg-slate-100 px-2 py-0.5 rounded-md text-slate-700 font-bold border border-slate-200">${escapeHtml(sku)}</span>
    </div>
    <div class="grid grid-cols-2 gap-2 text-xs mb-2">
      <div class="bg-slate-50 p-1.5 rounded-lg border border-slate-100">
        <span class="text-[10px] text-slate-400 uppercase block font-semibold">Sell-Through</span>
        <strong class="text-slate-900 font-mono font-bold">${str.toFixed(1)}%</strong>
      </div>
      <div class="bg-slate-50 p-1.5 rounded-lg border border-slate-100">
        <span class="text-[10px] text-slate-400 uppercase block font-semibold">Cover</span>
        <strong class="text-slate-900 font-mono font-bold">${wos.toFixed(1)} Wks</strong>
      </div>
    </div>
    <div class="flex items-center justify-between text-xs py-1">
      <span class="text-slate-500 font-medium">On-Hand: <strong class="text-slate-900 font-mono font-bold">${onHand} units</strong></span>
      ${directiveBadge}
    </div>
    <div class="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-100 mt-1 leading-snug">
      ${directive}
    </div>
    <div class="text-[9px] text-slate-400 mt-1.5 font-bold text-center uppercase tracking-wider">
      Click to isolate & scroll to row in Action Grid
    </div>
  `;

  tooltip.style.left = `${Math.min(x, rect.width - 250)}px`;
  tooltip.style.top = `${Math.max(10, Math.min(y, rect.height - 200))}px`;
  tooltip.classList.remove('hidden');
}

export function hideScatterTip() {
  const tooltip = document.getElementById('scatter-tooltip');
  if (tooltip) {
    tooltip.classList.add('hidden');
  }
}
