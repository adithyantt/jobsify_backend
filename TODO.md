# Backend Fixes TODO

## Tasks:
- [x] Fix `app/schemas/report.py` - Add missing fields (status, created_at, user_id)
- [x] Fix `app/routers/admin_reports.py` - Create request body model and update endpoint
- [x] Fix `app/routers/auth.py` - Improve get_current_admin security with JWT tokens
- [x] Update `app/routers/reports.py` - Ensure consistency with schema changes
- [x] Add PyJWT to requirements.txt
- [x] Test the API endpoints



## Progress:
- Started: [Current Date]
- Last Updated: [Current Date]

## Notes:
- JWT authentication now returns access_token on login
- Admin endpoints now require proper JWT Bearer tokens
- Report action endpoint now uses JSON request body instead of query params
