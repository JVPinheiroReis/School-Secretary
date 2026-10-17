import { useCallback } from 'react'
import { ROUTES } from '@/config'
import { FakeGroup, type GroupProps } from '@/types/group'
import { useFetchData } from './useFetchData'

const EMPTY_GROUPS: GroupProps[] = []

export function useGroups() {
    const generateMockGroups = useCallback((): GroupProps[] => {
        return Array.from({ length: 5 }, (_, i) => ({
            ...FakeGroup,
            id: i + 1,
            full_name: `Turma mock #${i + 1}`,
            short_name: `TM${i + 1}`,
        }))
    }, [])

    const {
        data: groups,
        loading,
        error,
        refetch: refetchGroups,
    } = useFetchData<GroupProps[]>({
        url: ROUTES.GROUPS,
        initialData: EMPTY_GROUPS,
        errorMessage: 'Não foi possível carregar as turmas.',
        generateMockData: generateMockGroups,
    })

    return { groups, loading, error, refetchGroups }
}
