# Learning Content API Contract

**Project:** EduForge  
**Version:** v2  
**Base URL:** `http://localhost:8000/api/`

---

# Scope

This contract covers instructor-side curriculum management: creating, reading,
updating, deleting, and reordering **Sections** and **Lessons** within a course.

The nested curriculum returned by the Course Details endpoint belongs to the
Course API contract (`courses_api_contract.md`).

## Supported Endpoints

- `POST   /api/courses/{course_id}/sections/`
- `GET    /api/courses/{course_id}/sections/{section_id}/`
- `PATCH  /api/courses/{course_id}/sections/{section_id}/`
- `PUT    /api/courses/{course_id}/sections/{section_id}/`
- `DELETE /api/courses/{course_id}/sections/{section_id}/`
- `PATCH  /api/courses/{course_id}/sections/reorder/`
- `POST   /api/sections/{section_id}/lessons/`
- `GET    /api/sections/{section_id}/lessons/{lesson_id}/`
- `PATCH  /api/sections/{section_id}/lessons/{lesson_id}/`
- `PUT    /api/sections/{section_id}/lessons/{lesson_id}/`
- `DELETE /api/sections/{section_id}/lessons/{lesson_id}/`
- `PATCH  /api/sections/{section_id}/lessons/reorder/`

Note the asymmetry: section routes are nested under their course, while lesson
routes are nested under their section only.

---

# Design Decisions

- Lessons store their video location in a field named **`video`**, holding an
  external URL (YouTube, Vimeo, Cloudflare R2, S3 CDN, etc.).
- Video uploads are intentionally out of scope and will be implemented in a
  future Media Storage milestone.
- Section and Lesson ordering is managed exclusively through dedicated reorder
  endpoints. `order` is read-only on create and update.
- Newly created Sections and Lessons are always appended to the end.

---

# Permission Strategy

All endpoints require authentication and the `instructor` role.

## Not an Instructor

A student (or any non-instructor) receives:

```http
403 Forbidden
```

```json
{
  "detail": "Only instructors can perform this action."
}
```

## Not the Owner

To avoid leaking IDs, every queryset is scoped to the owning instructor and to
the parent resource:

```
Course
 └── Section
      └── Lesson
```

An instructor acting on **another instructor's** curriculum therefore receives
`404 Not Found`, not `403 Forbidden`:

```http
404 Not Found
```

```json
{
  "detail": "No Course matches the given query."
}
```

or, for section-scoped and lesson-scoped routes:

```json
{
  "detail": "No Section matches the given query."
}
```

The same `404` is returned when a lesson does not belong to the supplied
section, or a section does not belong to the supplied course.

> Exception: `PATCH /api/courses/{course_id}/sections/reorder/` returns `400`
> rather than `404` for a course the caller does not own — see section 7.

## Anonymous

```http
401 Unauthorized
```

