import { useRef, useEffect } from 'react';
import ChartJS, { ChartConfiguration, ChartData, ChartOptions, ChartType } from 'chart.js/auto';

interface ChartProps<TType extends ChartType = 'bar'> {
  /** Chart.js chart type. Defaults to 'bar' for backwards compatibility. */
  type?: TType;
  data?: ChartData<TType>;
  options?: ChartOptions<TType>;
  /** Accessible description of what the chart shows. */
  ariaLabel?: string;
}

function Chart<TType extends ChartType = 'bar'>({ type, data, options, ariaLabel }: ChartProps<TType>) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const instanceRef = useRef<ChartJS<TType> | null>(null);

  useEffect(() => {
    if (!data || !canvasRef.current) return;
    // Destroy previous chart if exists
    instanceRef.current?.destroy();
    const config: ChartConfiguration<TType> = {
      type: (type ?? 'bar') as TType,
      data,
      options: options ?? ({ responsive: true, maintainAspectRatio: false } as ChartOptions<TType>),
    };
    instanceRef.current = new ChartJS<TType>(canvasRef.current, config);
    return () => {
      instanceRef.current?.destroy();
      instanceRef.current = null;
    };
  }, [type, data, options]);

  return <canvas ref={canvasRef} role="img" aria-label={ariaLabel} />;
}

export default Chart;
