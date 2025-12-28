import React from 'react';
import type { ChartConfig } from '../../types/data';

interface ChartRendererProps {
  config: ChartConfig;
  title?: string;
}

// Simple chart renderer using HTML5 Canvas
const ChartRenderer: React.FC<ChartRendererProps> = ({ config, title }) => {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);

  function renderBarChart(
    ctx: CanvasRenderingContext2D,
    config: ChartConfig,
    width: number,
    height: number
  ) {
    const { data } = config;
    const { labels, datasets } = data;

    if (!datasets.length || !labels.length) return;

    const dataset = datasets[0]; // Use first dataset
    const values = dataset.data;

    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    const barWidth = (chartWidth / values.length) * 0.8;
    const maxValue = Math.max(...values);

    // Draw axes
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // Draw bars
    values.forEach((value, index) => {
      const barHeight = (value / maxValue) * chartHeight;
      const x = padding + (chartWidth / values.length) * index + (chartWidth / values.length - barWidth) / 2;
      const y = height - padding - barHeight;

      ctx.fillStyle = dataset.backgroundColor || '#1890ff';
      ctx.fillRect(x, y, barWidth, barHeight);

      // Draw value label
      ctx.fillStyle = '#333';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(value.toString(), x + barWidth / 2, y - 5);

      // Draw label
      if (labels[index]) {
        ctx.save();
        ctx.translate(x + barWidth / 2, height - padding + 15);
        ctx.fillText(labels[index], 0, 0);
        ctx.restore();
      }
    });
  }

  React.useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Simple bar chart implementation
    if (config.type === 'bar') {
      renderBarChart(ctx, config, canvas.width, canvas.height);
    } else {
      // Placeholder for other chart types
      ctx.fillStyle = '#666';
      ctx.font = '16px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(`${config.type} chart not implemented`, canvas.width / 2, canvas.height / 2);
    }
  }, [config]);

  return (
    <div style={{ marginTop: '2rem' }}>
      {title && (
        <h3 style={{ marginBottom: '1rem', color: '#333' }}>{title}</h3>
      )}
      <div style={{
        border: '1px solid #e8e8e8',
        borderRadius: '8px',
        padding: '1rem',
        backgroundColor: 'white'
      }}>
        <canvas
          ref={canvasRef}
          width={600}
          height={400}
          style={{ maxWidth: '100%', height: 'auto' }}
        />
      </div>
    </div>
  );
};

export default ChartRenderer;