import React from 'react';

const WelcomePlaceholder: React.FC = () => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      textAlign: 'center',
      color: '#aaa',
      backgroundColor: '#f9f9f9',
      borderRadius: '8px',
      border: '2px dashed #ddd'
    }}>
            <h2 style={{ fontSize: '24px', margin: '0 0 16px 0', color: '#555' }}>欢迎使用查询系统</h2>
      <p style={{ maxWidth: '400px' }}>
        请在左侧选择一个查询类型并设置参数，然后点击“执行查询”来探索我们的电影数据库。
      </p>
    </div>
  );
};

export default WelcomePlaceholder;

