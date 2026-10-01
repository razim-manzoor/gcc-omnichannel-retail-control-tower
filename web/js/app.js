/**
 * GCC Omnichannel Retail Control Tower - Master Application Coordinator
 * Fluid Responsive Orchestrator linking State, Simulation, Visuals, and DOM Event Streams
 */

import { rawProducts, rawStores, initialInventoryPositions } from './data.js';
import { recalculateSimulation } from './simulation.js';
import { renderSensitivityChart, renderScatterPlot } from './charts.js';
import { renderTable, highlightFromRow, exportCSV } from './table.js';

// --- Global Application State ---
export const state = {
  currentQuarter: 'All',
  currentChannel: 'All',
  currentDept: 'All',
  currentDiscountPct: 0.10,
  currentStatusChip: 'All',
  sortColumn: 'wos',
  sortAsc: true,
  selectedSkuHighlight: null,
  inventoryPositions: [...initialInventoryPositions]
};

// --- Viewport & Modal Orchestration ---
export function toggleFullScreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {});
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen().catch(() => {});
    }
  }
}

export function toggleModal(show) {
  const modal = document.getElementById('briefing-modal');
  if (!modal) return;
  if (show) {
    modal.classList.remove('hidden');
  } else {
    modal.classList.add('hidden');
  }
}

// --- Filtering & Queries ---
export function getFilteredPositions() {
  const searchInput = document.getElementById('grid-search');
  const search = (searchInput ? searchInput.value : '').toLowerCase();

  return state.inventoryPositions.filter(pos => {
    if (state.currentChannel !== 'All') {
      const store = rawStores.find(s => s.code === pos.storeCode);
      if (store && store.channel !== state.currentChannel) return false;
    }
    if (state.currentDept !== 'All' && pos.dept !== state.currentDept) return false;
    if (state.currentStatusChip !== 'All' && pos.status !== state.currentStatusChip) return false;
    if (search) {
      const hay = `${pos.sku} ${pos.prodName} ${pos.storeName} ${pos.directive}`.toLowerCase();
      if (!hay.includes(search)) return false;
    }
    return true;
  });
}

export function applyGlobalFilters() {
  const channelElem = document.getElementById('channel-filter');
  const deptElem = document.getElementById('dept-filter');
  if (channelElem) state.currentChannel = channelElem.value;
  if (deptElem) state.currentDept = deptElem.value;

  const revElem = document.getElementById('kpi-net-revenue');
  const gmElem = document.getElementById('kpi-gross-margin');
  const gmroiElem = document.getElementById('kpi-gmroi');
  const wosElem = document.getElementById('kpi-wos');

  if (state.currentDept === 'Apparel') {
    if (revElem) revElem.innerText = '6,420,100 AED';
    if (gmElem) gmElem.innerText = '58.2%';
    if (gmroiElem) gmroiElem.innerText = '3.85x';
    if (wosElem) wosElem.innerText = '5.1 Wks';
  } else if (state.currentDept === 'Footwear') {
    if (revElem) revElem.innerText = '2,890,500 AED';
    if (gmElem) gmElem.innerText = '62.0%';
    if (gmroiElem) gmroiElem.innerText = '4.10x';
    if (wosElem) wosElem.innerText = '2.4 Wks';
  } else {
    if (revElem) revElem.innerText = '24,820,400 AED';
    if (gmElem) gmElem.innerText = '69.7%';
    if (gmroiElem) gmroiElem.innerText = '3.42x';
    if (wosElem) wosElem.innerText = '4.8 Wks';
  }

  updateAllVisuals();
}

export function setQuarter(q, btn) {
  state.currentQuarter = q;
  document.querySelectorAll('.quarter-btn').forEach(b => {
    b.className = "quarter-btn px-2.5 py-1 text-xs font-semibold rounded text-slate-600 hover:text-slate-900 transition";
  });
  if (btn) {
    btn.className = "quarter-btn px-2.5 py-1 text-xs font-semibold rounded bg-white text-slate-900 shadow-xs border border-slate-200";
  }
  applyGlobalFilters();
}

export function setStatusChip(status, btn) {
  state.currentStatusChip = status;
  document.querySelectorAll('.status-chip').forEach(b => {
    b.className = "status-chip px-3 py-1 rounded-lg text-xs font-medium bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100 transition cursor-pointer flex items-center";
  });
  if (btn) {
    btn.className = "status-chip px-3 py-1 rounded-lg text-xs font-semibold bg-slate-900 text-white transition cursor-pointer shadow-xs flex items-center";
  }
  updateAllVisuals();
}

