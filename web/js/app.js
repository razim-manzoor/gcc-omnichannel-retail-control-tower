/**
 * GCC Omnichannel Retail Control Tower - Master Application Coordinator
 * Fluid Responsive Orchestrator linking State, Simulation, Visuals, and DOM Event Streams
 */

import { rawProducts, rawStores, initialInventoryPositions, weeklyPacingData, channelBreakdownData, paymentTypeData } from './data.js';
import { recalculateSimulation } from './simulation.js';
import { renderSensitivityChart, renderScatterPlot, renderRetailPacingChart, renderChannelMixChart } from './charts.js';
import { renderTable, highlightFromRow, exportCSV } from './table.js';

// --- Global Application State ---
export const state = {
  currentQuarter: 'All',
  currentChannel: 'All',
  currentDept: 'All',
  currentDiscountPct: 0.15,
  currentStatusChip: 'All',
  sortColumn: 'wos',
  sortAsc: true,
  selectedSkuHighlight: null,
  activeTransferSku: null,
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

// --- Slide-Out Logistics Transfer Dispatch Drawer ---
export function openTransferDrawer(sku) {
  const item = state.inventoryPositions.find(p => p.sku === sku);
  if (!item) return;

  state.activeTransferSku = sku;
  const drawer = document.getElementById('transfer-drawer');
  const backdrop = document.getElementById('drawer-backdrop');
  if (!drawer) return;

  // Populate drawer fields
  const skuCode = document.getElementById('drawer-sku-code');
  const prodName = document.getElementById('drawer-prod-name');
  const fromNode = document.getElementById('drawer-from-node');
  const toNode = document.getElementById('drawer-to-node');
  const qtyInput = document.getElementById('drawer-transfer-qty');
  const freightVal = document.getElementById('drawer-freight-val');
  const revProtectedVal = document.getElementById('drawer-rev-val');
  const capReleasedVal = document.getElementById('drawer-cap-val');
  const transitVal = document.getElementById('drawer-transit-val');
  const statusBadge = document.getElementById('drawer-status-badge');

  if (skuCode) skuCode.innerText = item.sku;
  if (prodName) prodName.innerText = item.prodName;

  const action = item.transferAction || {
    fromStore: `${item.storeName} (${item.storeCode})`,
    toStore: 'The Dubai Mall Flagship (DXB-TDM-01)',
    recommendedUnits: Math.max(2, Math.round(item.onHand * 0.4)),
    freightAED: 180,
    revProtectedAED: Math.round(item.runRate * 4 * item.unitCost * 1.8),
    capReleasedAED: Math.round(item.onHand * item.unitCost * 0.5),
    transitTime: '24 Hours (GCC Logistics Shuttle)',
    urgency: item.status === 'CRITICAL_STOCKOUT_RISK' ? 'CRITICAL' : 'Standard'
  };

  if (fromNode) fromNode.innerText = action.fromStore;
  if (toNode) toNode.innerText = action.toStore;
  if (qtyInput) qtyInput.value = action.recommendedUnits;
  if (freightVal) freightVal.innerText = `AED ${action.freightAED}`;
  if (revProtectedVal) revProtectedVal.innerText = `AED ${action.revProtectedAED.toLocaleString()}`;
  if (capReleasedVal) capReleasedVal.innerText = `AED ${action.capReleasedAED.toLocaleString()}`;
  if (transitVal) transitVal.innerText = action.transitTime;

  if (statusBadge) {
    if (item.isDispatched) {
      statusBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200';
      statusBadge.innerText = 'Dispatched to Transit';
    } else if (item.status === 'CRITICAL_STOCKOUT_RISK') {
      statusBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200';
      statusBadge.innerText = 'Priority 1: Emergency Stockout';
    } else {
      statusBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200';
      statusBadge.innerText = 'Priority 2: Working Capital Overstock';
    }
  }

  // Show drawer
  drawer.classList.remove('translate-x-full');
  if (backdrop) backdrop.classList.remove('hidden');
}

export function closeTransferDrawer() {
  const drawer = document.getElementById('transfer-drawer');
  const backdrop = document.getElementById('drawer-backdrop');
  if (drawer) drawer.classList.add('translate-x-full');
  if (backdrop) backdrop.classList.add('hidden');
}

export function confirmTransferDispatch() {
  const sku = state.activeTransferSku;
  const item = state.inventoryPositions.find(p => p.sku === sku);
  if (!item) return;

  const qtyInput = document.getElementById('drawer-transfer-qty');
  const qty = qtyInput ? parseInt(qtyInput.value) : 10;

  item.isDispatched = true;
  closeTransferDrawer();

  // Show Toast Notification
  showToast(`✅ Transfer Order #TR-2026-${sku.slice(0, 7)} Dispatched: ${qty} units allocated to ${item.transferAction ? item.transferAction.toStore : 'Flagship'}.`);

  updateAllVisuals();
}

function showToast(msg) {
  let toast = document.getElementById('app-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'app-toast';
    toast.className = 'fixed bottom-5 right-5 z-50 bg-slate-900 text-white text-xs font-semibold px-4 py-3 rounded-lg shadow-xl border border-slate-700 flex items-center gap-2 transform transition-all duration-300 translate-y-20 opacity-0';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<span>${msg}</span>`;
  toast.classList.remove('translate-y-20', 'opacity-0');
  setTimeout(() => {
    toast.classList.add('translate-y-20', 'opacity-0');
  }, 4000);
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

  // Dynamically aggregate KPIs
  const filtered = getFilteredPositions();
  let totalRevenue = 0;
  let totalCost = 0;
  let totalOnHand = 0;
  let totalRunRate = 0;
  let totalInventoryCost = 0;
  let dayCount = 60;

  filtered.forEach(pos => {
    const product = rawProducts.find(p => p.sku === pos.sku);
    if (!product) return;
    const unitsSoldEst = pos.runRate * 4;
    const revenue = unitsSoldEst * product.price;
    const cost = unitsSoldEst * product.cost;
    totalRevenue += revenue;
    totalCost += cost;
    totalOnHand += pos.onHand;
    totalRunRate += pos.runRate;
    totalInventoryCost += pos.onHand * pos.unitCost;
  });

  const grossMargin = totalRevenue - totalCost;
  const gmPct = totalRevenue > 0 ? ((grossMargin / totalRevenue) * 100) : 0;
  const weeklyRate = totalRunRate;
  const wos = weeklyRate > 0 ? (totalOnHand / weeklyRate) : 0;
  const annualFactor = 365 / Math.max(1, dayCount);
  const annualizedMargin = grossMargin * annualFactor;
  const gmroi = totalInventoryCost > 0 ? (annualizedMargin / totalInventoryCost) : 0;

  const revElem = document.getElementById('kpi-net-revenue');
  const gmElem = document.getElementById('kpi-gross-margin');
  const gmroiElem = document.getElementById('kpi-gmroi');
  const wosElem = document.getElementById('kpi-wos');

  if (revElem) revElem.innerText = `${Math.round(totalRevenue).toLocaleString()} AED`;
  if (gmElem) gmElem.innerText = `${gmPct.toFixed(1)}%`;
  if (gmroiElem) gmroiElem.innerText = `${gmroi.toFixed(2)}x`;
  if (wosElem) wosElem.innerText = `${wos.toFixed(1)} Wks`;

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
    b.className = "status-chip px-2.5 py-1 rounded-md text-xs font-medium bg-white text-slate-600 hover:text-slate-900 border border-slate-200 transition cursor-pointer";
  });
  if (btn) {
    btn.className = "status-chip px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-900 text-white transition cursor-pointer shadow-xs";
  }
  updateAllVisuals();
}

export function resetFilters() {
  state.currentQuarter = 'All';
  state.currentChannel = 'All';
  state.currentDept = 'All';
  state.currentStatusChip = 'All';
  state.selectedSkuHighlight = null;
  state.currentDiscountPct = 0.15;

  const channelFilter = document.getElementById('channel-filter');
  const deptFilter = document.getElementById('dept-filter');
  const searchInput = document.getElementById('grid-search');
  const discountSlider = document.getElementById('discount-slider');

  if (channelFilter) channelFilter.value = 'All';
  if (deptFilter) deptFilter.value = 'All';
  if (searchInput) searchInput.value = '';
  if (discountSlider) discountSlider.value = '15';

  document.querySelectorAll('.quarter-btn').forEach((b, idx) => {
    b.className = idx === 0 
      ? "quarter-btn px-2.5 py-1 text-xs font-semibold rounded bg-white text-slate-900 shadow-xs border border-slate-200" 
      : "quarter-btn px-2.5 py-1 text-xs font-semibold rounded text-slate-600 hover:text-slate-900 transition";
  });

  document.querySelectorAll('.status-chip').forEach((b, idx) => {
    b.className = idx === 0
      ? "status-chip px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-900 text-white transition cursor-pointer shadow-xs"
      : "status-chip px-2.5 py-1 rounded-md text-xs font-medium bg-white text-slate-600 hover:text-slate-900 border border-slate-200 transition cursor-pointer";
  });

  setPresetDiscount(15);
  applyGlobalFilters();
}

// --- Interaction Handlers ---
export function handleSliderChange(val) {
  state.currentDiscountPct = parseFloat(val) / 100;
  
  // Sync preset pills active state
  document.querySelectorAll('.preset-pill').forEach(btn => {
    const bVal = parseFloat(btn.getAttribute('data-val'));
    if (bVal === parseFloat(val)) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  recalculateSimulation(state.currentDiscountPct, rawProducts, renderSensitivityChart);
}

export function setPresetDiscount(val) {
  const slider = document.getElementById('discount-slider');
  if (slider) {
    slider.value = val;
  }
  handleSliderChange(val);
}

export function switchTab(tabId) {
  // Update Tab Switcher Buttons
  document.querySelectorAll('.tab-switcher-btn').forEach(btn => {
    if (btn.getAttribute('data-tab') === tabId) {
      btn.className = "tab-switcher-btn segmented-btn active";
    } else {
      btn.className = "tab-switcher-btn segmented-btn";
    }
  });

  // Switch Active Tab Pane
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.add('hidden');
  });

  const activePane = document.getElementById(`pane-${tabId}`);
  if (activePane) {
    activePane.classList.remove('hidden');
    // If switching to diagnostics, trigger resize on scatter chart
    if (tabId === 'diagnostics') {
      setTimeout(() => renderScatterPlot(getFilteredPositions(), state.selectedSkuHighlight, drilldownToSku), 50);
    }
  }
}

export function drilldownToSku(sku) {
  state.selectedSkuHighlight = sku;
  const searchInput = document.getElementById('grid-search');
  if (searchInput) {
    searchInput.value = sku;
  }
  switchTab('inventory');
  updateAllVisuals();
  openTransferDrawer(sku);
}

export function handleRowClick(sku) {
  state.selectedSkuHighlight = sku;
  openTransferDrawer(sku);
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

export function updateAllVisuals() {
  const filtered = getFilteredPositions();
  renderRetailPacingChart(weeklyPacingData);
  renderChannelMixChart(channelBreakdownData);
  renderScatterPlot(filtered, state.selectedSkuHighlight, drilldownToSku);
  recalculateSimulation(state.currentDiscountPct, rawProducts, renderSensitivityChart);
  renderTable(filtered, state.selectedSkuHighlight, state.sortColumn, state.sortAsc, handleRowClick);
}

// --- Bootstrap & Window Event Binding ---
window.toggleFullScreen = toggleFullScreen;
window.toggleModal = toggleModal;
window.setQuarter = setQuarter;
window.setStatusChip = setStatusChip;
window.resetFilters = resetFilters;
window.applyGlobalFilters = applyGlobalFilters;
window.handleSliderChange = handleSliderChange;
window.setPresetDiscount = setPresetDiscount;
window.switchTab = switchTab;
window.sortTable = sortTable;
window.exportCSV = handleExportCSV;
window.drilldownToSku = drilldownToSku;
window.openTransferDrawer = openTransferDrawer;
window.closeTransferDrawer = closeTransferDrawer;
window.confirmTransferDispatch = confirmTransferDispatch;

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('grid-search');
  if (searchInput) {
    searchInput.addEventListener('input', () => updateAllVisuals());
  }

  // Initial Boot
  setPresetDiscount(15);
  applyGlobalFilters();
});
