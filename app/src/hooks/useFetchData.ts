import { useCallback, useEffect, useState } from 'react'
import api from '@/services/api'

interface UseFetchDataOptions<T> {
    url: string
    initialData: T
    errorMessage: string
    generateMockData: () => T
    isEmpty?: (payload: T | null | undefined) => boolean
    normalizePayload?: (raw: unknown) => T
}

export function useFetchData<T>({
    url,
    initialData,
    errorMessage,
    generateMockData,
    isEmpty = (payload) =>
        !payload || (Array.isArray(payload) && payload.length === 0),
    normalizePayload = (raw) => raw as T,
}: UseFetchDataOptions<T>) {
    const [data, setData] = useState<T>(initialData)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const fetchData = useCallback(async () => {
        setLoading(true)
        setError(null)

        try {
            const response = await api.get<T>(url)
            let payload = normalizePayload(response.data)

            if (process.env.NODE_ENV === 'development' && isEmpty(payload)) {
                payload = generateMockData()
            }

            setData(payload)
        } catch {
            if (process.env.NODE_ENV === 'development') {
                setData(generateMockData())
                setError(null)
            } else {
                setData(initialData)
                setError(errorMessage)
            }
        } finally {
            setLoading(false)
        }
    }, [url, initialData, errorMessage, generateMockData, isEmpty, normalizePayload])

    useEffect(() => {
        void fetchData()
    }, [fetchData])

    return { data, setData, loading, error, setError, refetch: fetchData }
}

