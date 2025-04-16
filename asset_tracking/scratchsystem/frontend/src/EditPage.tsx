import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { TextField, Box, Button, Select, MenuItem, Typography } from "@mui/material";
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
    due_date: "",
    priority: "medium",
    tags: [],
  });

  useEffect(() => {
    fetch(`http://localhost:5000/symbols/${id}`)
      .then((res) => res.json())
      .then((data) => {
        setForm({
          title: data[2],
          category: data[1],
          body: data[3],
          comment: data[4],
          due_date: data[7]?.slice(0, 16) || "",
          priority: data[8],
          tags: [], // You can add tag fetching if needed
        });
      });
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    if (name === "tags") {
      setForm({ ...form, tags: value.split(",").map(tag => tag.trim()) });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const handleUpdate = async () => {
    await updateSymbol(Number(id), form);
    alert("Updated!");
    navigate("/");
  };

  return (
    <Box maxWidth={600} mx="auto" mt={5}>
      <Typography variant="h5" gutterBottom>Edit Symbol #{id}</Typography>
      <TextField label="Title" name="title" value={form.title} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
      <TextField label="Body" name="body" value={form.body} onChange={handleChange} fullWidth multiline rows={4} sx={{ mb: 2 }} />
      <TextField label="Comment" name="comment" value={form.comment} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
      <TextField type="datetime-local" name="due_date" value={form.due_date} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
      <TextField label="Category" name="category" value={form.category} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
      <Select value={form.priority} name="priority" onChange={(e) => setForm({ ...form, priority: e.target.value })} fullWidth sx={{ mb: 2 }}>
        <MenuItem value="low">Low</MenuItem>
        <MenuItem value="medium">Medium</MenuItem>
        <MenuItem value="high">High</MenuItem>
      </Select>
      <TextField label="Tags" name="tags" value={form.tags.join(", ")} onChange={handleChange} fullWidth sx={{ mb: 2 }} />
      <Button variant="contained" onClick={handleUpdate}>Update Symbol</Button>
    </Box>
  );
};

export default EditPage;
