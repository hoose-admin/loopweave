declare module 'react-plotly.js/factory' {
  import { Component } from 'react';
  import { Data, Layout, Config } from 'plotly.js';

  interface PlotParams {
    data: Data[];
    layout?: Partial<Layout>;
    config?: Partial<Config>;
    frames?: any[];
    revision?: number;
    onInitialized?: (figure: any, graphDiv: HTMLElement) => void;
    onUpdate?: (figure: any, graphDiv: HTMLElement) => void;
    onPurge?: (figure: any, graphDiv: HTMLElement) => void;
    onError?: (err: Error) => void;
    debug?: boolean;
    useResizeHandler?: boolean;
    style?: React.CSSProperties;
    className?: string;
  }

  interface PlotlyComponent extends Component<PlotParams> {}

  function createPlotlyComponent(plotly: any): React.ComponentType<PlotParams>;
  
  export default createPlotlyComponent;
}

