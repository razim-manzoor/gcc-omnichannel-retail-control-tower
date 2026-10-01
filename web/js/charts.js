/**
 * GCC Omnichannel Retail Control Tower - Charting & Visual Rendering Engine
 * Clustered Bar/Line Sensitivity Engine & 2D Inventory Health Diagnostic Matrix (SVG)
 */

export function renderSensitivityChart(data) {
  const svg = document.getElementById('sim-chart-svg');
  if (!svg) return;

  const chartWidth = 700;
  const chartHeight = 160;
  const startX = 50;
  const startY = 15;
  
  const maxVal = Math.max(...data.map(d => Math.max(d.baselineGM, d.simGM, d.capReleased)));
  const groupWidth = (chartWidth - startX) / data.length;
  const barWidth = groupWidth * 0.28;

  let html = `
    <line x1="${startX}" y1="${startY}" x2="${chartWidth}" y2="${startY}" stroke="#F1F5F9" stroke-width="1" />
    <line x1="${startX}" y1="${startY + chartHeight/2}" x2="${chartWidth}" y2="${startY + chartHeight/2}" stroke="#F1F5F9" stroke-width="1" />
    <line x1="${startX}" y1="${startY + chartHeight}" x2="${chartWidth}" y2="${startY + chartHeight}" stroke="#CBD5E1" stroke-width="1.2" />
    <text x="15" y="${startY + 10}" fill="#94A3B8" font-size="9">${Math.round(maxVal/1000)}k</text>
    <text x="15" y="${startY + chartHeight/2 + 4}" fill="#94A3B8" font-size="9">${Math.round(maxVal/2000)}k</text>
    <text x="15" y="${startY + chartHeight}" fill="#94A3B8" font-size="9">0</text>
  `;

  let linePoints = [];

  data.forEach((d, idx) => {
    const gx = startX + idx * groupWidth + 15;
    const hBase = (d.baselineGM / maxVal) * chartHeight;
    const hSim = (d.simGM / maxVal) * chartHeight;
    const hCap = (d.capReleased / maxVal) * chartHeight;

    const yBase = startY + chartHeight - hBase;
    const ySim = startY + chartHeight - hSim;
    const yCap = startY + chartHeight - hCap;

    html += `<rect x="${gx}" y="${yBase}" width="${barWidth}" height="${hBase}" fill="#0F172A" rx="2" class="transition-all duration-300">
               <title>${d.subcat} Baseline GM: AED ${Math.round(d.baselineGM).toLocaleString()}</title>
             </rect>`;
    
    html += `<rect x="${gx + barWidth + 3}" y="${ySim}" width="${barWidth}" height="${hSim}" fill="#2563EB" rx="2" class="transition-all duration-300">
               <title>${d.subcat} Simulated GM: AED ${Math.round(d.simGM).toLocaleString()}</title>
             </rect>`;

    const lineX = gx + barWidth + 1.5;
    linePoints.push(`${lineX},${yCap}`);

    html += `<text x="${gx + barWidth}" y="${startY + chartHeight + 14}" fill="#64748B" font-size="9" font-weight="600" text-anchor="middle">${d.subcat}</text>`;
  });

  if (linePoints.length > 0) {
    html += `<polyline fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-dasharray="2,2" points="${linePoints.join(' ')}" />`;
    linePoints.forEach(pt => {
      const [px, py] = pt.split(',');
      html += `<circle cx="${px}" cy="${py}" r="4" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.5">
                 <title>Capital Released</title>
               </circle>`;
    });
  }

  svg.innerHTML = html;
}

