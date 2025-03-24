import React, { useState, useEffect } from 'react';
import {
  MaterialReactTable,
  useMaterialReactTable,
  MRT_ColumnDef,
} from 'material-react-table';
import { Button, TextField, Box, Paper } from '@mui/material';

interface Bond {
  id: number;
  bond_name: string;
  bond_type: string;
  bond_term: number;
  amount: number;
  maturity_date: string;
  apy: number;
  platform: string;
  comment: string;
}

const Bonds: React.FC = () => {
  const [bonds, setBonds] = useState<Bond[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [newBond, setNewBond] = useState<Partial<Bond>>({
    bond_name: '',
    bond_type: '',
    bond_term: 0,
    amount: 0,
    maturity_date: '',
    apy: 0,
    platform: '',
    comment: '',
  });

  // ✅ Fetch Bonds from API
  useEffect(() => {
    fetch('http://localhost:5000/api/bonds')
      .then((response) => response.json())
      .then((data: Bond[]) => {
        setBonds(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching bonds:', err);
        setLoading(false);
      });
  }, []);

  // ✅ Add a New Bond
  const addBond = async () => {
    if (!newBond.bond_name || !newBond.amount || !newBond.bond_term) {
      alert('Please fill in all required fields');
      return;
    }

    const bondData = {
      bond_name: newBond.bond_name,
      bond_type: newBond.bond_type || 'Unknown',
      bond_term: newBond.bond_term,
      amount: newBond.amount,
      maturity_date: newBond.maturity_date || new Date().toISOString().split('T')[0],
      apy: newBond.apy || 0,
      platform: newBond.platform || 'N/A',
      comment: newBond.comment || '',
    };

    const response = await fetch('http://localhost:5000/api/bonds', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bondData),
    });

    if (response.ok) {
      setNewBond({ bond_name: '', bond_type: '', bond_term: 0, amount: 0, maturity_date: '', apy: 0, platform: '', comment: '' });
      fetch('http://localhost:5000/api/bonds')
        .then((res) => res.json())
        .then(setBonds);
    } else {
      console.error("Failed to add bond");
    }
  };

  // ✅ Delete Bond
  const deleteBond = async (id: number) => {
    await fetch(`http://localhost:5000/api/bonds/${id}`, { method: 'DELETE' });
    setBonds(bonds.filter((bond) => bond.id !== id));
  };

  // ✅ Table Columns
  const columns: MRT_ColumnDef<Bond>[] = [
    { accessorKey: 'bond_name', header: 'Bond Name' },
    { accessorKey: 'bond_type', header: 'Bond Type' },
    { accessorKey: 'bond_term', header: 'Bond Term' },
    { accessorKey: 'amount', header: 'Amount ($)' },
    { accessorKey: 'maturity_date', header: 'Maturity Date' },
    { accessorKey: 'apy', header: 'APY (%)' },
    { accessorKey: 'platform', header: 'Platform' },
    { accessorKey: 'comment', header: 'Comment' },
    {
      accessorKey: 'id',
      header: 'Actions',
      Cell: ({ cell }: { cell: any }) => (
        <Button variant="contained" color="secondary" onClick={() => deleteBond(cell.getValue() as number)}>
          Delete
        </Button>
      ),
    },
  ];

  return (
    <Paper sx={{ padding: '20px' }}>
      <h2>Bonds</h2>

      {/* ✅ Input Fields for Adding a Bond */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '20px' }}>
        <TextField label="Bond Name" value={newBond.bond_name} onChange={(e) => setNewBond({ ...newBond, bond_name: e.target.value })} />
        <TextField label="Bond Type" value={newBond.bond_type} onChange={(e) => setNewBond({ ...newBond, bond_type: e.target.value })} />
        <TextField label="Bond Term" type="number" value={newBond.bond_term} onChange={(e) => setNewBond({ ...newBond, bond_term: Number(e.target.value) })} />
        <TextField label="Maturity Date" type="date" value={newBond.maturity_date || ""} onChange={(e) => setNewBond({ ...newBond, maturity_date: e.target.value })} />
        <TextField label="Maturity Date" type="date" value={newBond.maturity_date} onChange={(e) => setNewBond({ ...newBond, maturity_date: e.target.value })} />
        <TextField label="APY (%)" type="number" value={newBond.apy} onChange={(e) => setNewBond({ ...newBond, apy: Number(e.target.value) })} />
        <TextField label="Platform" value={newBond.platform} onChange={(e) => setNewBond({ ...newBond, platform: e.target.value })} />
        <TextField label="Comment" value={newBond.comment} onChange={(e) => setNewBond({ ...newBond, comment: e.target.value })} />
      </Box>

      <Button variant="contained" color="primary" onClick={addBond}>Add Bond</Button>

      {/* ✅ Display Bonds in Table */}
      <MaterialReactTable columns={columns} data={bonds} state={{ isLoading: loading }} />
    </Paper>
  );
};

export default Bonds;
