import axios from 'axios'
import { setCookie } from 'cookies-next'
import { type NextRequest, NextResponse } from 'next/server'
import { ROUTES_INTERNAL } from '@/config'

const DJANGO_LOGIN_URL = ROUTES_INTERNAL.LOGIN

export async function POST(req: NextRequest) {
    try {
        const { email, password } = await req.json()

        const response = await axios.post(
            DJANGO_LOGIN_URL,
            {
                email,
                password,
            },
            {
                headers: {
                    'Content-Type': 'application/json',
                },
            },
        )

        const { access, refresh } = response.data

        const res = new NextResponse(
            JSON.stringify({ message: 'Login bem-sucedido' }),
            {
                status: 200,
                headers: { 'Content-Type': 'application/json' },
            },
        )

        setCookie('access', access, {
            req,
            res,
            path: '/',
            sameSite: 'lax',
            maxAge: 60 * 60,
        })

        setCookie('refresh', refresh, {
            req,
            res,
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            path: '/',
            sameSite: 'lax',
            maxAge: 60 * 60 * 24 * 30,
        })

        return res
    } catch (error: unknown) {
        console.error('Erro na rota /auth/login:', error)
        // Type guard to handle axios error properties
        const status =
            error &&
            typeof error === 'object' &&
            'response' in error &&
            error.response &&
            typeof error.response === 'object' &&
            'status' in error.response
                ? (error.response as { status?: number }).status || 500
                : 500
        const message =
            error &&
            typeof error === 'object' &&
            'response' in error &&
            error.response &&
            typeof error.response === 'object' &&
            'data' in error.response &&
            error.response.data &&
            typeof error.response.data === 'object' &&
            'detail' in error.response.data
                ? (error.response.data as { detail?: string }).detail ||
                  'Erro interno do servidor.'
                : 'Erro interno do servidor.'
        return new NextResponse(JSON.stringify({ error: message }), { status })
    }
}
