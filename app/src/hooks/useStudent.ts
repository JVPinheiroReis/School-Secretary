import { useCallback } from 'react'
import { ROUTES } from '@/config'
import { FakeStudent, type StudentProps } from '@/types/student'
import { useFetchData } from './useFetchData'

const normalizeStudent = (raw: unknown): StudentProps | null =>
    (raw as StudentProps) || null

export function useStudent() {
    const generateMockStudents = useCallback((): StudentProps => {
        return { ...FakeStudent }
    }, [])

    const { data, loading, error, refetch } = useFetchData<StudentProps | null>(
        {
            url: ROUTES.STUDENTS,
            initialData: null,
            errorMessage:
                'Não foi possível carregar as informações do estudante.',
            generateMockData: generateMockStudents,
            normalizePayload: normalizeStudent,
        },
    )

    return { data, loading, error, refetch }
}
