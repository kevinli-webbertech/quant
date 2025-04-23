// App.tsx
import React, { useState } from "react";
import {
  Box, TextField, Button, Select, MenuItem, Typography,
  Paper, Divider, InputLabel, FormHelperText, IconButton, Collapse
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import { Link } from "react-router-dom";
import { SymbolEntry, SearchResult } from "./types";
import {
  createSymbol, searchSymbols, deleteSymbol
} from "./api";
import { SelectChangeEvent } from "@mui/material/Select";

const defaultForm: SymbolEntry = {
  category: "code",
  title: "",
  body: "",
  comment: "",
  due_date: new Date().toISOString().slice(0, 16),
  priority: "medium",
  tags: [],
};

function App() {
  const [form, setForm] = useState<SymbolEntry>(defaultForm);
  const [errors, setErrors] = useState({ title: false, tags: false });
  const [searchTag, setSearchTag] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const validateField = (name: string, value: string) => {
    if (name === "title") {
      setErrors(prev => ({ ...prev, title: value.trim() === "" }));
    } else if (name === "tags") {
      setErrors(prev => ({ ...prev, tags: value.trim() === "" }));
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    validateField(name, value);
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
    if (form.title.trim() === "" || form.tags.length === 0) return;
    await createSymbol(form);
    setForm(defaultForm);
    setErrors({ title: false, tags: false });
    handleSearch();
  };

  const handleSearch = async () => {
    const data = await searchSymbols(searchTag);
    setResults(data.map(r => ({ ...r, full: undefined })));
    setExpandedId(null);
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
            <TextField
              label="Title"
              name="title"
              value={form.title}
              onChange={handleInputChange}
              error={errors.title}
              helperText={errors.title ? "Title is required." : ""}
              fullWidth
              required
            />
            <TextField label="Body" name="body" value={form.body} onChange={handleInputChange} fullWidth multiline rows={4} />
            <TextField label="Comment" name="comment" value={form.comment} onChange={handleInputChange} fullWidth />
            <TextField
              type="datetime-local"
              name="due_date"
              value={form.due_date}
              onChange={handleInputChange}
              fullWidth
              label="Event Time"
              InputLabelProps={{ shrink: true }}
            />
            <Box>
              <InputLabel id="category-label">Category</InputLabel>
              <Select
                labelId="category-label"
                name="category"
                value={form.category}
                onChange={handleSelectChange}
                fullWidth
              >
                <MenuItem value="code">Code</MenuItem>
                <MenuItem value="news">News</MenuItem>
                <MenuItem value="indicator">Indicator</MenuItem>
              </Select>
            </Box>
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
            </Box>
            <TextField
              label="Tags (comma-separated)"
              name="tags"
              value={form.tags.join(", ")}
              onChange={handleInputChange}
              error={errors.tags}
              helperText={errors.tags ? "Please enter at least one tag." : ""}
              fullWidth
            />
            <Button type="submit" variant="contained">Add Symbol</Button>
          </Box>
        </form>

        <Divider sx={{ my: 4 }} />

        <Box display="flex" gap={2}>
          <TextField label="Search by tag" value={searchTag} onChange={(e) => setSearchTag(e.target.value)} fullWidth />
          <Button onClick={handleSearch}>Search</Button>
        </Box>

        <Box mt={4}>
          {results.map((r) => (
            <Paper key={r.id} sx={{ p: 2, mb: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h6">{r.title ?? "Untitled"}</Typography>
                  <Typography variant="body2">Category: {r.category} | Priority: {r.priority}</Typography>
                  <Typography variant="body2">{r.body?.slice(0, 100)}...</Typography>
                </Box>
                <IconButton
                  onClick={async () => {
                    if (expandedId === r.id) {
                      setExpandedId(null);
                    } else {
                      if (!r.full) {
                        const res = await fetch(`http://localhost:5000/symbols/${r.id}`);
                        const data = await res.json();
                        setResults(prev => prev.map(entry => entry.id === r.id ? { ...entry, full: data } : entry));
                      }
                      setExpandedId(r.id);
                    }
                  }}
                >
                  {expandedId === r.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>
              <Collapse in={expandedId === r.id}>
                {r.full && (
                  <Box mt={2} sx={{ bgcolor: "#f0f0f0", p: 2 }}>
                    <Typography><strong>Title:</strong> {r.full.title}</Typography>
                    <Typography><strong>Category:</strong> {r.full.category}</Typography>
                    <Typography><strong>Body:</strong> {r.full.body}</Typography>
                    <Typography><strong>Comment:</strong> {r.full.comment}</Typography>
                    <Typography><strong>Event Time:</strong> {new Date(r.full.due_date).toLocaleString()}</Typography>
                    <Typography><strong>Priority:</strong> {r.full.priority}</Typography>
                  </Box>
                )}
              </Collapse>
              <Box mt={2}>
                <Button component={Link} to={`/edit/${r.id}`} variant="outlined" size="small">Edit</Button>
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
