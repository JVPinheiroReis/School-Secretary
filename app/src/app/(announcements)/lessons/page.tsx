'use client'

import { useState } from 'react'
import { FullScreenError } from '@/components/FullScreenError'
import { FullScreenLoading } from '@/components/FullScreenLoading'
import SelectObject from '@/components/SelectObject'
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
import { useGroups } from '@/hooks/useGroup'
import { useGroupLessons } from '@/hooks/useGroupLesson'

export default function LessonsPage() {
    const [selectedGroup, setSelectedGroup] = useState<number>()
    const { groups, loading: loadingGroups, error: errorGroups } = useGroups()
    const {
        data: lessons,
        loading: loadingLessons,
        error: errorLessons,
        refetchLessons,
    } = useGroupLessons(selectedGroup)

    const handleSelectedGroup = (value?: number) => {
        setSelectedGroup(value)
        refetchLessons()
    }

    if (loadingGroups || loadingLessons) return <FullScreenLoading />

    if (errorGroups) return <FullScreenError error={errorGroups} />

    if (errorLessons) return <FullScreenError error={errorLessons} />

    if (selectedGroup && (!lessons || lessons.length === 0))
        return <FullScreenError error="Nenhuma aula encontrada." />

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 p-6">
                    <div>
                        <CardTitle>Horários da Turma</CardTitle>
                        <CardDescription className="pt-1">
                            Selecione uma turma para visualizar a grade de
                            horários.
                        </CardDescription>
                    </div>
                    <SelectObject
                        options={groups}
                        onSelect={handleSelectedGroup}
                    />
                </CardHeader>

                {selectedGroup && lessons && lessons.length > 0 && (
                    <CardContent className="overflow-x-auto">
                        <Table className="w-full">
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Dia</TableHead>
                                    <TableHead className="text-center">
                                        1° Horário
                                    </TableHead>
                                    <TableHead className="text-center">
                                        2° Horário
                                    </TableHead>
                                    <TableHead className="text-center">
                                        3° Horário
                                    </TableHead>
                                    <TableHead className="text-center">
                                        4° Horário
                                    </TableHead>
                                    <TableHead className="text-center">
                                        5° Horário
                                    </TableHead>
                                    <TableHead className="text-center">
                                        6° Horário
                                    </TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {lessons.map(({ day, lessons }) => (
                                    <TableRow key={day}>
                                        <TableCell className="font-medium">
                                            {day}
                                        </TableCell>
                                        {lessons.map((lesson) => (
                                            <TableCell
                                                key={
                                                    lesson?.id || Math.random()
                                                }
                                                className="text-center"
                                            >
                                                {lesson?.subject_details
                                                    ?.short_name || '-'}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </CardContent>
                )}
            </Card>
        </div>
    )
}
