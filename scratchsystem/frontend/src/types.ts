export interface SymbolEntry {
  id?: number;
  category: string;
  title: string;
  body: string;
  comment: string;
  due_date: string;
  priority: string;
  tags: string[];
}

export interface SearchResult {
  id: number;
  title: string;
  category: string;
  priority: string;
  body: string;
}
