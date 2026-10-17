import { useCallback } from 'react'
import { ROUTES } from '@/config'
import { type EventProps, FakeEvent } from '@/types/event'
import { useFetchData } from './useFetchData'

const EMPTY_EVENTS: EventProps[] = []
const normalizeArray = (raw: unknown): EventProps[] =>
    Array.isArray(raw) ? raw : []

export function useEvent() {
    const generateMockEvents = useCallback((): EventProps[] => {
        return Array.from({ length: 10 }, (_, i) => ({
            ...FakeEvent,
            id: i + 1,
            title: `Evento mock #${i + 1}`,
            description: `Descrição do evento mock #${i + 1}`,
        }))
    }, [])

    const { data, loading, error, refetch } = useFetchData<EventProps[]>({
        url: ROUTES.EVENTS,
        initialData: EMPTY_EVENTS,
        errorMessage: 'Não foi possível carregar os eventos.',
        generateMockData: generateMockEvents,
        normalizePayload: normalizeArray,
    })

    return { data, loading, error, refetch }
}
