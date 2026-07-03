import React, { useRef, useEffect } from 'react';
import ChartJS, { ChartData, ChartOptions } from 'chart.js/auto';

interface ChartProps {
  data?: ChartData<'bar'>;
  options?: ChartOptions<'bar'>;
}

const ChartComponent: React.FC<ChartProps> = ({ data, options }) => {
  const chartRef = useRef<HTMLCanvasElement | null>(null);
  const chartInstance = useRef<ChartJS | null>(null);

  useEffect(() => {
    if (data && chartRef.current) {
      // Destroy previous chart if exists
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
      chartInstance.current = new ChartJS(chartRef.current, {
        type: 'bar',
        data,
        options: options || {
          responsive: true,
          maintainAspectRatio: false,
        },
      });
    }
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data, options]);

  return <canvas ref={chartRef} />;
};

const Chart: React.FC = () => {
  const data: ChartData<'bar'> = {
    labels: ['January', 'February', 'March'],
    datasets: [
      {
        label: 'Dataset',
        data: [65, 59, 80],
        fill: false,
        borderColor: '#4bc0c0',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      },
    ],
  };

  return <ChartComponent data={data} />;
};

export default Chart;
