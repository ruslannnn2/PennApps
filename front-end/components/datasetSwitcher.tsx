// src/components/DatasetSwitcher.tsx
import React from 'react';
import { GraphData } from './ForceGraph';

export interface Dataset {
  name: string;
  data: GraphData;
  emoji: string;
  description: string;
}

interface DatasetSwitcherProps {
  datasets: Dataset[];
  onDatasetChange: (dataset: Dataset) => void;
  currentDataset: string;
}

const DatasetSwitcher: React.FC<DatasetSwitcherProps> = ({ 
  datasets, 
  onDatasetChange, 
  currentDataset 
}) => {
  return (
    <section className="dataset-switcher">
      <h3>📊 Choose Dataset</h3>
      <div className="dataset-buttons">
        {datasets.map((dataset, index) => (
          <button
            key={index}
            onClick={() => onDatasetChange(dataset)}
            className={`dataset-btn ${currentDataset === dataset.name ? 'active' : ''}`}
            title={dataset.description}
          >
            {dataset.emoji} {dataset.name}
          </button>
        ))}
      </div>
    </section>
  );
};

export default DatasetSwitcher;