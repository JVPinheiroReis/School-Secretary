'use client'

import { FullScreenError } from '@/components/FullScreenError'
import { FullScreenLoading } from '@/components/FullScreenLoading'
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card'
import { useEvent } from '@/hooks/useEvent'

export default function EventsPage() {
    const { data, loading, error } = useEvent()

    if (loading) return <FullScreenLoading />
    if (error) return <FullScreenError error={error} />
    if (!data || data.length === 0)
        return <FullScreenError error="Nenhum evento encontrado." />

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-center mb-6">
                <div className="title-container">
                    <h1 className="title">Eventos</h1>
                    <p className="text-muted-foreground">
                        Confira os eventos e atividades futuras.
                    </p>
                </div>
                {/* TODO implement search field */}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {data.map((event) => (
                    <Card key={event.id}>
                        <CardHeader>
                            <CardTitle className="text-xl">
                                {event.title}
                            </CardTitle>
                            <CardDescription>
                                De {event.start_date} até {event.end_date}
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            <p className="font-medium text-sm">
                                <span className="text-muted-foreground">
                                    Local:
                                </span>{' '}
                                {event.location}
                            </p>
                            <p className="text-sm">{event.description}</p>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    )
}
