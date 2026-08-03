# Learning Content API Contract

**Project:** EduForge  
**Version:** v1  
**Base URL:** `http://localhost:8000/api/courses/`

---

# Scope

This contract covers instructor-side curriculum management: creating, updating,
deleting, and reordering **Sections** and **Lessons** within a course.

Reading the curriculum is **not** covered here. The nested curriculum returned
by the Course Details endpoint belongs to the Course API contract.

---

# Design Decisions

- Lessons store a `video_url` (external URL such as YouTube, Vimeo, Cloudflare R2, S3 CDN, etc.).
- Video uploads are intentionally out of scope and will be implemented in a future Media Storage milestone.
- Section and Lesson ordering is managed exclusively through dedicated reorder endpoints.
- Newly created Sections and Lessons are always appended to the end.

---

# Permission Strategy

All endpoints require authentication.

Only the instructor who owns the course may modify its curriculum.

Any instructor attempting to modify another instructor's course receives:

```http
403 Forbidden
```

```json
{
  "detail": "You do not have permission to modify this course."
}
```

To avoid leaking IDs, every queryset is scoped to the parent resource.

For example:

```
Course
 └── Section
      └── Lesson
```

If a lesson does not belong to the supplied section (or a section does not
belong to the supplied course), the API returns:

```http
404 Not Found
```

instead of `403 Forbidden`.

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
- Empty strings after trimming are rejected.
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

`order` is automatically assigned.

## Validation

| Field | Rules                      |
| ----- | -------------------------- |
| title | Required, 3–100 characters |

## Success

```http
201 Created
```

```json
{
  "id": 1,
  "title": "Getting Started",
  "order": 1,
  "lessons": []
}
```

---

# 2. Update Section

## Endpoint

```http
PATCH /api/sections/{section_id}/
```

## Request

```json
{
  "title": "Getting Started with React"
}
```

## Success

```json
{
  "id": 1,
  "title": "Getting Started with React",
  "order": 1,
  "lessons": []
}
```

---

# 3. Delete Section

## Endpoint

```http
DELETE /api/sections/{section_id}/
```

## Success

```http
204 No Content
```

Deleting a section also deletes all of its lessons.

Remaining section orders are **not** automatically renumbered.

Use the reorder endpoint if contiguous ordering is required.

---

# 4. Create Lesson

## Endpoint

```http
POST /api/sections/{section_id}/lessons/
```

## Request

```json
{
  "title": "Welcome & Course Overview",
  "video_url": "https://cdn.example.com/lesson1.mp4",
  "duration_seconds": 332,
  "free": true
}
```

`order` is assigned automatically.

`free` defaults to `false`.

## Validation

| Field            | Rules                      |
| ---------------- | -------------------------- |
| title            | Required, 3–150 characters |
| video_url        | Required, valid URL        |
| duration_seconds | Required, integer > 0      |
| free             | Optional                   |

## Success

```http
201 Created
```

```json
{
  "id": 5,
  "title": "Welcome & Course Overview",
  "video_url": "https://cdn.example.com/lesson1.mp4",
  "duration_seconds": 332,
  "order": 1,
  "free": true
}
```

---

# 5. Update Lesson

## Endpoint

```http
PATCH /api/lessons/{lesson_id}/
```

## Request

```json
{
  "free": false
}
```

Any subset of fields may be updated.

## Success

```json
{
  "id": 5,
  "title": "Welcome & Course Overview",
  "video_url": "https://cdn.example.com/lesson1.mp4",
  "duration_seconds": 332,
  "order": 1,
  "free": false
}
```

---

# 6. Delete Lesson

## Endpoint

```http
DELETE /api/lessons/{lesson_id}/
```

## Success

```http
204 No Content
```

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

The payload must contain **every section ID belonging to the course exactly once.**

## Success

```json
{
  "message": "Sections reordered successfully."
}
```

## Validation Error

```json
{
  "order": ["Must include every section ID for this course exactly once."]
}
```

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

The payload must contain **every lesson ID belonging to the section exactly once.**

## Success

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

---

# Future Milestones

The following are intentionally **out of scope** for this contract:

- Video upload API
- S3 / Cloudflare R2 integration
- Presigned upload URLs
- Curriculum retrieval (Course Details endpoint)
- Lesson progress
- Watch history
- Course completion
- Streaming authorization
