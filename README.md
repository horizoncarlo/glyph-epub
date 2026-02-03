## Glyph epub hub

#### Python (mvp)
- Server that reads a directory of epub files and displays a basic HTML page of them for download
- SQLite for metadata, mainly tags (such as "Sci-fi" as a tag)
- Can drop files into dir locally to automatically update the list. So **file watch** as well
- Need to generate a nice rich HTML page AND a basic HTML that Kobo readers can reach
  - ** Use HTMX for nice page, do first. And see if it can just be used for simple HTML page too
  - Sortable table by column, sort by tags, search, genre?
- Also generate an EVEN simpler page of a pure directory style list? If possible. For ease of 3rd party apps (like if we do a Terminal epub reader that hooks in).
- Have an upload option (mainly for cell phone) to put a new book in. Rename (moves file), add tags, etc.
- Anyone can CRUD any book

#### Eventual
- Can read books directly in the browser
  - So Python epub reader that renders to returned HTML
  - Metadata for books? See if it can be pulled from .epub itself or from a remote service?
- Main benefit is we can remember read position AND allow bookmarks / quote saving across devices...so I can read on my phone then via `links` in a terminal at home (another benefit of plain HTML page), etc.
  - Saving quotes would put in a file that could be exported with book title, author, page num, date of bookmark
- No accounts, just enter your "private key" or something, basically like a password, and your data is associated with that
- Could also hook into the Terminal epub reader for fun. Sort of double-duty of `links` usage, but still an interesting learning process
