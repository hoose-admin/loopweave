"use client";

import React from "react";
import createPlotlyComponent from "react-plotly.js/factory";
import Plotly from "@/utils/custom-plotly";

const Plot = createPlotlyComponent(Plotly);

interface PlotlyChartProps {
  data: any[];
  layout: any;
  config?: any;
  staticPlot?: boolean;
}

export default function PlotlyChart({
  data,
  layout,
  config,
  staticPlot = true,
}: PlotlyChartProps) {
  const plotConfig = {
    displayModeBar: false,
    staticPlot: staticPlot,
    responsive: true,
    ...config,
  };

  return <Plot data={data} layout={layout} config={plotConfig} />;
}
