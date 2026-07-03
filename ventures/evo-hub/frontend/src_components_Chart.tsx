```tsx
import React from 'react';
import Chart from 'chart.js/auto';

interface ChartProps {
  data?: any;
}

const ChartComponent: React.FC<ChartProps> = ({ data }) => {
  const chartRef = React.useRef(null);

  React.useEffect(() => {
    if (data && chartRef.current) {
      new Chart(chartRef.current, {
        type: 'bar',
        data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      });
    }
  }, [data]);

  return <canvas ref={chartRef} />;
};

const Chart = () => {
  const data = {
    labels: ['January', 'February', 'March'],
    datasets: [
      {
        label: 'Dataset',
        data: [65, 59, 80],
        fill: false,
        borderColor: '#4bc0c0',
      },
    ],
  };

  return <ChartComponent data={data} />;
};

export default Chart;
```