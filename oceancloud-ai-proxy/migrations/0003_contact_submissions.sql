CREATE TABLE IF NOT EXISTS contact_submissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  company TEXT NOT NULL,
  service TEXT NOT NULL,
  org_size TEXT,
  message TEXT NOT NULL,
  source_url TEXT,
  status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new', 'read', 'archived')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_contact_submissions_status_created
ON contact_submissions(status, created_at DESC);
