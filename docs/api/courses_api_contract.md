# Courses API Contract

**Project:** EduForge  
**Version:** v2  
**Base URL:** `http://localhost:8000/api/`

---

# Overview

This contract documents the current courses app API for public course browsing and instructor-managed course operations.

## Supported Endpoints

- `GET /api/courses/`
- `POST /api/courses/`
- `GET /api/courses/{id}/`
- `PATCH /api/courses/{id}/`
- `DELETE /api/courses/{id}/`
- `GET /api/courses/mine/`
- `GET /api/categories/`
- `GET /api/topics/`

---

# Access and Permissions

## Public Access

- Anyone can list published courses.
- Anyone can view a published course detail.

## Instructor Access

- Authenticated instructors can create courses.
- Authenticated instructors can view their own courses via `/api/courses/mine/`.
- Only the owning instructor can update or delete a course.

## Student Access

- Students cannot create, update, delete courses, or access `/api/courses/mine/`.

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

# Pagination

List endpoints use page-based pagination.

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
- Unpublished courses do not appear in this endpoint.

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
      "thumbnail": null,
      "topics": ["Python", "Django"],
      "badge": "new",
      "instructor": {
        "id": 4,
        "username": "abdallah",
        "email": "abdallah@example.com"
      },
      "published": true,
      "created_at": "2026-07-01T10:00:00Z"
    }
  ]
}
```

---

# 2. Get Course Detail

## Endpoint

```http
GET /api/courses/{id}/
```

## Authentication

None required.

## Behavior

- Returns a published course only.
- Unpublished courses return `404 Not Found` for non-owners and anonymous users.

## Success

```http
200 OK
```

```json
{
  "id": 1,
  "title": "Backend Development with Django",
  "description": "Learn to build production APIs with Django REST Framework.",
  "category": "Programming",
  "level": "beginner",
  "price": "0.00",
  "thumbnail": null,
  "topics": ["Python", "Django"],
  "badge": "new",
  "instructor": {
    "id": 4,
    "username": "abdallah",
    "email": "abdallah@example.com"
  },
  "published": true,
  "created_at": "2026-07-01T10:00:00Z"
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
| `title`       | Required, 3–150 characters                                     |
| `description` | Required                                                       |
| `category`    | Required, must reference an existing category ID               |
| `level`       | Required, one of `beginner`, `intermediate`, `advanced`, `all` |
| `price`       | Optional, must be non-negative                                 |
| `topics`      | Optional, list of topic IDs                                    |
| `badge`       | Optional, one of `bestseller`, `hot`, `new`, `none`            |
| `published`   | Optional boolean                                               |

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

Otherwise it returns validation errors.

---

# 4. Update Course

## Endpoint

```http
PATCH /api/courses/{id}/
```

## Authentication

Required. Only the owning instructor can update the course.

## Request

Any subset of the writable fields may be provided.

```json
{
  "title": "Advanced Backend Development with Django",
  "published": true
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
  "thumbnail": null,
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

---

# 6. My Courses

## Endpoint

```http
GET /api/courses/mine/
```

## Authentication

Required. Must be authenticated as an instructor.

## Behavior

Returns the authenticated instructor’s own courses, including unpublished drafts.

## Success

```http
200 OK
```

```json
{
  "count": 2,
  "next": null,
  "previous": null,
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

\*\*\* End Patch
