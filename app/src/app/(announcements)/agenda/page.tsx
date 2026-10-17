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
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { useAgenda } from '@/hooks/useAgenda'

export default function AgendaPage() {
    const { data, loading, error } = useAgenda()

    if (loading) return <FullScreenLoading />
    if (error) return <FullScreenError error={error} />
    if (data.length === 0)
        return (
            <FullScreenError error="Nenhuma informação encontrada na agenda." />
        )

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Agenda</CardTitle>
                    <CardDescription>
                        Confira os próximos eventos e atividades.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <Table className="w-full">
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Título</TableHead>
                                    <TableHead>Descrição</TableHead>
                                    <TableHead>Data</TableHead>
                                    <TableHead>Hora</TableHead>
                                    <TableHead>Matéria</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {data.map((item) => (
                                    <TableRow key={item.id}>
                                        <TableCell className="font-medium whitespace-normal max-w-20">
                                            {item.title}
                                        </TableCell>
                                        <TableCell className="whitespace-normal max-w-36">
                                            {item.description}
                                        </TableCell>
                                        <TableCell>{item.date}</TableCell>
                                        <TableCell>{item.time}</TableCell>
                                        <TableCell>
                                            {item.subject_details?.full_name}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
