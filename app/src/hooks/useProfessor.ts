import { useCallback } from 'react'
import { ROUTES } from '@/config'
import { FakeProfessor, type ProfessorProps } from '@/types/professor'
import { useFetchData } from './useFetchData'

const normalizeProfessor = (raw: unknown): ProfessorProps | null =>
    (raw as ProfessorProps) || null

export function useProfessor() {
    const generateMockProfessors = useCallback((): ProfessorProps => {
        return { ...FakeProfessor }
    }, [])

    const { data, loading, error, refetch } =
        useFetchData<ProfessorProps | null>({
            url: ROUTES.PROFESSORS,
            initialData: null,
            errorMessage:
                'Não foi possível carregar as informações do professor.',
            generateMockData: generateMockProfessors,
            normalizePayload: normalizeProfessor,
        })

    return { data, loading, error, refetch }
}
