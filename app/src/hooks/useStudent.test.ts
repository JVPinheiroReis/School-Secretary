import { renderHook, waitFor } from '@testing-library/react'
import { ROUTES } from '@/config'
import api from '@/services/api'
import { createFakeStudent, FakeStudent } from '@/types/student'
import { useStudent } from './useStudent'

// Mock the API service
vi.mock('@/services/api')

describe('useStudent', () => {
    const originalNodeEnv = process.env.NODE_ENV

    beforeEach(() => {
        // Reset mocks before each test
        vi.clearAllMocks()
        process.env.NODE_ENV = originalNodeEnv // Reset NODE_ENV
    })

    afterAll(() => {
        process.env.NODE_ENV = originalNodeEnv
    })

    it('should return initial loading state', () => {
        const { result } = renderHook(() => useStudent())

        expect(result.current.loading).toBe(true)
        expect(result.current.data).toBeNull()
        expect(result.current.error).toBeNull()
    })

    it('should fetch student data successfully', async () => {
        const mockStudent = createFakeStudent()
        ;(api.get as vi.Mock).mockResolvedValueOnce({ data: mockStudent })

        const { result } = renderHook(() => useStudent())

        await waitFor(() => expect(result.current.loading).toBe(false))

        expect(result.current.data).toEqual(mockStudent)
        expect(result.current.error).toBeNull()
        expect(api.get).toHaveBeenCalledWith(ROUTES.STUDENTS)
    })

    it('should handle API error in development by returning FakeStudent', async () => {
        process.env.NODE_ENV = 'development'
        ;(api.get as vi.Mock).mockRejectedValueOnce(new Error('API Error'))

        const { result } = renderHook(() => useStudent())

        await waitFor(() => expect(result.current.loading).toBe(false))

        expect(result.current.data).toEqual(FakeStudent)
        expect(result.current.error).toBeNull()
    })

    it('should handle API error in production by returning error message', async () => {
        process.env.NODE_ENV = 'production'
        ;(api.get as vi.Mock).mockRejectedValueOnce(new Error('API Error'))

        const { result } = renderHook(() => useStudent())

        await waitFor(() => expect(result.current.loading).toBe(false))

        expect(result.current.data).toBeNull()
        expect(result.current.error).toBe(
            'Não foi possível carregar as informações do estudante.',
        )
    })

    it('should handle empty data in development by returning FakeStudent', async () => {
        process.env.NODE_ENV = 'development'
        ;(api.get as vi.Mock).mockResolvedValueOnce({ data: null })

        const { result } = renderHook(() => useStudent())

        await waitFor(() => expect(result.current.loading).toBe(false))

        expect(result.current.data).toEqual(FakeStudent)
        expect(result.current.error).toBeNull()
    })

    it('should refetch student data when refetch is called', async () => {
        const mockStudent1 = createFakeStudent()
        const mockStudent2 = createFakeStudent()

        ;(api.get as vi.Mock)
            .mockResolvedValueOnce({ data: mockStudent1 })
            .mockResolvedValueOnce({ data: mockStudent2 })

        const { result } = renderHook(() => useStudent())

        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(result.current.data).toEqual(mockStudent1)

        result.current.refetch()

        await waitFor(() => expect(result.current.loading).toBe(false))
        expect(result.current.data).toEqual(mockStudent2)
    })
})
