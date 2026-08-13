# Courses API Contract

**Project:** EduForge  
**Version:** v3  
**Base URL:** `http://localhost:8000/api/`

---

# Overview

This contract documents the current courses app API for public course browsing
and instructor-managed course operations.

## Supported Endpoints

- `GET /api/courses/`
- `POST /api/courses/`
- `GET /api/courses/{id}/`
- `PATCH /api/courses/{id}/`
- `PUT /api/courses/{id}/`
- `DELETE /api/courses/{id}/`
- `GET /api/courses/mine/`
- `GET /api/categories/`
- `GET /api/topics/`

Curriculum management (sections and lessons) is documented in
`curriculum_api_contract.md`. Enrollment is documented in
`enrollments_api_contract.md`.

---

# Access and Permissions

## Public Access

- Anyone can list published courses.
- Anyone can view a published course detail.

## Instructor Access

- Authenticated instructors can create courses.
- Authenticated instructors can view their own courses via `/api/courses/mine/`.
- Only the owning instructor can update or delete a course.
- Only authenticated instructors can list categories and topics.

## Student Access

- Students cannot create, update, or delete courses.
- Students cannot access `/api/courses/mine/`, `/api/categories/`, or
  `/api/topics/`.

## Permission Errors

Non-instructor callers (students) receive:

```http
403 Forbidden
```

```json
{
  "detail": "Only instructors can perform this action."
}
```

An instructor acting on a course they do not own receives:

```http
403 Forbidden
```

```json
{
  "detail": "You can only modify your own courses."
}
```

Anonymous callers on a protected endpoint receive:

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

# Serializer Shapes

Two different course shapes are returned depending on the operation.

| Operation                | `category`      | `topics`          |
| ------------------------ | --------------- | ----------------- |
| List / detail / mine     | category `name` | list of topic names |
| Create / update response | category `id`   | list of topic ids |

Write operations echo back IDs because they return the write serializer. Read
operations return human-readable names. Clients must not assume one shape for
both.

---

# Pagination

`GET /api/courses/`, `GET /api/categories/`, and `GET /api/topics/` use
page-based pagination.

Default page size: `10`

