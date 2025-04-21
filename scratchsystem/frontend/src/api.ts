import { SymbolEntry, SearchResult } from "./types";

const BASE_URL = "http://localhost:5000";

export async function createSymbol(data: SymbolEntry): Promise<any> {
  const res = await fetch(`${BASE_URL}/symbols`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function searchSymbols(tag: string): Promise<SearchResult[]> {
  const res = await fetch(`${BASE_URL}/symbols/search?tag=${tag}`);
  return res.json(); // no .map needed because backend returns JSON-friendly dicts
}

export async function deleteSymbol(id: number) {
  return await fetch(`${BASE_URL}/symbols/${id}`, {
    method: "DELETE",
  });
}

export async function updateSymbol(id: number, data: SymbolEntry) {
  return await fetch(`${BASE_URL}/symbols/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}
