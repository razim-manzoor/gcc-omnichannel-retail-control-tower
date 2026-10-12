/**
 * GCC Omnichannel Retail Control Tower - Haute Horlogerie Action Grid Engine
 * High-Density Data Presentation, Monospace Numerals, Dynamic Directives, CSV Export, Interactive Transfer Dispatch
 */

/** Escapes HTML entities to prevent XSS when injecting data into innerHTML */
function escapeHtml(str) {
  if (typeof str !== 'string') return str;
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

export function renderTable(data, selectedSkuHighlight, sortColumn, sortAsc, onRowClick) {
  const tbody = document.getElementById('table-body');
  if (!tbody) return;

  const sortedData = [...data].sort((a, b) => {
    let vA = a[sortColumn];
    let vB = b[sortColumn];
    if (typeof vA === 'string') return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(a[sortColumn]);
    return sortAsc ? vA - vB : vB - vA;
  });

  let rows = '';
  sortedData.forEach(item => {
    let wosBadge = `<span class="px-2 py-0.5 rounded-md font-mono text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200/80">${item.wos.toFixed(1)} Wks</span>`;
    if (item.wos < 2.5) {
      wosBadge = `<span class="px-2 py-0.5 rounded-md font-mono text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200/80">${item.wos.toFixed(1)} Wks</span>`;
    } else if (item.wos > 8.0) {
      wosBadge = `<span class="px-2 py-0.5 rounded-md font-mono text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200/80">${item.wos.toFixed(1)} Wks</span>`;
    }

    const strBarWidth = Math.min(100, Math.max(4, item.str));
    const strBar = `
      <div class="flex items-center space-x-2">
        <span class="w-10 font-mono text-xs font-semibold text-slate-800">${item.str.toFixed(1)}%</span>
        <div class="flex-1 bg-slate-100 h-1.5 rounded-full overflow-hidden">
          <div class="bg-slate-700 h-full rounded-full" style="width: ${strBarWidth}%;"></div>
        </div>
      </div>
    `;

    let directiveBadge = '';
    if (item.status === 'CRITICAL_STOCKOUT_RISK') {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200 shrink-0 mr-1.5"><span class="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1"></span>PULL</span>`;
    } else if (item.status === 'OVERSTOCK_CASH_TRAP') {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 shrink-0 mr-1.5"><span class="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1"></span>PUSH</span>`;
    } else {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0 mr-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1"></span>OPTIMAL</span>`;
    }

    const cleanDirective = item.directive.replace(/[⚠️🚨📦✅🏷️]/g, '').trim();

    // Action button
    let actionBtn = '';
    if (item.isDispatched) {
      actionBtn = `<span class="inline-flex items-center text-[10px] font-bold font-mono px-2 py-1 rounded bg-slate-100 text-slate-600 border border-slate-200">✓ Dispatched</span>`;
    } else if (item.transferAction) {
      actionBtn = `
        <button class="dispatch-trigger-btn inline-flex items-center px-2.5 py-1 text-[11px] font-bold rounded-md bg-slate-900 hover:bg-blue-600 text-white transition shadow-2xs gap-1 cursor-pointer" onclick="event.stopPropagation(); window.openTransferDrawer('${item.sku}')">
          <span>⚡ Rebalance</span>
        </button>
      `;
    } else {
      actionBtn = `<span class="text-[11px] text-slate-400 font-medium">Cover Healthy</span>`;
    }

    const isSelected = selectedSkuHighlight === item.sku;
    const rowBg = isSelected ? "bg-blue-50/70 border-l-4 border-l-blue-600" : "hover:bg-slate-50/80";

    rows += `
      <tr id="row-${item.sku}" data-sku="${item.sku}" class="${rowBg} transition-all duration-150 border-b border-slate-100 cursor-pointer text-xs" onclick="window.openTransferDrawer('${item.sku}')">
        <td class="py-2.5 px-3">
          <div class="font-mono font-bold text-slate-900">${escapeHtml(item.sku)}</div>
          <div class="text-[11px] text-slate-500">${escapeHtml(item.prodName)}</div>
        </td>
        <td class="py-2.5 px-3">
          <div class="font-semibold text-slate-800">${escapeHtml(item.storeName)}</div>
          <div class="font-mono text-[10px] text-slate-400">${escapeHtml(item.storeCode)}</div>
        </td>
        <td class="py-2.5 px-3 text-right font-mono font-bold text-slate-900">${item.onHand}</td>
        <td class="py-2.5 px-3 text-right font-mono text-slate-600">${item.runRate.toFixed(2)}/wk</td>
        <td class="py-2.5 px-3">${strBar}</td>
        <td class="py-2.5 px-3 text-right">${wosBadge}</td>
        <td class="py-2.5 px-3 text-right font-mono font-bold text-slate-800">${item.gmroi.toFixed(2)}x</td>
        <td class="py-2.5 px-3 text-slate-700 max-w-sm">
          <div class="flex items-center">
            ${directiveBadge}
            <span class="text-[11px] font-medium leading-snug text-slate-600 truncate">${cleanDirective}</span>
          </div>
        </td>
        <td class="py-2.5 px-3 text-right">
          ${actionBtn}
        </td>
      </tr>
    `;
  });

  if (rows === '') {
    rows = `<tr><td colspan="9" class="text-center py-8 text-slate-400 text-xs">No SKU inventory positions matching active filters.</td></tr>`;
  }

  tbody.innerHTML = rows;
}

export function highlightFromRow(sku) {
  document.querySelectorAll('tr[data-sku]').forEach(r => {
    if (r.getAttribute('data-sku') === sku) {
      r.classList.add('bg-blue-50/70', 'border-l-4', 'border-l-blue-600');
    } else {
      r.classList.remove('bg-blue-50/70', 'border-l-4', 'border-l-blue-600');
    }
  });
}

export function exportCSV(data) {
  const headers = ['SKU', 'Product Name', 'Store Code', 'Store Name', 'On Hand Units', 'Weekly Run Rate', 'STR Pct', 'WOS Weeks', 'Safety Stock', 'Unit Cost AED', 'GMROI', 'Status', 'Directive'];
  const rows = data.map(item => [
    item.sku,
    `"${item.prodName.replace(/"/g, '""')}"`,
    item.storeCode,
    `"${item.storeName.replace(/"/g, '""')}"`,
    item.onHand,
    item.runRate,
    item.str,
    item.wos,
    item.targetSS,
    item.unitCost,
    item.gmroi,
    item.status,
    `"${item.directive.replace(/"/g, '""')}"`
  ]);

  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `GCC_Control_Tower_Rebalancing_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
