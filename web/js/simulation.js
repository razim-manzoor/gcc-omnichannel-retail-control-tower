/**
 * GCC Omnichannel Retail Control Tower - What-If Simulation Engine
 * Encapsulates microeconomic price elasticity calculations:
 * % ΔQ = -ε * % Discount
 * Breakeven Hurdle Units = Baseline GM / (Simulated AUR - Unit Cost)
 * Working Capital Released = Incremental Units Sold * Unit Cost
 */

let lastCapReleased = 286560;
let lastMarginDelta = -145000;
let lastBeGap = -120;

export function animateValue(elemId, start, end, duration, formatPrefix = '', formatSuffix = '') {
  const obj = document.getElementById(elemId);
  if (!obj) return;
  const range = end - start;
  const startTime = performance.now();

  function step(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const value = Math.round(start + range * progress);
    obj.innerText = `${formatPrefix}${value.toLocaleString()}${formatSuffix}`;
    if (progress < 1) {
      requestAnimationFrame(step);
    }
  }
  requestAnimationFrame(step);
}

export function recalculateSimulation(discountPct, products, onChartRender) {
  let totalBaselineGM = 0;
  let totalSimulatedGM = 0;
  let totalCapitalReleased = 0;
  let totalSimUnits = 0;
  let totalBEUnits = 0;

  const categoryResults = products.map(prod => {
    const discount = discountPct;
    const deltaQ = -prod.elasticity * discount;
    const simUnits = prod.baseUnits * (1 + deltaQ);
    const simAUR = prod.price * (1 - discount);
    
    const baselineGM = prod.baseUnits * (prod.price - prod.cost);
    const simGM = simUnits * (simAUR - prod.cost);
    const gmDelta = simGM - baselineGM;
    
    const unitContribution = simAUR - prod.cost;
    const beUnits = unitContribution > 0 ? (baselineGM / unitContribution) : prod.baseUnits * 3;
    
    const incrementalUnits = Math.max(0, simUnits - prod.baseUnits);
    const capReleased = incrementalUnits * prod.cost;
    
    totalBaselineGM += baselineGM;
    totalSimulatedGM += simGM;
    totalCapitalReleased += capReleased;
    totalSimUnits += simUnits;
    totalBEUnits += beUnits;

    return {
      subcat: prod.subcat,
      baselineGM: baselineGM,
      simGM: simGM,
      capReleased: capReleased,
      isAccretive: gmDelta >= 0
    };
  });

  const totalGMDelta = totalSimulatedGM - totalBaselineGM;
  const roundedCap = Math.round(totalCapitalReleased);
  const roundedDelta = Math.round(totalGMDelta);
  const beGapTotal = Math.round(totalSimUnits - totalBEUnits);
  const capROI = Math.abs(roundedDelta) > 0 ? (roundedCap / Math.abs(roundedDelta)).toFixed(2) : 'N/A';

  // Update Slider Visuals & Label
  const sliderLabel = document.getElementById('slider-val-label');
  if (sliderLabel) {
    sliderLabel.innerText = `${Math.round(discountPct * 100)}% Markdown`;
  }

  // Update Preset Stepper Pills Active State
  const presetPills = document.querySelectorAll('.preset-pill');
  presetPills.forEach(pill => {
    const val = parseInt(pill.getAttribute('data-val'), 10);
    if (val === Math.round(discountPct * 100)) {
      pill.classList.add('active');
    } else {
      pill.classList.remove('active');
    }
  });

  // Animate Numbers smoothly
  animateValue('sim-cap-released', lastCapReleased, roundedCap, 200, '+', ' AED');
  animateValue('sim-margin-sacrificed', lastMarginDelta, roundedDelta, 200, roundedDelta >= 0 ? '+' : '', ' AED');
  animateValue('sim-be-gap', lastBeGap, beGapTotal, 200, beGapTotal >= 0 ? '+' : '', ' Units');
  
  const capRoiElem = document.getElementById('sim-cap-roi');
  if (capRoiElem) {
    capRoiElem.innerText = `${capROI}x`;
  }

  lastCapReleased = roundedCap;
  lastMarginDelta = roundedDelta;
  lastBeGap = beGapTotal;

  // Dynamic Slider Track Gradient Fill (Linear / Slate Dark Fill)
  const pctPos = (discountPct / 0.30) * 100;
  const slider = document.getElementById('discount-slider');
  if (slider) {
    slider.style.background = `linear-gradient(to right, #0F172A 0%, #0F172A ${pctPos}%, #E2E8F0 ${pctPos}%, #E2E8F0 100%)`;
  }

  // Update Verdict Badge & Executive Rationale (Aligned with DAX [Breakeven Feasibility Verdict])
  const badge = document.getElementById('sim-verdict-badge');
  const rationaleElem = document.getElementById('sim-verdict-rationale');
  
  if (badge) {
    if (discountPct === 0) {
      badge.className = "px-2.5 py-1 text-xs font-semibold rounded-md bg-slate-100 text-slate-800 border border-slate-200 inline-flex items-center gap-1.5";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-slate-400"></span> FULL PRICE BASELINE`;
      if (rationaleElem) {
        rationaleElem.innerText = "Operating at full price baseline. Margin realization is 100% preserved with zero promotional dilution. High-velocity SKUs maintain regular buffer.";
      }
    } else if (roundedDelta >= 0) {
      badge.className = "px-2.5 py-1 text-xs font-semibold rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 inline-flex items-center gap-1.5";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500"></span> ACCRETIVE PROFIT YIELD`;
      if (rationaleElem) {
        rationaleElem.innerText = `Elasticity expansion (+${Math.round((-1.82 * discountPct) * 100)}% est volume) exceeds discount depth. Net gross profit expands by +AED ${Math.abs(roundedDelta).toLocaleString()}. Recommended for immediate omni campaign.`;
      }
    } else if (capROI !== 'N/A' && parseFloat(capROI) >= 1.5) {
      badge.className = "px-2.5 py-1 text-xs font-semibold rounded-md bg-amber-50 text-amber-800 border border-amber-200 inline-flex items-center gap-1.5";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span> CAPITAL TRADE-OFF (${capROI}x ROI)`;
      if (rationaleElem) {
        rationaleElem.innerText = `Strategic liquidity trade-off: surrendering AED ${Math.abs(roundedDelta).toLocaleString()} in margin liberates +AED ${roundedCap.toLocaleString()} in trapped working capital (${capROI}x multiplier). Acceptable for overstocked seasonal lines.`;
      }
    } else {
      badge.className = "px-2.5 py-1 text-xs font-semibold rounded-md bg-rose-50 text-rose-800 border border-rose-200 inline-flex items-center gap-1.5";
      badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-500"></span> DILUTIVE MARGIN RISK`;
      if (rationaleElem) {
        rationaleElem.innerText = `Excessive price concession: margin erosion (-AED ${Math.abs(roundedDelta).toLocaleString()}) outweighs volume lift. Breakeven volume shortfall is ${Math.abs(beGapTotal).toLocaleString()} units. Restrict strictly to terminal clearance.`;
      }
    }
  }

  if (typeof onChartRender === 'function') {
    onChartRender(categoryResults);
  }

  return {
    categoryResults,
    totalGMDelta,
    roundedCap,
    roundedDelta,
    beGapTotal,
    capROI
  };
}
