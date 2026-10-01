/**
 * GCC Omnichannel Retail Control Tower - Action Grid Table Engine
 * Cross-filtering, column sorting, dynamic inventory directive badges, and CSV export
 */

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
    let wosBadge = `<span class="px-2 py-0.5 rounded-full font-bold text-[11px] bg-emerald-50 text-emerald-700 border border-emerald-200">${item.wos.toFixed(1)} Wks</span>`;
    if (item.wos < 2.0) {
      wosBadge = `<span class="px-2 py-0.5 rounded-full font-bold text-[11px] bg-red-100 text-red-800 border border-red-300">${item.wos.toFixed(1)} Wks (LOW)</span>`;
    } else if (item.wos > 10.0) {
      wosBadge = `<span class="px-2 py-0.5 rounded-full font-bold text-[11px] bg-amber-100 text-amber-800 border border-amber-300">${item.wos.toFixed(1)} Wks (HIGH)</span>`;
    }

    const strBarWidth = Math.min(100, Math.max(4, item.str));
    const strBar = `
      <div class="flex items-center space-x-2">
        <span class="w-10 font-semibold text-[#0F172A]">${item.str.toFixed(1)}%</span>
        <div class="flex-1 bg-slate-100 h-2 rounded-full overflow-hidden">
          <div class="bg-slate-500 h-full rounded-full" style="width: ${strBarWidth}%;"></div>
        </div>
      </div>
    `;

    let directiveBadge = '';
    if (item.directive.includes('Stockout') || item.directive.includes('Urgent') || item.directive.includes('PULL')) {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200 mr-1.5 shrink-0">PULL</span>`;
    } else if (item.directive.includes('RESTOCK') || item.directive.includes('PRIORITY')) {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-900 border border-blue-200 mr-1.5 shrink-0">RESTOCK</span>`;
    } else if (item.directive.includes('OPTIMAL')) {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 mr-1.5 shrink-0">OPTIMAL</span>`;
    } else {
      directiveBadge = `<span class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 mr-1.5 shrink-0">REBALANCE</span>`;
    }

    const cleanDirective = item.directive.replace(/[⚠️🚨📦✅🏷️]/g, '').trim();

    const isSelected = selectedSkuHighlight === item.sku;
    const rowBg = isSelected ? "bg-blue-50/80" : "hover:bg-slate-50";

    rows += `
      <tr id="row-${item.sku}" data-sku="${item.sku}" class="${rowBg} transition border-b border-slate-100 cursor-pointer">
        <td class="py-2.5 px-3">
          <div class="font-bold text-[#0F172A]">${item.sku}</div>
          <div class="text-[11px] text-[#64748B]">${item.prodName}</div>
        </td>
        <td class="py-2.5 px-3">
          <div class="font-semibold text-[#0F172A]">${item.storeName}</div>
          <div class="text-[10px] text-slate-400">${item.storeCode}</div>
        </td>
        <td class="py-2.5 px-3">${strBar}</td>
        <td class="py-2.5 px-3">${wosBadge}</td>
        <td class="py-2.5 px-3 font-semibold text-[#0F172A]">${item.gmroi.toFixed(2)}x</td>
        <td class="py-2.5 px-3 text-right font-bold text-[#0F172A]">${item.onHand}</td>
        <td class="py-2.5 px-3 text-right text-[#64748B]">${item.targetSS}</td>
        <td class="py-2.5 px-3 text-right text-[#64748B]">AED ${item.unitCost}</td>
        <td class="py-2.5 px-3 text-[#334155]">
          <div class="flex items-center">
            ${directiveBadge}
            <span class="text-[11px] leading-tight font-medium text-slate-700">${cleanDirective}</span>
          </div>
        </td>
      </tr>
    `;
  });

  if (rows === '') {
    rows = `<tr><td colspan="9" class="text-center py-6 text-slate-400">No SKU inventory positions matching active filters.</td></tr>`;
  }

  tbody.innerHTML = rows;

  // Row click listeners
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
