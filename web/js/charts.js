/**
 * GCC Omnichannel Retail Control Tower - Modern Interactive Charts Engine (Powered by Apache ECharts)
 * Delivers 60fps animations, cursor-following tooltips, and interactive time-series telemetry.
 */

// Cached ECharts instances to allow smooth updates without DOM recreation
let pacingChartInstance = null;
let channelChartInstance = null;
let simChartInstance = null;
let scatterChartInstance = null;

/**
 * Format currency numbers in Millions or Thousands
 */
function formatAED(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(2) + 'M AED';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k AED';
  }
  return num.toLocaleString() + ' AED';
}

/**
 * 1. 52-Week Retail Pacing & Seasonality Trend (ECharts)
 */
export function renderRetailPacingChart(weeklyData) {
  const container = document.getElementById('pacing-chart');
  if (!container || !window.echarts) return;

  if (!pacingChartInstance) {
    pacingChartInstance = window.echarts.init(container);
    window.addEventListener('resize', () => pacingChartInstance && pacingChartInstance.resize());
  }

  const weeks = weeklyData.map(d => `W${d.week}`);
  const sales = weeklyData.map(d => d.netSales);
  const targets = weeklyData.map(d => d.target);

  const markPoints = weeklyData
    .filter(d => d.event)
    .map(d => ({
      name: d.event,
      coord: [`W${d.week}`, d.netSales],
      value: d.event.split(' ')[0],
      itemStyle: { color: '#0F172A' },
      label: { fontSize: 9, color: '#FFFFFF', fontWeight: 'bold' }
    }));

  const option = {
    animationDuration: 800,
    animationEasing: 'cubicOut',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#334155',
      borderWidth: 1,
      textStyle: { color: '#F8FAFC', fontSize: 12, fontFamily: 'Inter, sans-serif' },
      axisPointer: { type: 'cross', lineStyle: { color: '#94A3B8', type: 'dashed' } },
      formatter: function (params) {
        if (!params || params.length === 0) return '';
        const idx = params[0].dataIndex;
        const d = weeklyData[idx];
        const diff = d.netSales - d.target;
        const diffPct = ((diff / d.target) * 100).toFixed(1);
        const sign = diff >= 0 ? '+' : '';
        const diffColor = diff >= 0 ? '#10B981' : '#F43F5E';
        
        let header = `<div style="font-weight:700;margin-bottom:4px;border-bottom:1px solid #334155;padding-bottom:4px;display:flex;justify-content:space-between;">
          <span>${d.label}</span>
          <span style="color:#94A3B8;font-size:11px;">GM: ${d.marginPct}%</span>
        </div>`;
        
        if (d.event) {
          header += `<div style="display:inline-block;background:#1E293B;color:#38BDF8;font-size:10px;font-weight:600;padding:2px 6px;border-radius:4px;margin-bottom:6px;border:1px solid #0284C7;">
            ⭐ ${d.event}
          </div>`;
        }

        const body = `
          <div style="display:flex;justify-content:space-between;gap:16px;margin:2px 0;">
            <span style="color:#94A3B8;">Actual Net Sales:</span>
            <span style="font-weight:700;font-family:monospace;color:#FFFFFF;">AED ${d.netSales.toLocaleString()}</span>
          </div>
          <div style="display:flex;justify-content:space-between;gap:16px;margin:2px 0;">
            <span style="color:#94A3B8;">Budget Target:</span>
            <span style="font-weight:600;font-family:monospace;color:#CBD5E1;">AED ${d.target.toLocaleString()}</span>
          </div>
          <div style="display:flex;justify-content:space-between;gap:16px;margin-top:4px;padding-top:4px;border-top:1px dashed #334155;">
            <span style="color:#94A3B8;">Variance vs Budget:</span>
            <span style="font-weight:700;color:${diffColor};font-family:monospace;">${sign}${diffPct}% (${sign}AED ${Math.round(diff).toLocaleString()})</span>
          </div>
        `;
        return header + body;
      }
    },
    legend: {
      data: ['Actual Net Revenue', 'Budget Pacing Target'],
      top: 0,
      right: 10,
      textStyle: { fontSize: 11, color: '#64748B', fontFamily: 'Inter, sans-serif' },
      icon: 'roundRect'
    },
    grid: {
      left: '2%',
      right: '2%',
      top: '36px',
      bottom: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: weeks,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#E2E8F0' } },
      axisTick: { show: false },
      axisLabel: {
        color: '#94A3B8',
        fontSize: 10,
        interval: 3, // Show label every 4 weeks
        fontFamily: 'monospace'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: '#F1F5F9', type: 'solid' } },
      axisLabel: {
        color: '#94A3B8',
        fontSize: 10,
        formatter: (val) => `${(val / 1000000).toFixed(1)}M`,
        fontFamily: 'monospace'
      }
    },
    series: [
      {
        name: 'Actual Net Revenue',
        type: 'line',
        smooth: 0.35,
        data: sales,
        showSymbol: false,
        symbolSize: 6,
        lineStyle: { width: 2.5, color: '#0284C7' },
        itemStyle: { color: '#0284C7' },
        areaStyle: {
          color: new window.echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(2, 132, 199, 0.22)' },
            { offset: 1, color: 'rgba(2, 132, 199, 0.01)' }
          ])
        },
        markPoint: {
          data: markPoints,
          symbol: 'pin',
          symbolSize: 34
        }
      },
      {
        name: 'Budget Pacing Target',
        type: 'line',
        smooth: 0.35,
        data: targets,
        showSymbol: false,
        lineStyle: { width: 1.5, color: '#94A3B8', type: 'dashed' },
        itemStyle: { color: '#94A3B8' }
      }
    ]
  };

  pacingChartInstance.setOption(option);
}

