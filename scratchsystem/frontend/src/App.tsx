import React, { useState } from "react";
import {
  Box, TextField, Button, Select, MenuItem, Typography,
  Paper, Divider, InputLabel, FormHelperText
} from "@mui/material";
import { Link } from "react-router-dom";
import { SymbolEntry, SearchResult } from "./types";
import {
  createSymbol,
  searchSymbols,
  deleteSymbol
} from "./api";
import { SelectChangeEvent } from "@mui/material/Select";

const defaultForm: SymbolEntry = {
  category: "code",
  title: "",
  body: "",
  comment: "",
  due_date: "",
  priority: "medium",
  tags: [],
};

function App() {
  const [form, setForm] = useState<SymbolEntry>(defaultForm);
  const [searchTag, setSearchTag] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    if (name === "tags") {
      setForm({ ...form, tags: value.split(",").map(tag => tag.trim()) });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const handleSelectChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    if (name) {
      setForm({ ...form, [name]: value });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.category || !form.priority) {
      alert("Category and priority are required.");
      return;
    }
    await createSymbol(form);
    alert("Symbol created!");
    setForm(defaultForm);
    handleSearch();
  };

  const handleSearch = async () => {
    const data = await searchSymbols(searchTag);
    setResults(data);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this entry?")) return;
    await deleteSymbol(id);
    setResults(results.filter(r => r.id !== id));
  };

  return (
    <Box sx={{ bgcolor: "#f5f5f5", minHeight: "100vh", py: 4 }}>
      <Paper elevation={3} sx={{ maxWidth: 700, mx: "auto", p: 4 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Scratch System
        </Typography>

        <form onSubmit={handleSubmit}>
          <Box display="flex" flexDirection="column" gap={2}>
            <TextField label="Title" name="title" value={form.title} onChange={handleInputChange} fullWidth required />
            <TextField label="Body" name="body" value={form.body} onChange={handleInputChange} fullWidth multiline rows={4} />
            <TextField label="Comment" name="comment" value={form.comment} onChange={handleInputChange} fullWidth />
            <TextField type="datetime-local" name="due_date" value={form.due_date} onChange={handleInputChange} fullWidth InputLabelProps={{ shrink: true }} />
            <TextField label="Category" name="category" value={form.category} onChange={handleInputChange} fullWidth />
            <Box>
              <InputLabel id="priority-label">Priority</InputLabel>
              <Select
                labelId="priority-label"
                value={form.priority}
                name="priority"
                onChange={handleSelectChange}
                fullWidth
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
              <FormHelperText>High = urgent, Medium = planned, Low = reference</FormHelperText>
            </Box>
            <TextField label="Tags (comma-separated)" name="tags" value={form.tags.join(", ")} onChange={handleInputChange} fullWidth />
            <Button type="submit" variant="contained">Add Symbol</Button>
          </Box>
        </form>

        <Divider sx={{ my: 4 }} />

        <Box display="flex" gap={2}>
          <TextField label="Search by tag" value={searchTag} onChange={(e) => setSearchTag(e.target.value)} fullWidth />
          <Button onClick={handleSearch}>Search</Button>
        </Box>

        <Box mt={4}>
          {results.map(r => (
            <Paper key={r.id} sx={{ p: 2, mb: 2 }}>
              <Typography variant="h6">{r.title}</Typography>
              <Typography>Category: {r.category} | Priority: {r.priority}</Typography>
              <Typography>{r.body?.slice(0, 100)}...</Typography>
              <Box mt={2}>
                <Button component={Link} to={`/edit/${r.id}`} variant="outlined" size="small" sx={{ mr: 1 }}>Edit</Button>
                <Button variant="outlined" size="small" color="error" onClick={() => handleDelete(r.id)}>Delete</Button>
              </Box>
            </Paper>
          ))}
        </Box>
      </Paper>
    </Box>
  );
}

export default App;
