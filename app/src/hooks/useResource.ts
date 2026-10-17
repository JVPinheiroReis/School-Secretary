import { useCallback } from 'react'
import { ROUTES } from '@/config'
import {
    createFakeResource,
    createFakeResourceLoan,
    type ResourceLoanProps,
    type ResourceProps,
} from '@/types/resources'
import { useFetchData } from './useFetchData'

const EMPTY_RESOURCES: ResourceProps[] = []
const EMPTY_LOANS: ResourceLoanProps[] = []

export function useResources() {
    const generateMockResources = useCallback((): ResourceProps[] => {
        return Array.from({ length: 5 }, (_, i) => ({
            ...createFakeResource(),
            id: i + 1,
            name: `Recurso mock #${i + 1}`,
        }))
    }, [])

    const {
        data: resources,
        loading,
        error,
        refetch: refetchResources,
    } = useFetchData<ResourceProps[]>({
        url: ROUTES.RESOURCES,
        initialData: EMPTY_RESOURCES,
        errorMessage: 'Não foi possível carregar os recursos.',
        generateMockData: generateMockResources,
    })

    return { resources, loading, error, refetchResources }
}

export function useResourceLoans() {
    const generateMockResourceLoans = useCallback((): ResourceLoanProps[] => {
        return Array.from({ length: 5 }, (_, i) => ({
            ...createFakeResourceLoan(),
            id: i + 1,
        }))
    }, [])

    const {
        data: resourceLoans,
        loading,
        error,
        refetch: refetchResourceLoans,
    } = useFetchData<ResourceLoanProps[]>({
        url: ROUTES.RESOURCE_LOANS,
        initialData: EMPTY_LOANS,
        errorMessage: 'Não foi possível carregar os empréstimos de recursos.',
        generateMockData: generateMockResourceLoans,
    })

    return {
        resourceLoans,
        loading,
        error,
        refetchResourceLoans,
    }
}
