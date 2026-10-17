import { type NextRequest, NextResponse } from 'next/server'

const protectedRoutes = [
    '/dashboard',
    '/profile',
    '/inbox',
    '/agenda',
    '/events',
    '/lessons',
    '/groups',
    '/week-planning',
    '/resources',
]
const loginRoute = '/'

export function middleware(request: NextRequest) {
    if (process.env.NODE_ENV === 'development') {
        return NextResponse.next()
    }

    const { pathname } = request.nextUrl

    const accessToken = request.cookies.get('access')?.value

    const isProtectedRoute = protectedRoutes.some((route) =>
        pathname.startsWith(route),
    )

    if (isProtectedRoute && !accessToken) {
        const loginUrl = new URL(loginRoute, request.url)
        loginUrl.searchParams.set('from', pathname)
        return NextResponse.redirect(loginUrl)
    }

    return NextResponse.next()
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
