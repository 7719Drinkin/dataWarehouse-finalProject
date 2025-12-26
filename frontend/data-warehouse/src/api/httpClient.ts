export interface HttpResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  status: number;
}

class HttpClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async get<T = unknown>(endpoint: string, params?: Record<string, unknown>): Promise<HttpResponse<T>> {
    try {
      const url = new URL(endpoint, this.baseURL);

      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            url.searchParams.append(key, value.toString());
          }
        });
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30秒超时

      const response = await fetch(url.toString(), {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      return {
        success: true,
        data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network request failed',
        status: 0
      };
    }
  }
}

// 获取环境变量的辅助函数
const getApiUrl = (): string => {
  // 在 Vite 中使用 import.meta.env
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return import.meta.env.VITE_API_URL || 'http://localhost:5000';
  }
  
  // 回退到默认值
  return 'http://localhost:5000';
};

// 导出单例实例
export const httpClient = new HttpClient(getApiUrl());