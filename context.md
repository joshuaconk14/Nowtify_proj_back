this is an app that lets users create accounts and connect to their spotify in order to create playlists based on their mood. consider that this is a smaller application that wont reach millions of users

Frontend: react

Backend: python

temporary session storage:
    - filesystem: for local dev - stores session id + spotify tokens as files
    - Redis: for production - stores session id + spotify tokens in central db

permanent db storage
    - SQLite: for local dev - stores user accounts
    - PostgreSQL: for production - stores user accounts


TIPS:
lets also create this app using best software engineering practices and principles for secure application