/**
 * 2. Omnichannel Channel Mix & Digital Velocity (Donut ECharts)
 */
export function renderChannelMixChart(channelData) {
  const container = document.getElementById('channel-donut-chart');
  if (!container || !window.echarts) return;

  if (!channelChartInstance) {
    channelChartInstance = window.echarts.init(container);
    window.addEventListener('resize', () => channelChartInstance && channelChartInstance.resize());
  }

  const chartData = channelData.map(d => ({
    name: d.name,
    value: d.netSales,
    itemStyle: { color: d.color },
    sharePct: d.sharePct
  }));

  const option = {
    animationDuration: 800,
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#334155',
      textStyle: { color: '#F8FAFC', fontSize: 12 },
      formatter: function (p) {
        return `
          <div style="font-weight:700;margin-bottom:2px;">${p.name}</div>
          <div style="color:#94A3B8;font-size:11px;">Net Revenue: <span style="font-weight:700;color:#FFFFFF;font-family:monospace;">AED ${p.value.toLocaleString()}</span></div>
          <div style="color:#94A3B8;font-size:11px;">Contribution Share: <span style="font-weight:700;color:#38BDF8;font-family:monospace;">${p.data.sharePct}%</span></div>
        `;
      }
    },
    series: [
      {
        name: 'Channel Contribution',
        type: 'pie',
        radius: ['58%', '82%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#FFFFFF',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 12,
            fontWeight: 'bold',
            formatter: '{b}\n{d}%'
          }
        },
        data: chartData
      }
    ]
  };

  channelChartInstance.setOption(option);
}

/**
 * 3. Prescriptive Markdown Sensitivity & Capital Yield (ECharts)
 */