export function resetFilters() {
  state.currentQuarter = 'All';
  state.currentChannel = 'All';
  state.currentDept = 'All';
  state.currentStatusChip = 'All';
  state.selectedSkuHighlight = null;
  state.currentDiscountPct = 0.25;

  const channelFilter = document.getElementById('channel-filter');
  const deptFilter = document.getElementById('dept-filter');
  const searchInput = document.getElementById('grid-search');
  const discountSlider = document.getElementById('discount-slider');

  if (channelFilter) channelFilter.value = 'All';
  if (deptFilter) deptFilter.value = 'All';
  if (searchInput) searchInput.value = '';
  if (discountSlider) discountSlider.value = '25';

  document.querySelectorAll('.quarter-btn').forEach((b, idx) => {
    b.className = idx === 0 
      ? "quarter-btn px-2.5 py-1 text-xs font-semibold rounded bg-white text-slate-900 shadow-xs border border-slate-200" 
      : "quarter-btn px-2.5 py-1 text-xs font-semibold rounded text-slate-600 hover:text-slate-900 transition";
  });

  document.querySelectorAll('.status-chip').forEach((b, idx) => {
    b.className = idx === 0
      ? "status-chip px-3 py-1 rounded-lg text-xs font-semibold bg-slate-900 text-white transition cursor-pointer shadow-xs"
      : "status-chip px-3 py-1 rounded-lg text-xs font-medium bg-slate-50 text-slate-600 hover:text-slate-900 border border-slate-200 transition cursor-pointer";
  });

  applyGlobalFilters();
}

// --- Interaction Handlers ---
export function handleSliderChange(val) {
  state.currentDiscountPct = parseFloat(val) / 100;
  recalculateSimulation(state.currentDiscountPct, rawProducts, renderSensitivityChart);
}

export function drilldownToSku(sku) {
  state.selectedSkuHighlight = sku;
  const searchInput = document.getElementById('grid-search');
  if (searchInput) {
    searchInput.value = sku;
  }
  updateAllVisuals();

  const targetRow = document.getElementById(`row-${sku}`);
  if (targetRow) {
    targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
    targetRow.classList.add('row-highlight');
    setTimeout(() => targetRow.classList.remove('row-highlight'), 2500);
  }
}

export function handleRowClick(sku) {
  state.selectedSkuHighlight = sku;
  renderScatterPlot(getFilteredPositions(), state.selectedSkuHighlight, drilldownToSku);
  highlightFromRow(sku);
}

export function sortTable(col) {
  if (state.sortColumn === col) {
    state.sortAsc = !state.sortAsc;
  } else {
    state.sortColumn = col;
    state.sortAsc = true;
  }
  renderTable(getFilteredPositions(), state.selectedSkuHighlight, state.sortColumn, state.sortAsc, handleRowClick);
}

export function handleExportCSV() {
  exportCSV(getFilteredPositions());
}

export function simulateTransfer() {
  const banner = document.getElementById('banner-text');
  if (banner) {
    banner.innerHTML = `<strong class="text-blue-900">SIMULATION ACTIVE:</strong> 450 units re-routed from Yas Mall to Dubai Mall. Projected Stockout Risk reduced to 0.0%; Projected Dubai Mall STR sustained at 78.5%.`;
  }
  
  const kpiWos = document.getElementById('kpi-wos');
  if (kpiWos) kpiWos.innerText = '4.2 Wks';
  
  const wosBadge = document.getElementById('wos-badge-status');
  if (wosBadge) {
    wosBadge.className = 'px-2 py-0.5 text-[10px] font-bold bg-emerald-50 text-emerald-700 rounded border border-emerald-200';
    wosBadge.innerText = 'Optimal';
  }

  const wosBar = document.getElementById('wos-progress-bar');
  if (wosBar) {
    wosBar.className = 'bg-emerald-500 h-full rounded-full transition-all duration-500';
    wosBar.style.width = '42%';
  }

  const badge = document.getElementById('sim-verdict-badge');
  if (badge) {
    badge.className = "px-2.5 py-1 text-xs font-bold rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center";
    badge.innerHTML = `<span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span> REBALANCING OPTIMAL: Zero lost revenue`;
  }
}

export function approveTransfer() {
  alert("✅ Inter-Mall Stock Transfer #TR-2026-DXB-0450 APPROVED.\n\nDispatching 450 units from Yas Mall Logistics Hub to The Dubai Mall Flagship via GCC Express Logistics.\nERP Transfer Order Created in Dynamics 365.");
}

export function updateAllVisuals() {
  const filtered = getFilteredPositions();
  renderScatterPlot(filtered, state.selectedSkuHighlight, drilldownToSku);
  recalculateSimulation(state.currentDiscountPct, rawProducts, renderSensitivityChart);
  renderTable(filtered, state.selectedSkuHighlight, state.sortColumn, state.sortAsc, handleRowClick);
}

// Bind to window for HTML event handlers
window.toggleFullScreen = toggleFullScreen;
window.toggleModal = toggleModal;
window.setQuarter = setQuarter;
window.setStatusChip = setStatusChip;
window.applyGlobalFilters = applyGlobalFilters;
window.resetFilters = resetFilters;
window.handleSliderChange = handleSliderChange;
window.drilldownToSku = drilldownToSku;
window.highlightFromRow = handleRowClick;
window.sortTable = sortTable;
window.simulateTransfer = simulateTransfer;
window.approveTransfer = approveTransfer;
window.exportCSV = handleExportCSV;

// Initialization
window.addEventListener('DOMContentLoaded', () => {
  updateAllVisuals();
  
  const searchInput = document.getElementById('grid-search');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      updateAllVisuals();
    });
  }
});
