import React from 'react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      gap: '1rem',
      backgroundColor: '#fff2f0',
      border: '1px solid #ffccc7',
      borderRadius: '6px'
    }}>
      <div style={{
        fontSize: '48px',
        color: '#ff4d4f'
      }}>
        ⚠️
      </div>
      <h3 style={{ margin: 0, color: '#cf1322' }}>Error</h3>
      <p style={{ margin: 0, color: '#666', textAlign: 'center' }}>
        {message}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            padding: '8px 16px',
            backgroundColor: '#1890ff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;