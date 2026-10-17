'use client'

import { Home, Inbox, type LucideIcon, User } from 'lucide-react'
import { useRouter } from 'next/navigation'
import type * as React from 'react'
import { NavMain } from '@/components/NavMain'
import { NavSecondary } from '@/components/NavSecondary'
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarRail,
} from '@/components/ui/sidebar'
import { NAVIGATION } from '@/config'
import { useUser } from '@/hooks/useUser'
import { logout } from '@/services/auth'
import { UserRole } from '@/types/user'
import { Button } from '../ui/button'

type NavItem = {
    title: string
    url: string
    icon: LucideIcon
    blockedRoles?: UserRole[]
}

type NavSecondaryChildItem = {
    title: string
    url: string
    blockedRoles?: UserRole[]
}

type NavSecondaryItem = {
    title: string
    url: string
    items: NavSecondaryChildItem[]
    blockedRoles?: UserRole[]
}

const data = {
    navMain: [
        {
            title: 'Início',
            url: NAVIGATION.DASHBOARD,
            icon: Home,
        },
        {
            title: 'Perfil',
            url: NAVIGATION.PROFILE,
            icon: User,
        },
        {
            title: 'Notificações',
            url: NAVIGATION.INBOX,
            icon: Inbox,
        },
    ],
    navSecondary: [
        {
            title: 'Anúncios',
            url: '#',
            items: [
                {
                    title: 'Atividades',
                    url: NAVIGATION.AGENDA,
                },
                {
                    title: 'Eventos',
                    url: NAVIGATION.EVENTS,
                },
                {
                    title: 'Aulas',
                    url: NAVIGATION.LESSONS,
                    blockedRoles: [UserRole.STAFF],
                },
            ],
        },
        {
            title: 'Professor',
            url: '#',
            blockedRoles: [UserRole.STUDENT, UserRole.GUARDIAN],
            items: [
                {
                    title: 'Planejamento Semanal',
                    url: NAVIGATION.WEEK_PLANNING,
                },
            ],
        },
        {
            title: 'Escola',
            url: '#',
            items: [
                {
                    title: 'Sobre',
                    url: NAVIGATION.ABOUT,
                },
                {
                    title: 'Recursos',
                    url: NAVIGATION.RESOURCES,
                    blockedRoles: [UserRole.GUARDIAN],
                },
                {
                    title: 'Painel administrativo',
                    url: NAVIGATION.ADMIN,
                    blockedRoles: [
                        UserRole.STUDENT,
                        UserRole.GUARDIAN,
                        UserRole.PROFESSOR,
                    ],
                },
            ],
        },
    ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
    const router = useRouter()
    const { data: user, loading } = useUser()

    async function handleClick() {
        await logout()
        router.push('/')
    }

    if (loading) {
        return null
    }

    const userRole = user?.role

    const filterNavMainItems = (items: NavItem[]): NavItem[] => {
        if (!userRole) return []
        return items.filter(
            (item) =>
                !item.blockedRoles || !item.blockedRoles.includes(userRole),
        )
    }

    const filterNavSecondaryChildItems = (
        items: NavSecondaryChildItem[],
    ): NavSecondaryChildItem[] => {
        if (!userRole) return []
        return items.filter(
            (item) =>
                !item.blockedRoles || !item.blockedRoles.includes(userRole),
        )
    }

    const filterNavSecondaryItems = (
        items: NavSecondaryItem[],
    ): NavSecondaryItem[] => {
        if (!userRole) return []
        return items
            .map((item) => ({
                ...item,
                items: filterNavSecondaryChildItems(item.items),
            }))
            .filter(
                (item) =>
                    (!item.blockedRoles ||
                        !item.blockedRoles.includes(userRole)) &&
                    item.items.length > 0,
            )
    }

    const filteredNavMain = filterNavMainItems(data.navMain)
    const filteredNavSecondary = filterNavSecondaryItems(data.navSecondary)

    return (
        <Sidebar {...props}>
            <SidebarContent>
                <NavMain items={filteredNavMain} />
                <NavSecondary items={filteredNavSecondary} />
            </SidebarContent>
            <SidebarRail />
            <SidebarFooter>
                <Button variant={'outline'} onClick={() => void handleClick()}>
                    Logout
                </Button>
            </SidebarFooter>
        </Sidebar>
    )
}