```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

# Error Response Format

Validation errors:

```json
{
  "field_name": ["Error message."]
}
```

General errors:

```json
{
  "detail": "Error message."
}
```

---

# Validation Rules

Unless otherwise specified:

- Leading/trailing whitespace is trimmed.
- Whitespace-only strings are rejected with `"This field may not be blank."`
- **No minimum length is enforced** on titles. A 2-character title is accepted.
- Title uniqueness is **not** enforced.
- Validation errors follow DRF's standard format.

---

# 1. Create Section

## Endpoint

```http
POST /api/courses/{course_id}/sections/
```

## Request

```json
{
  "title": "Getting Started"
}
```

`order` is assigned automatically as `max(order) + 1` within the course.

## Validation

| Field | Rules                             |
| ----- | --------------------------------- |
| title | Required, non-blank, max 150 chars |

## Success

```http
201 Created
```

```json
{
  "id": 1,
  "title": "Getting Started",
  "order": 1
}
```

The section payload does **not** include a `lessons` key. Lessons are only
returned nested inside the Course Details response.

---

# 2. Read Section

## Endpoint

```http
GET /api/courses/{course_id}/sections/{section_id}/
```

## Success

```http
200 OK
```

```json
{
  "id": 1,
  "title": "Getting Started",
  "order": 1
}
```

---

# 3. Update Section

## Endpoints

```http
PATCH /api/courses/{course_id}/sections/{section_id}/
PUT   /api/courses/{course_id}/sections/{section_id}/
```

## Request

```json
{
  "title": "Getting Started with React"
}
```

`title` is the only writable field. `PUT` requires it to be present.

## Success

```http
200 OK
```

```json
{
  "id": 1,
  "title": "Getting Started with React",
  "order": 1
}
```

---

# 4. Delete Section

## Endpoint

```http
DELETE /api/courses/{course_id}/sections/{section_id}/
```

## Success

```http
204 No Content
```

Deleting a section also deletes all of its lessons.

Remaining section orders are **not** automatically renumbered.

Use the reorder endpoint if contiguous ordering is required.

---

# 5. Create Lesson

## Endpoint

```http
POST /api/sections/{section_id}/lessons/
```

The course ID does not appear in this path. Ownership is resolved through the
section.

## Request

```json
{
  "title": "Welcome & Course Overview",
  "video": "https://cdn.example.com/lesson1.mp4",
  "duration_seconds": 332,
  "free": true
}
```

`order` is assigned automatically as `max(order) + 1` within the section.

`free` defaults to `false`.

## Validation

| Field            | Rules                              |
| ---------------- | ---------------------------------- |
| title            | Required, non-blank, max 150 chars |
| video            | Required, valid URL                |
| duration_seconds | Required, integer >= 0             |
| free             | Optional boolean                   |

A negative `duration_seconds` is rejected with:

```json
{
  "duration_seconds": ["Ensure this value is greater than or equal to 0."]
}
```

An invalid URL is rejected with:

```json
{
  "video": ["Enter a valid URL."]
}
```

## Success

```http
201 Created
```

```json
{
  "id": 5,
  "title": "Welcome & Course Overview",
  "video": "https://cdn.example.com/lesson1.mp4",
  "duration_seconds": 332,
  "order": 1,
  "free": true
}
```

---

# 6. Read, Update, and Delete Lesson

## Endpoints

```http
GET    /api/sections/{section_id}/lessons/{lesson_id}/
PATCH  /api/sections/{section_id}/lessons/{lesson_id}/
PUT    /api/sections/{section_id}/lessons/{lesson_id}/
DELETE /api/sections/{section_id}/lessons/{lesson_id}/
```

## Request

`PATCH` accepts any subset of the writable fields (`title`, `video`,
`duration_seconds`, `free`).

```json
{
  "free": false
}
```

`PUT` requires `title`, `video`, and `duration_seconds`.

## Success

```http
200 OK
```

```json
{
  "id": 5,
  "title": "Welcome & Course Overview",
  "video": "https://cdn.example.com/lesson1.mp4",
  "duration_seconds": 332,
  "order": 1,
  "free": false
}
```

`DELETE` returns:

```http
204 No Content
```

Remaining lesson orders are **not** renumbered.

---

# 7. Reorder Sections

## Endpoint

```http
PATCH /api/courses/{course_id}/sections/reorder/
```

## Request

```json
{
  "order": [3, 1, 2]
}
```

The payload must contain **every section ID belonging to the course exactly
once**, in the desired order. IDs must be integers `>= 1` and the list must be
non-empty.

Sections are renumbered contiguously from `1` in the given order.

## Success

```http
200 OK
```

```json
{
  "message": "Sections reordered successfully."
}
```

## Validation Errors

Wrong, missing, or duplicated IDs:

```json
{
  "order": ["Must include every section ID for this course exactly once."]
}
```

Missing key:

```json
{
  "order": ["This field is required."]
}
```

Empty list:

```json
{
  "order": ["This list may not be empty."]
}
```

> A course the caller does not own — or one with no sections — resolves to an
> empty expected set, so it also returns the
> `"Must include every section ID..."` error with `400`, not a `404`.

---

# 8. Reorder Lessons

## Endpoint

```http
PATCH /api/sections/{section_id}/lessons/reorder/
```

## Request

```json
{
  "order": [7, 5, 6]
}
```

The payload must contain **every lesson ID belonging to the section exactly
once**, in the desired order.

Lessons are renumbered contiguously from `1` in the given order.

## Success

```http
200 OK
```

```json
{
  "message": "Lessons reordered successfully."
}
```

## Validation Error

```json
{
  "order": ["Must include every lesson ID for this section exactly once."]
}
```

Unlike section reordering, a section the caller does not own returns `404` with
`{"detail": "No Section matches the given query."}` because the section is
resolved before validation.

---

# Known Issues

- **`duration_seconds: 0` returns `500`.** The serializer's lower bound is `0`,
  but the database check constraint requires `> 0`, so a zero duration raises an
  `IntegrityError` instead of a `400`. The serializer needs `min_value=1`.
- **Section reorder does not distinguish "not found" from "invalid payload".**
  Both produce the same `400`.

---

# Future Milestones

The following are intentionally **out of scope** for this contract:

- Video upload API
- S3 / Cloudflare R2 integration
- Presigned upload URLs
- Moving a lesson between sections
- Automatic renumbering after a delete
- Lesson progress
- Watch history
- Course completion
- Streaming authorization