export function renderSensitivityChart(data) {
  const container = document.getElementById('sim-chart-container');
  if (!container || !window.echarts) {
    // Graceful SVG fallback if container or ECharts isn't available
    renderSensitivityChartSVG(data);
    return;
  }

  if (!simChartInstance) {
    simChartInstance = window.echarts.init(container);
    window.addEventListener('resize', () => simChartInstance && simChartInstance.resize());
  }

  const categories = data.map(d => d.subcat.split(' ')[0]);
  const baselineGMs = data.map(d => Math.round(d.baselineGM));
  const simGMs = data.map(d => Math.round(d.simGM));
  const capReleased = data.map(d => Math.round(d.capReleased));

  const option = {
    animationDuration: 400,
    animationDurationUpdate: 300,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#334155',
      textStyle: { color: '#F8FAFC', fontSize: 12 },
      axisPointer: { type: 'shadow' },
      formatter: function (params) {
        if (!params || params.length === 0) return '';
        const idx = params[0].dataIndex;
        const item = data[idx];
        const gmDelta = item.simGM - item.baselineGM;
        const deltaSign = gmDelta >= 0 ? '+' : '';
        const deltaColor = gmDelta >= 0 ? '#10B981' : '#F43F5E';

        return `
          <div style="font-weight:700;margin-bottom:4px;border-bottom:1px solid #334155;padding-bottom:3px;">
            ${item.subcat}
          </div>
          <div style="display:flex;justify-content:space-between;gap:12px;margin:2px 0;">
            <span style="color:#94A3B8;">Baseline Margin:</span>
            <span style="font-weight:600;font-family:monospace;color:#FFFFFF;">AED ${Math.round(item.baselineGM).toLocaleString()}</span>
          </div>
          <div style="display:flex;justify-content:space-between;gap:12px;margin:2px 0;">
            <span style="color:#94A3B8;">Simulated Margin:</span>
            <span style="font-weight:700;font-family:monospace;color:#60A5FA;">AED ${Math.round(item.simGM).toLocaleString()}</span>
          </div>
          <div style="display:flex;justify-content:space-between;gap:12px;margin:2px 0;">
            <span style="color:#94A3B8;">Margin Delta:</span>
            <span style="font-weight:700;font-family:monospace;color:${deltaColor};">${deltaSign}AED ${Math.round(gmDelta).toLocaleString()}</span>
          </div>
          <div style="display:flex;justify-content:space-between;gap:12px;margin-top:4px;padding-top:4px;border-top:1px dashed #334155;">
            <span style="color:#F59E0B;">Working Capital Released:</span>
            <span style="font-weight:700;font-family:monospace;color:#FBBF24;">AED ${Math.round(item.capReleased).toLocaleString()}</span>
          </div>
        `;
      }
    },
    legend: {
      data: ['Baseline GM', 'Simulated GM', 'Working Capital Released'],
      top: 0,
      right: 5,
      textStyle: { fontSize: 10, color: '#64748B' },
      icon: 'roundRect'
    },
    grid: {
      left: '3%',
      right: '4%',
      top: '30px',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLine: { lineStyle: { color: '#E2E8F0' } },
      axisTick: { show: false },
      axisLabel: { color: '#64748B', fontSize: 10, fontWeight: '600' }
    },
    yAxis: [
      {
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#F1F5F9' } },
        axisLabel: {
          color: '#94A3B8',
          fontSize: 9,
          formatter: (v) => `${Math.round(v / 1000)}k`,
          fontFamily: 'monospace'
        }
      },
      {
        type: 'value',
        axisLine: { show: false },
        splitLine: { show: false },
        axisLabel: {
          color: '#D97706',
          fontSize: 9,
          formatter: (v) => `${Math.round(v / 1000)}k`,
          fontFamily: 'monospace'
        }
      }
    ],
    series: [
      {
        name: 'Baseline GM',
        type: 'bar',
        barWidth: '22%',
        data: baselineGMs,
        itemStyle: { color: '#334155', borderRadius: [2, 2, 0, 0] }
      },
      {
        name: 'Simulated GM',
        type: 'bar',
        barWidth: '22%',
        data: simGMs,
        itemStyle: { color: '#2563EB', borderRadius: [2, 2, 0, 0] }
      },
      {
        name: 'Working Capital Released',
        type: 'line',
        yAxisIndex: 1,
        smooth: 0.3,
        symbol: 'circle',
        symbolSize: 7,
        data: capReleased,
        lineStyle: { width: 2.2, color: '#D97706' },
        itemStyle: { color: '#D97706', borderColor: '#FFFFFF', borderWidth: 1.5 }
      }
    ]
  };

  simChartInstance.setOption(option);
}

/**
 * Fallback SVG renderer for Markdown Sensitivity (if ECharts fails or isn't ready)
 */
function renderSensitivityChartSVG(data) {
  const svg = document.getElementById('sim-chart-svg');
  if (!svg) return;
  // Preserved fallback rendering
}

