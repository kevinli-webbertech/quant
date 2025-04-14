import React, { useState, useEffect } from 'react';
import {
  MaterialReactTable,
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

  const [errors, setErrors] = useState({
    bond_name: '',
    bond_term: '',
    apy: '',
  });

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

  const validateFields = () => {
    const newErrors = {
      bond_name: newBond.bond_name ? '' : 'Bond name is required',
      bond_term: newBond.bond_term && newBond.bond_term > 0 ? '' : 'Bond term must be > 0',
      apy: newBond.apy !== undefined && newBond.apy >= 0 ? '' : 'APY must be ≥ 0',
    };
    setErrors(newErrors);
    return !Object.values(newErrors).some((err) => err !== '');
  };

  const addBond = async () => {
    if (!validateFields()) return;

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
      setNewBond({
        bond_name: '',
        bond_type: '',
        bond_term: 0,
        amount: 0,
        maturity_date: '',
        apy: 0,
        platform: '',
        comment: '',
      });
      fetch('http://localhost:5000/api/bonds')
        .then((res) => res.json())
        .then(setBonds);
    } else {
      console.error('Failed to add bond');
    }
  };

  const deleteBond = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this bond?')) {
      await fetch(`http://localhost:5000/api/bonds/${id}`, { method: 'DELETE' });
      setBonds(bonds.filter((bond) => bond.id !== id));
    }
  };

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
        <Button
          variant="contained"
          color="secondary"
          onClick={() => deleteBond(cell.getValue() as number)}
        >
          Delete
        </Button>
      ),
    },
  ];

  return (
    <Paper sx={{ padding: '20px' }}>
      <h2>Bonds</h2>

      <Box sx={{ display: 'flex', gap: '10px', marginBottom: '10px', flexWrap: 'wrap' }}>
        <TextField
          label="Bond Name"
          value={newBond.bond_name}
          onChange={(e) => {
            const value = e.target.value;
            setNewBond({ ...newBond, bond_name: value });
            setErrors((prev) => ({ ...prev, bond_name: value ? '' : 'Bond name is required' }));
          }}
          error={!!errors.bond_name}
          helperText={errors.bond_name}
        />
        <TextField
          label="Bond Type"
          value={newBond.bond_type}
          onChange={(e) => setNewBond({ ...newBond, bond_type: e.target.value })}
        />
        <TextField
          label="Bond Term"
          type="number"
          inputProps={{ min: 0 }}
          value={newBond.bond_term}
          onChange={(e) => {
            const value = Number(e.target.value);
            setNewBond({ ...newBond, bond_term: value });
            setErrors((prev) => ({
              ...prev,
              bond_term: value > 0 ? '' : 'Bond term must be > 0',
            }));
          }}
          error={!!errors.bond_term}
          helperText={errors.bond_term}
        />
        <TextField
          label="Maturity Date"
          type="date"
          value={newBond.maturity_date || ''}
          onChange={(e) => setNewBond({ ...newBond, maturity_date: e.target.value })}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="APY (%)"
          type="number"
          inputProps={{ min: 0, step: 0.01 }}
          value={newBond.apy}
          onChange={(e) => {
            const value = Number(e.target.value);
            setNewBond({ ...newBond, apy: value });
            setErrors((prev) => ({
              ...prev,
              apy: value >= 0 ? '' : 'APY must be ≥ 0',
            }));
          }}
          error={!!errors.apy}
          helperText={errors.apy}
        />
        <TextField
          label="Amount ($)"
          type="number"
          inputProps={{ min: 0 }}
          value={newBond.amount}
          onChange={(e) => setNewBond({ ...newBond, amount: Number(e.target.value) })}
        />
        <TextField
          label="Platform"
          value={newBond.platform}
          onChange={(e) => setNewBond({ ...newBond, platform: e.target.value })}
        />
        <TextField
          label="Comment"
          value={newBond.comment}
          onChange={(e) => setNewBond({ ...newBond, comment: e.target.value })}
        />
        <Button variant="contained" color="primary" onClick={addBond}>
          Add Bond
        </Button>
      </Box>

      <MaterialReactTable columns={columns} data={bonds} state={{ isLoading: loading }} />
    </Paper>
  );
};

export default Bonds;
