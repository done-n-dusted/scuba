"use client";

import { useState } from "react";
import styles from "./page.module.css";
import { GlassCard } from "./components/GlassCard";
import { GlassInput } from "./components/GlassInput";
import { GlassButton } from "./components/GlassButton";

// Define Types for API Responses
interface IndexResponse {
  message: string;
  indexed_files_count: number;
}

interface SearchResult {
  [path: string]: {
    size: number;
    last_modified: number;
  };
}

interface SearchResponse {
  query: string;
  results: SearchResult;
}

export default function Home() {
  // State for Indexing
  const [rootPath, setRootPath] = useState("");
  const [isIndexing, setIsIndexing] = useState(false);
  const [indexMessage, setIndexMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  // State for Searching
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Constants
  const API_BASE_URL = "http://localhost:8000";

  const handleIndexDirectory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rootPath.trim()) return;

    setIsIndexing(true);
    setIndexMessage(null);

    try {
      const response = await fetch(`${API_BASE_URL}/index`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ directory: rootPath }),
      });

      if (!response.ok) {
        throw new Error("Failed to index directory");
      }

      const data: IndexResponse = await response.json();
      setIndexMessage({
        type: 'success',
        text: `Indexed ${data.indexed_files_count} files successfully!`
      });
    } catch (err) {
      setIndexMessage({
        type: 'error',
        text: err instanceof Error ? err.message : "An unknown error occurred"
      });
    } finally {
      setIsIndexing(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setSearchError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery)}`);
      
      if (!response.ok) {
        throw new Error("Search request failed");
      }

      const data: SearchResponse = await response.json();
      setSearchResults(data.results);
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : "Failed to search");
      setSearchResults(null);
    } finally {
      setIsSearching(false);
    }
  };

  // Helper function to format timestamp
  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  // Helper function to format bytes
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <main className={styles.main}>
      <header className={styles.header}>
        <h1 className={styles.title}>Scuba Explorer</h1>
        <p className={styles.subtitle}>Index and search your file system with blazing speed</p>
      </header>

      <div className={styles.grid}>
        {/* Explorer Section */}
        <section className={styles.section}>
          <GlassCard>
            <h2 className={styles.sectionTitle}>1. Index Repository</h2>
            <p className={styles.sectionDesc}>Enter the absolute path of the root directory you want to index.</p>
            
            <form onSubmit={handleIndexDirectory} className={styles.form}>
              <GlassInput
                label="Root Folder Path"
                placeholder="e.g., /home/user/projects/scuba"
                value={rootPath}
                onChange={(e) => setRootPath(e.target.value)}
                disabled={isIndexing}
                required
              />
              <GlassButton type="submit" isLoading={isIndexing} disabled={!rootPath.trim()}>
                Index Directory
              </GlassButton>
            </form>

            {indexMessage && (
              <div className={`${styles.message} ${styles[indexMessage.type]} animate-fade-in`}>
                {indexMessage.text}
              </div>
            )}
          </GlassCard>
        </section>

        {/* Search Section */}
        <section className={styles.section}>
          <GlassCard>
            <h2 className={styles.sectionTitle}>2. Search</h2>
            <p className={styles.sectionDesc}>Find files instantly across your indexed repository.</p>
            
            <form onSubmit={handleSearch} className={styles.form}>
              <GlassInput
                label="Search Query"
                placeholder="Search for a filename..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                disabled={isSearching}
                required
              />
              <GlassButton type="submit" variant="secondary" isLoading={isSearching} disabled={!searchQuery.trim()}>
                Search Files
              </GlassButton>
            </form>

            {searchError && (
              <div className={`${styles.message} ${styles.error} animate-fade-in`}>
                {searchError}
              </div>
            )}

            {/* Search Results Display */}
            {searchResults && (
              <div className={`${styles.resultsContainer} animate-fade-in`}>
                <h3 className={styles.resultsHeader}>
                  Found {Object.keys(searchResults).length} matching files
                </h3>
                
                {Object.keys(searchResults).length > 0 ? (
                  <ul className={styles.resultsList}>
                    {Object.entries(searchResults).map(([path, meta]) => (
                      <li key={path} className={styles.resultItem}>
                        <div className={styles.resultPath}>{path}</div>
                        <div className={styles.resultMeta}>
                          <span>Size: {formatBytes(meta.size)}</span>
                          <span className={styles.dot}>•</span>
                          <span>Modified: {formatDate(meta.last_modified)}</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className={styles.emptyState}>
                    No files found matching "{searchQuery}"
                  </div>
                )}
              </div>
            )}
          </GlassCard>
        </section>
      </div>
    </main>
  );
}
