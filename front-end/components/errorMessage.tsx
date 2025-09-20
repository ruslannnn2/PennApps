// src/components/ErrorMessage.tsx
import React from 'react';

interface ErrorMessageProps {
  error: string;
  onRetry?: () => void;
  title?: string;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ 
  error, 
  onRetry,
  title = "❌ Error Loading Data" 
}) => {
  return (
    <div className="error-message">
      <h3>{title}</h3>
      <p>{error}</p>
      <p>Make sure your Python backend is running on port 5000</p>
      {onRetry && (
        <button onClick={onRetry} className="retry-btn">
          🔄 Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;