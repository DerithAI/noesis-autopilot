import React from 'react';
import { ColumnDef, useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table';

interface TableProps<TData extends Record<string, unknown>> {
  columns: ColumnDef<TData, unknown>[];
  data: TData[];
}

function DataTable<TData extends Record<string, unknown>>({ columns, data }: TableProps<TData>) {
  const table = useReactTable({
    columns,
    data,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <table>
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <th key={header.id}>
                {flexRender(header.column.columnDef.header, header.getContext())}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <tr key={row.id}>
            {row.getVisibleCells().map(cell => (
              <td key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

interface Person {
  id: number;
  name: string;
  age: number;
}

const Table: React.FC = () => {
  const columns: ColumnDef<Person, unknown>[] = [
    { header: 'ID', accessorKey: 'id' },
    { header: 'Name', accessorKey: 'name' },
    { header: 'Age', accessorKey: 'age' },
  ];

  const data: Person[] = [
    { id: 1, name: 'John Doe', age: 28 },
    { id: 2, name: 'Jane Smith', age: 34 },
  ];

  return <DataTable columns={columns} data={data} />;
};

export default Table;
