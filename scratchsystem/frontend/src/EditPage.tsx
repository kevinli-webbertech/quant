// EditPage.tsx
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  TextField, Box, Button, Select, MenuItem, Typography, InputLabel, FormHelperText
} from "@mui/material";
import { SymbolEntry } from "./types";
import { updateSymbol } from "./api";

const EditPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [form, setForm] = useState<SymbolEntry>({
    title: "",
    body: "",
    category: "code",
    comment: "",
    due_date: new Date().toISOString().slice(0, 16),
    priority: "medium",
    tags: [],
  });

  const [errors, setErrors] = useState({ title: false, tags: false });

  useEffect(() => {
    fetch(`http://localhost:5000/symbols/${id}`)
      .then((res) => res.json())
      .then((data) => {
        setForm({
          title: data.title ?? "",
          category: data.category ?? "code",
          body: data.body ?? "",
          comment: data.comment ?? "",
          due_date: data.due_date?.slice(0, 16) ?? new Date().toISOString().slice(0, 16),
          priority: data.priority ?? "medium",
          tags: data.tags ?? [],
        });
      });
  }, [id]);

  const validateField = (name: string, value: string) => {
    if (name === "title") {
      setErrors((prev) => ({ ...prev, title: value.trim() === "" }));
    } else if (name === "tags") {
      setErrors((prev) => ({ ...prev, tags: value.trim() === "" }));
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    validateField(name, value);

    if (name === "tags") {
      setForm({ ...form, tags: value.split(",").map(tag => tag.trim()) });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const handleUpdate = async () => {
    if (form.title.trim() === "" || form.tags.length === 0) return;
    await updateSymbol(Number(id), form);
    navigate("/");
  };

  return (
    <Box maxWidth={600} mx="auto" mt={5}>
      <Typography variant="h5" gutterBottom>Edit Symbol #{id}</Typography>

      <TextField
        label="Title"
        name="title"
        value={form.title}
        onChange={handleChange}
        error={errors.title}
        helperText={errors.title ? "Title is required." : ""}
        fullWidth
        sx={{ mb: 2 }}
      />

      <TextField
        label="Body"
        name="body"
        value={form.body}
        onChange={handleChange}
        fullWidth
        multiline
        rows={4}
        sx={{ mb: 2 }}
      />

      <TextField
        label="Comment"
        name="comment"
        value={form.comment}
        onChange={handleChange}
        fullWidth
        sx={{ mb: 2 }}
      />

      <TextField
        type="datetime-local"
        label="Event Time"
        name="due_date"
        value={form.due_date}
        onChange={handleChange}
        fullWidth
        InputLabelProps={{ shrink: true }}
        sx={{ mb: 2 }}
      />

      <InputLabel sx={{ mt: 1 }}>Category</InputLabel>
      <Select
        name="category"
        value={form.category}
        onChange={(e) => setForm({ ...form, category: e.target.value })}
        fullWidth
        sx={{ mb: 2 }}
      >
        <MenuItem value="code">Code</MenuItem>
        <MenuItem value="news">News</MenuItem>
        <MenuItem value="indicator">Indicator</MenuItem>
      </Select>

      <InputLabel>Priority</InputLabel>
      <Select
        name="priority"
        value={form.priority}
        onChange={(e) => setForm({ ...form, priority: e.target.value })}
        fullWidth
        sx={{ mb: 2 }}
      >
        <MenuItem value="low">Low</MenuItem>
        <MenuItem value="medium">Medium</MenuItem>
        <MenuItem value="high">High</MenuItem>
      </Select>

      <TextField
        label="Tags"
        name="tags"
        value={form.tags.join(", ")}
        onChange={handleChange}
        error={errors.tags}
        helperText={errors.tags ? "At least one tag is required." : ""}
        fullWidth
        sx={{ mb: 2 }}
      />

      <Button variant="contained" onClick={handleUpdate}>Update Symbol</Button>
    </Box>
  );
};

export default EditPage;
