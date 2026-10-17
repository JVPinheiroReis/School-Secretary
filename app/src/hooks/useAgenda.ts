import { useCallback } from 'react'
import { ROUTES } from '@/config'
import { type AgendaItemProps, FakeAgendaItem } from '@/types/agendaItem'
import { useFetchData } from './useFetchData'

const EMPTY_AGENDA: AgendaItemProps[] = []
const normalizeArray = (raw: unknown): AgendaItemProps[] =>
    Array.isArray(raw) ? raw : []

export function useAgenda() {
    const generateMockAgenda = useCallback((): AgendaItemProps[] => {
        return Array.from({ length: 10 }, (_, i) => ({
            ...FakeAgendaItem,
            id: i + 1,
            title: `Evento mock #${i + 1}`,
        }))
    }, [])

    const { data, loading, error, refetch } = useFetchData<AgendaItemProps[]>({
        url: ROUTES.AGENDA,
        initialData: EMPTY_AGENDA,
        errorMessage: 'Não foi possível carregar a agenda.',
        generateMockData: generateMockAgenda,
        normalizePayload: normalizeArray,
    })

    return { data, loading, error, refetch }
}
