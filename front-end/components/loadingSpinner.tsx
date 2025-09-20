// src/components/LoadingSpinner.tsx
import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  message = "Loading...", 
  size = 'medium' 
}) => {
  const sizeClasses = {
    small: 'loading-small',
    medium: 'loading-medium', 
    large: 'loading-large'
  };

  return (
    <div className={`loading-container ${sizeClasses[size]}`}>
      <div className="loading-spinner">
        <div className="spinner"></div>
      </div>
      <h3 className="loading-message">📊 {message}</h3>
    </div>
  );
};

export default LoadingSpinner;