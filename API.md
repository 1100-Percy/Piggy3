# API Documentation

## Auth
- `POST /api/register/`: {username, password, major}
- `POST /api/login/`: {username, password}
- `GET /api/check_auth/`
- `GET /api/logout/`

## Core
- `POST /api/upload_course/`: FormData(file)
- `POST /api/set_thinking_type/`: {thinking_type}
- `POST /api/generate_tasks/`: {count}
- `GET /api/get_dashboard_data/`
- `GET /api/get_task_details/?id=<id>`
- `POST /api/complete_task/`: {task_id, status}
- `GET /api/get_results/`