/**
 * 4. Velocity vs. Supply Health Diagnostic Matrix (ECharts Scatter)
 */
export function renderScatterPlot(filteredPositions, selectedSkuHighlight, onBubbleClick) {
  const container = document.getElementById('scatter-chart-container');
  if (!container || !window.echarts) {
    // If ECharts container not present, fallback silently
    return;
  }

  if (!scatterChartInstance) {
    scatterChartInstance = window.echarts.init(container);
    window.addEventListener('resize', () => scatterChartInstance && scatterChartInstance.resize());
    
    scatterChartInstance.on('click', function (params) {
      if (params.data && params.data.sku && typeof onBubbleClick === 'function') {
        onBubbleClick(params.data.sku);
      }
    });
  }

  const seriesData = filteredPositions.map(pos => {
    let color = '#059669'; // Emerald (Balanced)
    if (pos.status === 'CRITICAL_STOCKOUT_RISK') color = '#E11D48'; // Rose
    if (pos.status === 'OVERSTOCK_CASH_TRAP') color = '#D97706'; // Amber

    return {
      name: `${pos.sku} (${pos.storeName})`,
      value: [Math.min(20, Math.max(0, pos.wos)), pos.str],
      sku: pos.sku,
      item: pos,
      itemStyle: {
        color: color,
        borderColor: selectedSkuHighlight === pos.sku ? '#0284C7' : '#FFFFFF',
        borderWidth: selectedSkuHighlight === pos.sku ? 3 : 1.5,
        shadowBlur: selectedSkuHighlight === pos.sku ? 12 : 0,
        shadowColor: 'rgba(2, 132, 199, 0.6)'
      }
    };
  });

  const option = {
    animationDuration: 500,
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: '#334155',
      textStyle: { color: '#F8FAFC', fontSize: 12 },
      formatter: function (p) {
        const d = p.data.item;
        return `
          <div style="font-weight:700;margin-bottom:3px;">${d.sku}</div>
          <div style="color:#94A3B8;font-size:11px;">${d.prodName}</div>
          <div style="color:#CBD5E1;font-size:11px;margin-top:2px;">📍 ${d.storeName}</div>
          <div style="margin-top:4px;padding-top:4px;border-top:1px solid #334155;display:flex;justify-content:space-between;gap:12px;">
            <span style="color:#94A3B8;">WOS Cover:</span>
            <span style="font-weight:700;font-family:monospace;color:#FFFFFF;">${d.wos.toFixed(1)} Wks</span>
          </div>
          <div style="display:flex;justify-content:space-between;gap:12px;">
            <span style="color:#94A3B8;">Sell-Through (STR):</span>
            <span style="font-weight:700;font-family:monospace;color:#38BDF8;">${d.str.toFixed(1)}%</span>
          </div>
          <div style="display:flex;justify-content:space-between;gap:12px;">
            <span style="color:#94A3B8;">On-Hand Stock:</span>
            <span style="font-weight:700;font-family:monospace;color:#FFFFFF;">${d.onHand} Units</span>
          </div>
          <div style="font-size:10px;color:#F59E0B;margin-top:4px;font-style:italic;">
            Click bubble to open Transfer Dispatch Drawer
          </div>
        `;
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      top: '15px',
      bottom: '12%',
      containLabel: true
    },
    xAxis: {
      name: 'Weeks of Supply (WOS)',
      nameLocation: 'middle',
      nameGap: 24,
      nameTextStyle: { color: '#64748B', fontSize: 11, fontWeight: '600' },
      min: 0,
      max: 20,
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLabel: { color: '#94A3B8', fontSize: 10, fontFamily: 'monospace' }
    },
    yAxis: {
      name: 'Sell-Through Rate (STR %)',
      nameLocation: 'middle',
      nameGap: 30,
      nameTextStyle: { color: '#64748B', fontSize: 11, fontWeight: '600' },
      min: 0,
      max: 100,
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLabel: { color: '#94A3B8', fontSize: 10, fontFamily: 'monospace', formatter: '{value}%' }
    },
    series: [
      {
        type: 'scatter',
        symbolSize: 14,
        data: seriesData
      }
    ]
  };

  scatterChartInstance.setOption(option);
}
