'use client'

import { FullScreenError } from '@/components/FullScreenError'
import { FullScreenLoading } from '@/components/FullScreenLoading'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card'
import { useNotification } from '@/hooks/useNotification'

const notificationTypeLabels: Record<string, string> = {
    GRADE: 'Nota',
    ABSENCE: 'Falta',
    WARNING: 'Advertência',
    SUSPENSION: 'Suspensão',
    EVENT: 'Evento',
    ASSIGNMENT: 'Trabalho',
    EXAM: 'Prova',
    PAYMENT: 'Pagamento',
    GENERAL: 'Geral',
}

const notificationTypeColors: Record<string, string> = {
    GRADE: 'bg-blue-500',
    ABSENCE: 'bg-orange-500',
    WARNING: 'bg-yellow-500',
    SUSPENSION: 'bg-red-500',
    EVENT: 'bg-green-500',
    ASSIGNMENT: 'bg-purple-500',
    EXAM: 'bg-pink-500',
    PAYMENT: 'bg-cyan-500',
    GENERAL: 'bg-gray-500',
}

export default function InboxPage() {
    const { data, loading, error, markAsRead, markAllAsRead } =
        useNotification()

    if (loading) return <FullScreenLoading />
    if (error) return <FullScreenError error={error} />

    const unreadCount = data.filter((n) => !n.read).length

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-center mb-6">
                <div className="title-container">
                    <h1 className="title">Caixa de Entrada</h1>
                    <p className="text-muted-foreground">
                        {unreadCount > 0
                            ? `Você tem ${unreadCount} notificação${unreadCount > 1 ? 'ões' : ''} não lida${unreadCount > 1 ? 's' : ''}`
                            : 'Todas as notificações foram lidas'}
                    </p>
                </div>
                {unreadCount > 0 && (
                    <Button onClick={markAllAsRead} variant="outline">
                        Marcar todas como lidas
                    </Button>
                )}
            </div>

            {data.length === 0 ? (
                <Card>
                    <CardContent className="py-8">
                        <p className="text-center text-muted-foreground">
                            Nenhuma notificação encontrada.
                        </p>
                    </CardContent>
                </Card>
            ) : (
                <div className="space-y-4">
                    {data.map((notification) => (
                        <Card
                            key={notification.id}
                            className={`${
                                !notification.read
                                    ? 'border-l-4 border-l-primary'
                                    : 'opacity-75'
                            }`}
                        >
                            <CardHeader>
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Badge
                                                className={`${
                                                    notificationTypeColors[
                                                        notification
                                                            .notification_type
                                                    ] || 'bg-gray-500'
                                                } text-white`}
                                            >
                                                {notificationTypeLabels[
                                                    notification
                                                        .notification_type
                                                ] || 'Geral'}
                                            </Badge>
                                            {!notification.read && (
                                                <Badge variant="outline">
                                                    Nova
                                                </Badge>
                                            )}
                                        </div>
                                        <CardTitle className="text-lg">
                                            {notification.title}
                                        </CardTitle>
                                        <CardDescription>
                                            {new Date(
                                                notification.created_at,
                                            ).toLocaleString('pt-BR')}
                                        </CardDescription>
                                    </div>
                                    {!notification.read && (
                                        <Button
                                            onClick={() =>
                                                markAsRead(notification.id)
                                            }
                                            variant="ghost"
                                            size="sm"
                                        >
                                            Marcar como lida
                                        </Button>
                                    )}
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm whitespace-pre-wrap break-words">
                                    {notification.message}
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    )
}
