```tsx
import React from 'react';
import { Table as DataTable, useTable } from '@tanstack/react-table';

interface TableProps {
  columns?: any[];
  data?: any[];
}

const TableComponent: React.FC<TableProps> = ({ columns, data }) => {
  const table = useTable({ columns, data });

  return (
    <div className="table">
      <DataTable {...table} />
    </div>
  );
};

const Table = () => {
  const columns = [
    { header: 'ID', accessorKey: 'id' },
    { header: 'Name', accessorKey: 'name' },
    { header: 'Age', accessorKey: 'age' },
  ];

  const data = [
    { id: 1, name: 'John Doe', age: 28 },
    { id: 2, name: 'Jane Smith', age: 34 },
  ];

  return <TableComponent columns={columns} data={data} />;
};

export default Table;
```