import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Switch, FormControlLabel, Box } from '@mui/material';
import BankAccounts from './BankAccounts';
import Bonds from './Bonds';

const App: React.FC = () => {
  // ✅ State for Dark Mode
  const [darkMode, setDarkMode] = useState<boolean>(false);

  // ✅ Create light & dark themes
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ padding: '20px', textAlign: 'center' }}>
        <h1>Investment Portfolio</h1>

        {/* ✅ Dark Mode Toggle */}
        <FormControlLabel
          control={
            <Switch
              checked={darkMode}
              onChange={() => setDarkMode(!darkMode)}
            />
          }
          label={darkMode ? '🌙 Dark Mode' : '☀️ Light Mode'}
        />

        {/* ✅ Tables with spacing */}
        <Box sx={{ marginBottom: '40px' }}>
          <BankAccounts />
        </Box>
        <Box>
          <Bonds />
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default App;
