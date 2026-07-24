import { useState } from 'react';
import {
  ColumnDef,
  SortingState,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

interface TableProps<TData extends object> {
  columns: ColumnDef<TData, unknown>[];
  data: TData[];
  /** Optional class applied to the <table> element (e.g. from a CSS module). */
  className?: string;
}

/** Per-column extras carried via columnDef.meta (kept untyped to avoid module augmentation). */
function metaClassName(meta: unknown): string | undefined {
  return (meta as { className?: string } | undefined)?.className;
}

function DataTable<TData extends object>({ columns, data, className }: TableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    columns,
    data,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <table className={className}>
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => {
              const canSort = header.column.getCanSort();
              const sorted = header.column.getIsSorted(); // false | 'asc' | 'desc'
              return (
                <th
                  key={header.id}
                  className={metaClassName(header.column.columnDef.meta)}
                  aria-sort={sorted === 'asc' ? 'ascending' : sorted === 'desc' ? 'descending' : undefined}
                  tabIndex={canSort ? 0 : undefined}
                  onClick={canSort ? header.column.getToggleSortingHandler() : undefined}
                  onKeyDown={
                    canSort
                      ? e => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            header.column.toggleSorting();
                          }
                        }
                      : undefined
                  }
                  style={canSort ? { cursor: 'pointer', userSelect: 'none' } : undefined}
                >
                  {header.isPlaceholder
                    ? null
                    : flexRender(header.column.columnDef.header, header.getContext())}
                  {canSort && (
                    <span aria-hidden="true" style={{ opacity: sorted ? 1 : 0.35, marginLeft: 4 }}>
                      {sorted === 'asc' ? '▲' : sorted === 'desc' ? '▼' : '⇅'}
                    </span>
                  )}
                </th>
              );
            })}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <tr key={row.id}>
            {row.getVisibleCells().map(cell => (
              <td key={cell.id} className={metaClassName(cell.column.columnDef.meta)}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default DataTable;
