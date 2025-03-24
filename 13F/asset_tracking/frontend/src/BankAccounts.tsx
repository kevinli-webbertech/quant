import React, { useState, useEffect } from 'react';
import {
  MaterialReactTable,
  useMaterialReactTable,
  MRT_ColumnDef,
} from 'material-react-table';
import { Button, TextField, Box, Paper } from '@mui/material';

interface BankAccount {
  id: number;
  bank_name: string;
  account_name: string;
  account_number: string;
  routing_number: string;
  deposit_amount: number;
  current_amount: number;
  maturity_date: string;
  current_rate: string;
  comments: string;
}

const BankAccounts: React.FC = () => {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [newAccount, setNewAccount] = useState<Partial<BankAccount>>({
    bank_name: '',
    account_name: '',
    account_number: '',
    routing_number: '',
    deposit_amount: 0,
    current_amount: 0,
    maturity_date: '',
    current_rate: '',
    comments: '',
  });

  // ✅ Fetch Bank Accounts from Backend
  useEffect(() => {
    fetch('http://localhost:5000/api/bank_accounts')
      .then((response) => response.json())
      .then((data: BankAccount[]) => {
        setAccounts(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching bank accounts:', err);
        setLoading(false);
      });
  }, []);

  // ✅ Add New Bank Account (Matching SQL Schema)
  const addAccount = async () => {
    if (!newAccount.bank_name || !newAccount.account_name || !newAccount.account_number) {
      alert('Please fill in all required fields');
      return;
    }

    const response = await fetch('http://localhost:5000/api/bank_accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newAccount),
    });

    if (response.ok) {
      setNewAccount({ bank_name: '', account_name: '', account_number: '', routing_number: '', deposit_amount: 0, current_amount: 0, maturity_date: '', current_rate: '', comments: '' });
      fetch('http://localhost:5000/api/bank_accounts')
        .then((res) => res.json())
        .then(setAccounts);
    }
  };

  // ✅ Delete Bank Account
  const deleteAccount = async (id: number) => {
    await fetch(`http://localhost:5000/api/bank_accounts/${id}`, { method: 'DELETE' });
    setAccounts(accounts.filter((account) => account.id !== id));
  };

  // ✅ Table Columns (Matching SQL Schema)
  const columns: MRT_ColumnDef<BankAccount>[] = [
    { accessorKey: 'bank_name', header: 'Bank Name' },
    { accessorKey: 'account_name', header: 'Account Name' },
    { accessorKey: 'account_number', header: 'Account Number' },
    { accessorKey: 'routing_number', header: 'Routing Number' },
    { accessorKey: 'deposit_amount', header: 'Deposit Amount ($)' },
    { accessorKey: 'current_amount', header: 'Current Amount ($)' },
    { accessorKey: 'maturity_date', header: 'Maturity Date' },
    { accessorKey: 'current_rate', header: 'Current Rate (%)' },
    { accessorKey: 'comments', header: 'Comments' },
    {
      accessorKey: 'id',
      header: 'Actions',
      Cell: ({ cell }: { cell: any }) => (
        <Button variant="contained" color="secondary" onClick={() => deleteAccount(cell.getValue() as number)}>
          Delete
        </Button>
      ),
    },
  ];

  return (
    <Paper sx={{ padding: '20px' }}>
      <h2>Bank Accounts</h2>

      {/* ✅ Input Fields (Keep SQL Structure) */}
      <Box sx={{ display: 'flex', gap: '10px', marginBottom: '10px', flexWrap: 'wrap' }}>
        <TextField label="Bank Name" value={newAccount.bank_name} onChange={(e) => setNewAccount({ ...newAccount, bank_name: e.target.value })} />
        <TextField label="Account Name" value={newAccount.account_name} onChange={(e) => setNewAccount({ ...newAccount, account_name: e.target.value })} />
        <TextField label="Account Number" value={newAccount.account_number} onChange={(e) => setNewAccount({ ...newAccount, account_number: e.target.value })} />
        <TextField label="Routing Number" value={newAccount.routing_number} onChange={(e) => setNewAccount({ ...newAccount, routing_number: e.target.value })} />
        <TextField label="Deposit Amount" type="number" value={newAccount.deposit_amount} onChange={(e) => setNewAccount({ ...newAccount, deposit_amount: Number(e.target.value) })} />
        <TextField label="Current Amount" type="number" value={newAccount.current_amount} onChange={(e) => setNewAccount({ ...newAccount, current_amount: Number(e.target.value) })} />
        <TextField label="Maturity Date" value={newAccount.maturity_date} onChange={(e) => setNewAccount({ ...newAccount, maturity_date: e.target.value })} />
        <TextField label="Current Rate" value={newAccount.current_rate} onChange={(e) => setNewAccount({ ...newAccount, current_rate: e.target.value })} />
        <TextField label="Comments" value={newAccount.comments} onChange={(e) => setNewAccount({ ...newAccount, comments: e.target.value })} />
        <Button variant="contained" color="primary" onClick={addAccount}>Add Account</Button>
      </Box>

      {/* ✅ Table Display */}
      <MaterialReactTable columns={columns} data={accounts} state={{ isLoading: loading }} />
    </Paper>
  );
};

export default BankAccounts;
