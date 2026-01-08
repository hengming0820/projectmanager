import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { ApiStatus } from './status'
import { HttpError, showError } from './error'
import { $t } from '@/locales'

/** 扩展配置接口，支持重试和错误消息控制 */
export interface ExtendedAxiosRequestConfig extends AxiosRequestConfig {
  showErrorMessage?: boolean
  /** 重试次数，默认为 2 */
  retries?: number
  /** 重试延迟（毫秒），默认为 1000 */
  retryDelay?: number
  /** 原始配置对象（兼容旧代码） */
  _retryCount?: number
}

// 后端API专用的HTTP客户端
class BackendApiClient {
  private instance: AxiosInstance
  private isUnauthorizedErrorShown: boolean = false
  private readonly DEFAULT_RETRIES = 2
  private readonly DEFAULT_RETRY_DELAY = 1000

  constructor() {
    this.instance = axios.create({
      timeout: 15000, // 增加到 15s，与原 http 客户端一致
      baseURL: '/api', // 使用相对路径，让Vite代理处理
      withCredentials: false,
      headers: {
        'Content-Type': 'application/json'
      },
      // ✅ 配置参数序列化器，确保数组参数正确序列化
      paramsSerializer: {
        serialize: (params) => {
          const searchParams = new URLSearchParams()
          Object.keys(params || {}).forEach((key) => {
            const value = params[key]
            if (Array.isArray(value)) {
              // 数组参数：重复添加同名参数 (status=active&status=paused)
              value.forEach((item) => searchParams.append(key, item))
            } else if (value !== undefined && value !== null) {
              searchParams.append(key, String(value))
            }
          })
          return searchParams.toString()
        }
      }
    })

    // 请求拦截器
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // 添加token到请求头（从 localStorage 获取，不依赖 store，避免循环依赖）
        const token = localStorage.getItem('token') || sessionStorage.getItem('token')
        
        // 开发环境日志
        if (import.meta.env.DEV) {
          console.log(`🚀 [API] ${config.method?.toUpperCase()} ${config.url}`, {
            params: config.params,
            data: config.data
          })
        }

        if (token) {
          // 检查token是否已经包含Bearer前缀
          if (token.startsWith('Bearer ')) {
            config.headers.Authorization = token
          } else {
            config.headers.Authorization = `Bearer ${token}`
          }
        }

        return config
      },
      (error) => {
        console.error('❌ [API] 请求配置错误:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // 开发环境日志
        if (import.meta.env.DEV) {
           console.log(`✅ [API] ${response.config.url} (${response.status})`)
        }

        // 直接返回响应数据
        // 注意：这里兼容了两种后端返回格式
        // 1. 标准格式: { code: 200, data: {...}, msg: '...' }
        // 2. 直接返回数据: {...} 或 [...]
        return response.data
      },
      async (error) => {
        const config = error.config as ExtendedAxiosRequestConfig
        
        // 错误日志
        console.error('❌ [API] 请求失败:', {
          url: config?.url,
          status: error.response?.status,
          message: error.message,
          data: error.response?.data
        })

        // 处理 401 未认证 (Token过期)
        if (error.response?.status === ApiStatus.unauthorized) {
           return this.handleUnauthorized()
        }
        
        // 处理 403 权限不足
        if (error.response?.status === ApiStatus.forbidden) {
          console.warn('🚫 [API] 权限不足(403)')
        }

        // 处理 422 验证错误 (特殊处理，提取详细信息)
        if (error.response?.status === 422) {
          const responseData = error.response.data
          let errorMsg = '数据验证失败'
          
          if (responseData?.errors && Array.isArray(responseData.errors)) {
            errorMsg = responseData.errors
              .map((err: any) => `${err.field}: ${err.message}`)
              .join('; ')
          } else if (responseData?.detail) {
            errorMsg = responseData.detail
          }
          
          const httpError = new HttpError(errorMsg, 422)
          if (config?.showErrorMessage !== false) {
            showError(httpError, true)
          }
          return Promise.reject(httpError)
        }

        // 重试逻辑
        if (this.shouldRetry(error) && config && (config.retries ?? this.DEFAULT_RETRIES) > 0) {
           config._retryCount = config._retryCount || 0
           if (config._retryCount < (config.retries ?? this.DEFAULT_RETRIES)) {
             config._retryCount++
             const delay = config.retryDelay ?? this.DEFAULT_RETRY_DELAY
             console.log(`🔄 [API] 正在重试 (${config._retryCount})...`)
             await new Promise(resolve => setTimeout(resolve, delay))
             return this.instance(config)
           }
        }

        // 通用错误处理
        const message = error.response?.data?.detail || 
                        error.response?.data?.message || 
                        error.message || 
                        $t('httpMsg.requestFailed')
        
        const httpError = new HttpError(message, error.response?.status || ApiStatus.error)
        
        if (config?.showErrorMessage !== false) {
          // 避免重复显示 401 错误 (虽然上面已经拦截了，双重保险)
          if (error.response?.status !== ApiStatus.unauthorized) {
             showError(httpError, true)
          }
        }

        return Promise.reject(httpError)
      }
    )
  }

  /** 处理 401 逻辑 */
  private handleUnauthorized(): Promise<never> {
    if (!this.isUnauthorizedErrorShown) {
      this.isUnauthorizedErrorShown = true
      
      // 1. 提示
      ElMessage.error('登录已过期，请重新登录')
      
      // 2. 清除数据
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('userId')
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('refreshToken')
      sessionStorage.removeItem('userId')

      // 3. 延迟跳转
      setTimeout(() => {
        this.isUnauthorizedErrorShown = false
        if (!window.location.href.includes('/login')) {
          window.location.href = '/login'
        }
      }, 1500)
    }
    
    // 返回 pending Promise 中断业务流程
    return new Promise(() => {})
  }

  /** 判断是否需要重试 */
  private shouldRetry(error: any): boolean {
    // 仅对网络错误或 5xx 服务端错误进行重试
    if (!error.response) return true // 网络错误
    const status = error.response.status
    return [
      ApiStatus.requestTimeout,
      ApiStatus.internalServerError,
      ApiStatus.badGateway,
      ApiStatus.serviceUnavailable,
      ApiStatus.gatewayTimeout
    ].includes(status)
  }

  // ==========================================
  // 公共方法 (兼容两种调用风格)
  // ==========================================

  /**
   * 通用请求方法
   * 兼容 backendApi.get(url, config) 和 http.get(config)
   */
  get<T = any>(config: ExtendedAxiosRequestConfig): Promise<T>
  get<T = any>(url: string, config?: ExtendedAxiosRequestConfig): Promise<T>
  async get<T = any>(urlOrConfig: string | ExtendedAxiosRequestConfig, config?: ExtendedAxiosRequestConfig): Promise<T> {
    if (typeof urlOrConfig === 'string') {
      return this.instance.get(urlOrConfig, config)
    } else {
      return this.instance.get(urlOrConfig.url || '', urlOrConfig)
    }
  }

  post<T = any>(config: ExtendedAxiosRequestConfig): Promise<T>
  post<T = any>(url: string, data?: any, config?: ExtendedAxiosRequestConfig): Promise<T>
  async post<T = any>(urlOrConfig: string | ExtendedAxiosRequestConfig, data?: any, config?: ExtendedAxiosRequestConfig): Promise<T> {
    if (typeof urlOrConfig === 'string') {
      return this.instance.post(urlOrConfig, data, config)
    } else {
      // 兼容 http.post({ url: '...', data: ... })
      const conf = urlOrConfig
      return this.instance.post(conf.url || '', conf.data, conf)
    }
  }

  put<T = any>(config: ExtendedAxiosRequestConfig): Promise<T>
  put<T = any>(url: string, data?: any, config?: ExtendedAxiosRequestConfig): Promise<T>
  async put<T = any>(urlOrConfig: string | ExtendedAxiosRequestConfig, data?: any, config?: ExtendedAxiosRequestConfig): Promise<T> {
    if (typeof urlOrConfig === 'string') {
      return this.instance.put(urlOrConfig, data, config)
    } else {
      const conf = urlOrConfig
      return this.instance.put(conf.url || '', conf.data, conf)
    }
  }

  delete<T = any>(config: ExtendedAxiosRequestConfig): Promise<T>
  delete<T = any>(url: string, config?: ExtendedAxiosRequestConfig): Promise<T>
  async delete<T = any>(urlOrConfig: string | ExtendedAxiosRequestConfig, config?: ExtendedAxiosRequestConfig): Promise<T> {
    if (typeof urlOrConfig === 'string') {
      return this.instance.delete(urlOrConfig, config)
    } else {
      return this.instance.delete(urlOrConfig.url || '', urlOrConfig)
    }
  }

  // 兼容 http.del 方法名
  del<T = any>(config: ExtendedAxiosRequestConfig): Promise<T>
  del<T = any>(url: string, config?: ExtendedAxiosRequestConfig): Promise<T>
  async del<T = any>(urlOrConfig: string | ExtendedAxiosRequestConfig, config?: ExtendedAxiosRequestConfig): Promise<T> {
    return this.delete<T>(urlOrConfig as any, config)
  }
  
  // 兼容 http.request 方法
  async request<T = any>(config: ExtendedAxiosRequestConfig): Promise<T> {
    return this.instance.request(config)
  }
}

// 导出单例实例
export const backendApi = new BackendApiClient()