export function renderScatterPlot(filteredPositions, selectedSkuHighlight, onBubbleClick) {
  const g = document.getElementById('scatter-points-group');
  if (!g) return;

  let pointsHtml = '';

  filteredPositions.forEach((pos, idx) => {
    const boundedWos = Math.min(20, Math.max(0, pos.wos));
    const cx = 60 + (boundedWos / 20) * 980;
    const cy = 240 - (pos.str / 100) * 220;

    let fill = '#10B981';
    if (pos.status === 'CRITICAL_STOCKOUT_RISK') fill = '#EF4444';
    if (pos.status === 'OVERSTOCK_CASH_TRAP') fill = '#F59E0B';

    const radius = Math.min(18, Math.max(7, Math.sqrt(pos.onHand + 5) * 2.8));

    // Stagger labels for clean visual separation
    const isEven = idx % 2 === 0;
    let labelY = isEven ? (cy - radius - 5) : (cy + radius + 13);
    let textAnchor = "middle";
    let labelX = cx;

    if (labelY < 32) labelY = cy + radius + 13;
    if (labelY > 250) labelY = cy - radius - 5;
    if (cx < 100) { textAnchor = "start"; labelX = cx + radius + 3; }
    else if (cx > 980) { textAnchor = "end"; labelX = cx - radius - 3; }

    const isHighlighted = selectedSkuHighlight === pos.sku;
    const strokeWidth = isHighlighted ? 4 : 2;
    const strokeColor = isHighlighted ? '#1E3A8A' : '#FFFFFF';

    pointsHtml += `
      <g class="cursor-pointer transition-transform duration-200 hover:scale-125" 
         id="scatter-g-${pos.sku}"
         data-sku="${pos.sku}"
         data-store="${pos.storeCode}"
         data-str="${pos.str}"
         data-wos="${pos.wos}"
         data-onhand="${pos.onHand}"
         data-directive="${pos.directive.replace(/"/g, '&quot;')}">
        <circle cx="${cx}" cy="${cy}" r="${radius}" fill="${fill}" fill-opacity="${isHighlighted ? 1 : 0.85}" stroke="${strokeColor}" stroke-width="${strokeWidth}" class="shadow-sm" />
        <text x="${labelX}" y="${labelY}" fill="#0F172A" font-size="9" font-weight="700" text-anchor="${textAnchor}" class="svg-text-halo">${pos.storeCode.split('-')[1]} • ${pos.sku.split('-')[0]}</text>
      </g>
    `;
  });

  g.innerHTML = pointsHtml;

  // Attach event listeners cleanly
  g.querySelectorAll('g[data-sku]').forEach(elem => {
    elem.addEventListener('mouseenter', (e) => {
      const store = elem.getAttribute('data-store');
      const sku = elem.getAttribute('data-sku');
      const str = parseFloat(elem.getAttribute('data-str'));
      const wos = parseFloat(elem.getAttribute('data-wos'));
      const onHand = parseInt(elem.getAttribute('data-onhand'));
      const directive = elem.getAttribute('data-directive');
      showScatterTip(e, store, sku, str, wos, onHand, directive);
    });

    elem.addEventListener('mouseleave', () => {
      hideScatterTip();
    });

    elem.addEventListener('click', () => {
      const sku = elem.getAttribute('data-sku');
      if (typeof onBubbleClick === 'function') {
        onBubbleClick(sku);
      }
    });
  });
}

export function showScatterTip(e, store, sku, str, wos, onHand, directive) {
  const tooltip = document.getElementById('scatter-tooltip');
  const container = document.getElementById('scatter-container');
  if (!tooltip || !container) return;

  const rect = container.getBoundingClientRect();
  const x = e.clientX - rect.left + 15;
  const y = e.clientY - rect.top - 20;

  tooltip.innerHTML = `
    <div class="font-bold text-slate-200 border-b border-slate-700 pb-1 mb-1.5 flex items-center justify-between">
      <span>${store}</span>
      <span class="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-300">${sku}</span>
    </div>
    <div class="grid grid-cols-2 gap-2 text-[11px] mb-2">
      <span>Sell-Through: <strong class="text-white">${str}%</strong></span>
      <span>WOS Cover: <strong class="text-white">${wos.toFixed(1)} Wks</strong></span>
      <span>On-Hand: <strong class="text-white">${onHand} units</strong></span>
      <span>Directive: <strong class="${wos < 2 ? 'text-red-400' : wos > 8 ? 'text-amber-400' : 'text-emerald-400'}">${wos < 2 ? 'PULL' : wos > 8 ? 'PUSH' : 'HOLD'}</strong></span>
    </div>
    <div class="text-[10px] text-slate-300 italic border-t border-slate-800 pt-1 leading-snug">${directive}</div>
    <div class="text-[9px] text-slate-400 mt-1 font-semibold uppercase tracking-wider">👉 Click to drill down into Action Grid</div>
  `;
  tooltip.style.left = `${Math.min(x, 820)}px`;
  tooltip.style.top = `${Math.max(10, y)}px`;
  tooltip.classList.remove('hidden');
}

export function hideScatterTip() {
  const tooltip = document.getElementById('scatter-tooltip');
  if (tooltip) {
    tooltip.classList.add('hidden');
  }
}
