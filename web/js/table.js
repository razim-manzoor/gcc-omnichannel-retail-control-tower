/**
 * GCC Omnichannel Retail Control Tower - Haute Horlogerie Action Grid Engine
 * High-Density Data Presentation, Monospace Numerals, Dynamic Directives, CSV Export
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
    if (item.wos < 2.0) {
      wosBadge = `<span class="px-2 py-0.5 rounded-md font-mono text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200/80">${item.wos.toFixed(1)} Wks</span>`;
    } else if (item.wos > 10.0) {
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
    if (item.directive.includes('Stockout') || item.directive.includes('Urgent') || item.directive.includes('PULL')) {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200 shrink-0 mr-1.5"><span class="w-1.5 h-1.5 rounded-full bg-rose-500 mr-1"></span>PULL</span>`;
    } else if (item.directive.includes('RESTOCK') || item.directive.includes('PRIORITY')) {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200 shrink-0 mr-1.5"><span class="w-1.5 h-1.5 rounded-full bg-blue-500 mr-1"></span>RESTOCK</span>`;
    } else if (item.directive.includes('OPTIMAL')) {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0 mr-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1"></span>OPTIMAL</span>`;
    } else {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 shrink-0 mr-1.5"><span class="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1"></span>REBALANCE</span>`;
    }

    const cleanDirective = item.directive.replace(/[⚠️🚨📦✅🏷️]/g, '').trim();

    const isSelected = selectedSkuHighlight === item.sku;
    const rowBg = isSelected ? "bg-blue-50/70 border-l-4 border-l-blue-600" : "hover:bg-slate-50/80";

    rows += `
      <tr id="row-${item.sku}" data-sku="${item.sku}" class="${rowBg} transition-all duration-150 border-b border-slate-100 cursor-pointer text-xs">
        <td class="py-2.5 px-3">
          <div class="font-mono font-bold text-slate-900">${escapeHtml(item.sku)}</div>
          <div class="text-[11px] text-slate-500">${escapeHtml(item.prodName)}</div>
        </td>
        <td class="py-2.5 px-3">
          <div class="font-semibold text-slate-800">${escapeHtml(item.storeName)}</div>
          <div class="font-mono text-[10px] text-slate-400">${escapeHtml(item.storeCode)}</div>
        </td>
        <td class="py-2.5 px-3">${strBar}</td>
        <td class="py-2.5 px-3">${wosBadge}</td>
        <td class="py-2.5 px-3 font-mono font-semibold text-slate-800">${item.gmroi.toFixed(2)}x</td>
        <td class="py-2.5 px-3 text-right font-mono font-bold text-slate-900">${item.onHand}</td>
        <td class="py-2.5 px-3 text-right font-mono text-slate-500">${item.targetSS}</td>
        <td class="py-2.5 px-3 text-right font-mono text-slate-600">AED ${item.unitCost}</td>
        <td class="py-2.5 px-3 text-slate-700 max-w-md">
          <div class="flex items-center">
            ${directiveBadge}
            <span class="text-[11px] font-medium leading-snug text-slate-600 truncate">${cleanDirective}</span>
          </div>
        </td>
      </tr>
    `;
  });

  if (rows === '') {
    rows = `<tr><td colspan="9" class="text-center py-8 text-slate-400 text-xs">No SKU inventory positions matching active filters.</td></tr>`;
  }

  tbody.innerHTML = rows;

  tbody.querySelectorAll('tr[data-sku]').forEach(tr => {
    tr.addEventListener('click', () => {
      const sku = tr.getAttribute('data-sku');
      if (typeof onRowClick === 'function') {
        onRowClick(sku);
      }
    });
  });
}

export function highlightFromRow(sku) {
  const circleGroup = document.getElementById(`scatter-g-${sku}`);
  if (circleGroup) {
    circleGroup.classList.add('scale-150');
    setTimeout(() => circleGroup.classList.remove('scale-150'), 1500);
  }
}

export function exportCSV(data) {
  let csv = 'SKU,ProductName,StoreCode,StoreName,SellThroughRatePct,WeeksOfSupply,GMROI,OnHandUnits,TargetSafetyStock,UnitCostAED,Directive\n';
  data.forEach(d => {
    csv += `"${d.sku}","${d.prodName}","${d.storeCode}","${d.storeName}",${d.str},${d.wos},${d.gmroi},${d.onHand},${d.targetSS},${d.unitCost},"${d.directive}"\n`;
  });
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'GCC_Control_Tower_Rebalance_Matrix.csv';
  a.click();
}
