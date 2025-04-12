# SQL

## DDL

```sql
-- bank_account definition

CREATE TABLE bank_account (
    id INTEGER PRIMARY KEY,
    bank_name TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_number TEXT NOT NULL,
    routing_number TEXT,
    deposit_amount NUMERIC NULL,
    current_amount NUMERIC NOT NULL,
    maturity_date TEXT NOT NULL,
    current_rate TEXT NULL,
    comments TEXT NULL
);

CREATE UNIQUE INDEX bank_account_account_number_IDX ON bank_account (account_number, routing_number);
```


```sql
-- bond definition

CREATE TABLE bond (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    bond_name TEXT,
    bond_type TEXT,
    bond_term INTEGER,
    amount INTEGER,
    maturity_date INTEGER,
    apy NUMERIC,
    platform TEXT,
    comment TEXT
);
```



## DML

```sql
INSERT INTO bank_account
(id, bank_name, account_name, account_number, routing_number, deposit_amount, current_amount, maturity_date, current_rate, comments)
VALUES(0, '', '', '', '', 0, 0, '', '', '');
```

```sql
INSERT INTO bond
(id, bond_name, bond_type, bond_term, amount, maturity_date, apy, platform, comment)
VALUES(0, '', '', 0, 0, 0, 0, '', '');
```

```
select SUM(current_amount) from bank_accounts;


select SUM(current_amount) from bank_accounts
group by bank_name;


select SUM(current_amount) from bank_accounts
where bank_name = "synchrony";


select account_number ,current_amount from bank_accounts
where bank_name = "synchrony";


INSERT INTO bank_accounts
(id, bank_name, account_name, account_number, routing_number, deposit_amount, current_amount, maturity_date, current_rate, comments)
VALUES(null, 'synchrony', 'cd', '7001217389', '021213591', 0, 26796.71, '08/22/2025', '4.80', '');
```




