/**
 * 数据格式化工具函数
 */

// 格式化执行时间
export const formatExecutionTime = (seconds: number): string => {
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(2)}ms`;
  } else if (seconds < 60) {
    return `${seconds.toFixed(2)}s`;
  } else {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(2)}s`;
  }
};

// 格式化百分比
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${(value * 100).toFixed(decimals)}%`;
};

// 格式化数字
export const formatNumber = (value: number, decimals: number = 0): string => {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  } else if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  } else {
    return value.toFixed(decimals);
  }
};

// 格式化评分
export const formatRating = (rating: number): string => {
  return rating.toFixed(1);
};

// 格式化日期
export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
};

// 格式化数组为字符串
export const formatArray = (arr: string[], maxItems: number = 3): string => {
  if (!arr || arr.length === 0) return '无';

  const items = arr.slice(0, maxItems);
  const result = items.join(', ');

  if (arr.length > maxItems) {
    return `${result} 等${arr.length}项`;
  }

  return result;
};

// 获取状态颜色
export const getStatusColor = (success: boolean): string => {
  return success ? '#52c41a' : '#ff4d4f';
};

// 获取性能等级
export const getPerformanceLevel = (ratio: number): { level: string; color: string } => {
  if (ratio < 1.5) {
    return { level: '优秀', color: '#52c41a' };
  } else if (ratio < 3) {
    return { level: '良好', color: '#1890ff' };
  } else if (ratio < 5) {
    return { level: '一般', color: '#faad14' };
  } else {
    return { level: '需要优化', color: '#ff4d4f' };
  }
};

// 格式化数据库名称
export const formatDatabaseName = (dbName: string): string => {
  const nameMap: Record<string, string> = {
    'opengauss': 'OpenGauss',
    'hive': 'Hive',
    'neo4j': 'Neo4j'
  };

  return nameMap[dbName] || dbName;
};

// 格式化查询类型名称
export const formatQueryTypeName = (queryType: string): string => {
  const nameMap: Record<string, string> = {
    'movies_by_year': '按年份查询电影',
    'movies_by_director': '按导演查询电影',
    'movies_by_actor_starring': '按演员查询主演电影',
    'movies_by_actor_participated': '按演员查询参演电影',
    'movies_by_genre': '按类型查询电影统计',
    'high_rated_movies': '查询高评分电影',
    'actor_collaborations': '查询演员合作关系',
    'director_actor_collaborations': '查询导演演员合作关系',
    'popular_actor_combinations': '查询热门演员组合'
  };

  return nameMap[queryType] || queryType;
};

// 截断文本
export const truncateText = (text: string, maxLength: number = 50): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// 格式化文件大小
export const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`;
};

// 验证邮箱格式
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// 验证URL格式
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// 生成随机颜色
export const generateRandomColor = (): string => {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
};

// 获取图表颜色数组
export const getChartColors = (count: number): string[] => {
  const baseColors = [
    '#1890ff', '#52c41a', '#faad14', '#f5222d',
    '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16'
  ];

  const colors: string[] = [];
  for (let i = 0; i < count; i++) {
    if (i < baseColors.length) {
      colors.push(baseColors[i]);
    } else {
      colors.push(generateRandomColor());
    }
  }

  return colors;
};

