# Piggy Chef Development Documentation

## Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (Native), Bootstrap 5, Vis-Network.
- **Backend**: Python 3, Django 4.2.
- **Database**: MongoDB (via MongoEngine), SQLite (Auth).
- **AI**: Mock Integration (Ready for requests/openai).

## Architecture
- **Hybrid Database**: Django Auth uses SQLite for session management. Business data (Courses, Graphs, Tasks) is stored in MongoDB.
- **Offline First**: Service Worker caches static assets. LocalStorage holds offline samples.

## Key Modules
- **api**: Handles all AJAX requests (Auth, Upload, Task Generation).
- **piggy_chef**: Main project settings and URL routing.
- **templates**: 10 Screen definitions.
- **static**: CSS/JS assets.
