# Authentication Fix TODO

## Problem
Flutter frontend sends "Bearer null" when UserSession.token is null, causing 401 errors on admin endpoints.

## Backend Fixes
- [x] app/routers/auth.py - Add null check in get_current_user() for consistency

## Frontend Fixes  
- [x] ../jobsify/lib/services/admin_service.dart - Add safe token helper method
- [x] ../jobsify/lib/screens/admin/admin_dashboard.dart - Use safe token retrieval
- [x] ../jobsify/lib/screens/admin/screens/job_verification_screen.dart - Use safe token retrieval
- [x] ../jobsify/lib/screens/admin/screens/users_screen.dart - Use safe token retrieval
- [x] ../jobsify/lib/screens/admin/screens/provider_verification_screen.dart - Use safe token retrieval
- [x] ../jobsify/lib/screens/admin/screens/reports_screen.dart - Use safe token retrieval

## Testing
- [ ] Verify admin endpoints work correctly
- [ ] Check job verification functionality