Example response:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/courses/?page=2",
  "previous": null,
  "results": []
}
```

Requesting a page beyond the last one returns:

```http
404 Not Found
```

```json
{
  "detail": "Invalid page."
}
```

`GET /api/courses/mine/` is **not** paginated — see section 6.

> The published-courses queryset has no explicit ordering, so page boundaries
> are not guaranteed stable across requests. Ordering is a future improvement.

---

# 1. List Published Courses

## Endpoint

```http
GET /api/courses/
```

## Authentication

None required.

## Behavior

- Returns only courses where `published: true`.
- Unpublished courses do not appear in this endpoint, not even for their owner.
- No filtering, search, or ordering query parameters are supported yet. Only
  `page` is honoured.
- Includes `is_enrolled` field: A boolean indicating if the requesting authenticated user is enrolled in the course. Returns `false` for anonymous users.

## Success

```http
200 OK
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Backend Development with Django",
      "category": "Programming",
      "level": "beginner",
      "price": "0.00",
      "thumbnail": "http://localhost:8000/media/courses/django.png",
      "topics": ["Python", "Django"],
      "badge": "new",
      "instructor": {
        "id": 4,
        "username": "abdallah",
        "email": "abdallah@example.com"
      },
      "published": true,
      "is_enrolled": false,
      "created_at": "2026-07-01T10:00:00Z"
    }
  ]
}
```

`thumbnail` is an absolute URL, or `null` when no image has been uploaded.

---

# 2. Get Course Detail

## Endpoint

```http
GET /api/courses/{id}/
```

## Authentication

Optional. Authenticated instructors can access their own unpublished courses.

## Behavior

- Published courses are publicly accessible.
- An authenticated **instructor** can retrieve their own courses regardless of
  publication status.
- Everyone else — anonymous users, students, and other instructors — receives
  `404 Not Found` for an unpublished course.
- Sections are returned ordered by their `order` field.
- Lessons are returned ordered by their `order` field.
- Includes `is_enrolled` field: A boolean indicating if the requesting authenticated user is enrolled in this course. Returns `false` for anonymous users.
- The `video` field is returned when the lesson is a free preview, when the requester is the course owner, **or** when the requester is an enrolled student. Otherwise it is `null`.

## Success

```http
200 OK
```

```json
{
  "id": 1,
  "title": "Backend Development with Django",
  "category": "Programming",
  "level": "beginner",
  "price": "0.00",
  "thumbnail": "http://localhost:8000/media/courses/django.png",
  "topics": ["Python", "Django"],
  "badge": "new",
  "instructor": {
    "id": 4,
    "username": "abdallah",
    "email": "abdallah@example.com"
  },
  "published": true,
  "is_enrolled": false,
  "created_at": "2026-07-01T10:00:00Z",
  "description": "Learn to build production APIs with Django REST Framework.",
  "total_lessons": 2,
  "total_duration_seconds": 600,
  "sections": [
    {
      "id": 1,
      "title": "Getting Started",
      "order": 1,
      "lessons": [
        {
          "id": 1,
          "title": "Introduction",
          "duration_seconds": 180,
          "order": 1,
          "free": true,
          "video": "https://cdn.example.com/videos/intro.mp4"
        },
        {
          "id": 2,
          "title": "Environment Setup",
          "duration_seconds": 420,
          "order": 2,
          "free": false,
          "video": null
        }
      ]
    }
  ]
}
```

`total_lessons` and `total_duration_seconds` are aggregated across all sections
and default to `0` for an empty curriculum.

## Error Cases

### Unpublished or Missing Course

```http
404 Not Found
```

```json
{
  "detail": "No Course matches the given query."
}
```

---

# 3. Create Course

## Endpoint

```http
POST /api/courses/
```

## Authentication

Required. Must be authenticated as an instructor.

## Request

```json
{
  "title": "Backend Development with Django",
  "description": "Learn to build production APIs with Django REST Framework.",
  "category": 1,
  "level": "beginner",
  "price": 49.99,
  "topics": [1, 2],
  "badge": "new",
  "published": false
}
```

## Notes

- The authenticated user is assigned as the course instructor automatically.
- `thumbnail` can be sent as a file when using `multipart/form-data`.

## Validation Rules

| Field         | Rules                                                          |
| ------------- | -------------------------------------------------------------- |
| `title`       | Required, non-blank, max 150 characters                        |
| `description` | Required, non-blank                                            |
| `category`    | Required, must reference an existing category ID               |
| `level`       | Required, one of `beginner`, `intermediate`, `advanced`, `all` |
| `price`       | Optional, max 7 digits with 2 decimal places                   |
| `topics`      | Optional, list of topic IDs                                    |
| `badge`       | Optional, one of `bestseller`, `hot`, `new`, `none`            |
| `published`   | Optional boolean, defaults to `false`                          |

- No minimum length is enforced on `title` — a 2-character title is accepted.
- Leading/trailing whitespace is trimmed; a whitespace-only value is rejected
  with `"This field may not be blank."`
- `badge` defaults to `none` and `price` defaults to `null` when omitted.

## Success

```http
201 Created
```

```json
{
  "id": 12,
  "title": "Backend Development with Django",
  "description": "Learn to build production APIs with Django REST Framework.",
  "category": 1,
  "level": "beginner",
  "price": "49.99",
  "thumbnail": null,
  "topics": [1, 2],
  "badge": "new",
  "published": false
}
```

## Publishing Rules

If `published` is set to `true`, the API requires:

- a non-null `price`
- a thumbnail
- at least one topic

Otherwise it returns:

```http
400 Bad Request
```

```json
{
  "price": ["Price is required to publish the course."],
  "thumbnail": ["A thumbnail is required to publish the course."],
  "topics": ["At least one topic must be selected to publish."]
}
```

These rules also apply to `PATCH` and `PUT`, evaluated against the merged
result of the existing course and the incoming payload.

---

# 4. Update Course

## Endpoints

```http
PATCH /api/courses/{id}/
PUT   /api/courses/{id}/
```

## Authentication

Required. Only the owning instructor can update the course.

## Request

`PATCH` accepts any subset of the writable fields.

```json
{
  "title": "Advanced Backend Development with Django",
  "published": true
}
```

`PUT` is a full replacement and requires every non-optional field
(`title`, `description`, `category`, `level`). A partial `PUT` returns:

```http
400 Bad Request
```

```json
{
  "description": ["This field is required."],
  "category": ["This field is required."],
  "level": ["This field is required."]
}
```

## Success

```http
200 OK
```

```json
{
  "id": 12,
  "title": "Advanced Backend Development with Django",
  "description": "Learn to build production APIs with Django REST Framework.",
  "category": 1,
  "level": "beginner",
  "price": "49.99",
  "thumbnail": "http://localhost:8000/media/courses/django.png",
  "topics": [1, 2],
  "badge": "new",
  "published": true
}
```

---

# 5. Delete Course

## Endpoint

```http
DELETE /api/courses/{id}/
```

## Authentication

Required. Only the owning instructor can delete the course.

## Success

```http
204 No Content
```

Deleting a course also deletes its sections, lessons, and enrollments.

---

# 6. My Courses

## Endpoint

```http
GET /api/courses/mine/
```

## Authentication

Required. Must be authenticated as an instructor.

## Behavior

Returns the authenticated instructor's own courses, including unpublished
drafts.

This endpoint is **not paginated**. It returns every owned course in one
response and the payload has no `next` or `previous` keys.

## Success

```http
200 OK
```

```json
{
  "count": 1,
  "results": [
    {
      "id": 12,
      "title": "Backend Development with Django",
      "category": "Programming",
      "level": "beginner",
      "price": "49.99",
      "thumbnail": null,
      "topics": ["Python", "Django"],
      "badge": "new",
      "instructor": {
        "id": 4,
        "username": "abdallah",
        "email": "abdallah@example.com"
      },
      "published": false,
      "is_enrolled": false,
      "created_at": "2026-07-16T09:15:00Z"
    }
  ]
}
```

---

# 7. List Categories

## Endpoint

```http
GET /api/categories/
```

## Authentication

Required. Must be authenticated as an instructor.

## Success

```http
200 OK
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Programming",
      "slug": "programming"
    }
  ]
}
```

Categories are created through the Django admin. There is no create, update, or
delete endpoint.

---

# 8. List Topics

## Endpoint

```http
GET /api/topics/
```

## Authentication

Required. Must be authenticated as an instructor.

## Success

```http
200 OK
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Python",
      "slug": "python"
    }
  ]
}
```

Topics are created through the Django admin. There is no create, update, or
delete endpoint.

---

# Known Issues

- **A negative `price` returns `500`.** The serializer does not validate the
  lower bound, so the database check constraint
  (`price_must_be_non_negative`) raises an `IntegrityError` instead of a `400`
  validation error. Needs a `min_value=0` on the serializer field.

---

# Future Milestones

Intentionally **out of scope** for this contract:

- Filtering, search, and ordering on the course list
- Stable ordering for paginated course results
- Category and topic management endpoints
- Ratings and reviews
- Enrollment counts on the course payloads
