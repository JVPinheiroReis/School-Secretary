import axios from 'axios'
import { getCookie, setCookie } from 'cookies-next'
import { NAVIGATION } from '@/config'

const api = axios.create()

let isRefreshing = false
let failedQueue: Array<{
    resolve: (token: string) => void
    reject: (error: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null = null) => {
    for (const prom of failedQueue) {
        if (error) {
            prom.reject(error)
        } else if (token) {
            prom.resolve(token)
        }
    }
    failedQueue = []
}

api.interceptors.request.use(
    (config) => {
        const token = getCookie('access')
        if (token) {
            if (!config.headers) {
                config.headers = axios.AxiosHeaders.from({})
            }
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error),
)

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config

        // Handle 401 Unauthorized - try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise<string>((resolve, reject) => {
                    failedQueue.push({ resolve, reject })
                }).then((token) => {
                    if (!originalRequest.headers) {
                        originalRequest.headers = axios.AxiosHeaders.from({})
                    }
                    originalRequest.headers.Authorization = `Bearer ${token}`
                    return api(originalRequest)
                })
            }

            originalRequest._retry = true
            isRefreshing = true

            try {
                const response = await axios.post(NAVIGATION.AUTH_REFRESH)
                const { access } = response.data

                setCookie('access', access, { path: '/', sameSite: 'lax' })

                if (typeof window !== 'undefined') {
                    window.dispatchEvent(new CustomEvent('tokenRefreshed'))
                }

                processQueue(null, access)

                if (!originalRequest.headers) {
                    originalRequest.headers = axios.AxiosHeaders.from({})
                }
                originalRequest.headers.Authorization = `Bearer ${access}`

                return api(originalRequest)
            } catch (refreshError) {
                processQueue(refreshError, null)
                console.error('Refresh token failed', refreshError)
                if (typeof window !== 'undefined') {
                    window.location.href = '/'
                }
                return Promise.reject(refreshError)
            } finally {
                isRefreshing = false
            }
        }

        // Handle 403 Forbidden - redirect to login
        if (error.response?.status === 403) {
            console.error('Access forbidden - redirecting to login')
            if (typeof window !== 'undefined') {
                window.location.href = '/'
            }
        }

        return Promise.reject(error)
    },
)

export default api
