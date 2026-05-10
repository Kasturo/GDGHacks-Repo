import { Container, CssBaseline, Typography, Button } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    mode: 'light',
  },
});

function App() {
  const callApi = async () => {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/health`);
    const data = await response.json();
    console.log(data);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container sx={{ mt: 5 }}>
        <Typography variant="h3">EC2-Ready App</Typography>
        <Button variant="contained" onClick={callApi}>Test API</Button>
      </Container>
    </ThemeProvider>
  );
}
export default App;