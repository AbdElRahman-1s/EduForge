# Instructor Analytics API Contract

**Base URL:** `http://localhost:8000/api/instructor/`

All endpoints require JWT authentication and the `instructor` role. Anonymous
requests return `401`; authenticated non-instructors return `403`. Queries are
scoped to courses owned by the requester.

## Dashboard overview

`GET /api/instructor/dashboard/` returns published-course and distinct
active-student totals, all owned courses created or updated in the last 30 days,
and all owned-course enrollments from the last 30 days. Neither collection has
a count limit. Signups are newest-first and include `id`, username, email, and
status.

## Course analytics

`GET /api/instructor/courses/` returns only owned courses with `id`, `title`,
`thumbnail`, `category` (the category **name**, not its id), active
`enrollment_count`, `review_count`, `avg_rating`, `lesson_count`,
`total_duration` (seconds), and `price`. Review fields currently default to
`0`/`0.0` because no review model exists.

```json
[{"id": 1, "title": "Intro to Django", "thumbnail": "/media/courses/intro.jpg",
  "category": "Web Development", "enrollment_count": 12, "review_count": 0,
  "avg_rating": 0.0, "lesson_count": 8, "total_duration": 3600,
  "price": "0.00"}]
```

## Student summary

`GET /api/instructor/students/` returns each student once across owned courses.
Active and suspended enrollments are included; no status or mutation action is
exposed.

```json
[{"username":"abdo_adel","email":"abdo@example.com","course_count":3,"joined_at":"2026:08:25"}]
```

`course_count` is scoped to owned courses and `joined_at` is the earliest
matching enrollment date formatted as `YYYY:MM:DD`.
