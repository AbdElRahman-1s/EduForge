# Reviews API Contract

**Project:** EduForge  
**Version:** v1  
**Base URL:** `http://localhost:8000/api/`

---

# Scope

This contract covers course reviews and ratings: a public paginated list of
reviews per course, creation restricted to actively-enrolled students, and
author-only update/delete.

One review per (student, course) — a student can rate a course at most once.
Ratings are integers from 1 to 5, enforced at both the serializer and database
level.

## Supported Endpoints

- `GET /api/courses/{course_id}/reviews/` — public, paginated, newest-first
- `POST /api/courses/{course_id}/reviews/` — authenticated, enrolled students only
- `GET /api/reviews/{id}/` — author only
- `PATCH /api/reviews/{id}/` — author only
- `DELETE /api/reviews/{id}/` — author only

---

# Data Model

A review is a rating + optional comment left by a student on a course.

| Field         | Type     | Notes                                          |
| ------------- | -------- | ---------------------------------------------- |
| `id`          | integer  | Primary key                                    |
| `student`     | FK user  | The reviewer (authenticated user at creation)  |
| `course`      | FK course| The course being reviewed                      |
| `rating`      | integer  | 1–5; DB check constraint                       |
| `comment`     | text     | Optional; defaults to `""`                     |
| `created_at`  | datetime | Set automatically on creation                  |
| `updated_at`  | datetime | Set automatically on update; **not exposed** in responses |

`(student, course)` is unique — enforced by a `UniqueConstraint`. Duplicate
reviews are rejected with a clear message (see section 2).

Reviews are ordered newest-first (`-created_at`), with `id` descending as a
deterministic tie-breaker. The list endpoint returns pages of **5** reviews.

> `updated_at` exists on the model but is not in any response payload. Clients
> cannot currently tell when a review was last edited.

---

# Error Response Format

General errors:

```json
{
  "detail": "Error message."
}
```

The detail view uses `detail`-style errors. The create endpoint also returns
field-level validation errors for the rating:

```json
{
  "rating": ["Ensure this value is greater than or equal to 1."]
}
```

---

# 1. List Reviews

## Endpoint

```http
GET /api/courses/{course_id}/reviews/
```

## Authentication

None — public.

## Behavior

- Returns reviews for the course, newest-first.
- **Paginated, 5 per page.** The payload uses a load-more envelope: `count`,
  `next`, and `results`. There is **no** `previous` key.
- `next` is an absolute URL to the next page, or `null` when there are no more.
  Clients implementing "load more" should follow `next` until it is `null`.
- The `student` field is a nested `{id, username}` object.

## Success

```http
200 OK
```

```json
{
  "count": 2,
  "next": null,
  "results": [
    {
      "id": 12,
      "student": {
        "id": 4,
        "username": "reviewer"
      },
      "rating": 5,
      "comment": "Loved the Django module.",
      "created_at": "2026-09-01T12:30:19.998161Z"
    },
    {
      "id": 9,
      "student": {
        "id": 7,
        "username": "student_02"
      },
      "rating": 3,
      "comment": "",
      "created_at": "2026-08-30T09:15:02.101130Z"
    }
  ]
}
```

With more than 5 reviews, page 2:

```json
{
  "count": 7,
  "next": "http://localhost:8000/api/courses/3/reviews/?page=3",
  "results": [ "…5 more reviews…" ]
}
```

Empty course:

```json
{
  "count": 0,
  "next": null,
  "results": []
}
```

## Field Reference

| Field       | Notes                                          |
| ----------- | ---------------------------------------------- |
| `id`        | Review primary key (usable with `/api/reviews/{id}/`) |
| `student`   | Nested `{id, username}` of the reviewer        |
| `rating`    | Integer 1–5                                    |
| `comment`   | Free text; `""` when the reviewer left none    |
| `created_at`| When the review was created                    |

## Pagination

| Key      | Type             | Notes                                    |
| -------- | ---------------- | ---------------------------------------- |
| `count`  | integer          | Total number of reviews for the course   |
| `next`   | string \| null   | Absolute URL of the next page, or `null` |
| `results`| array            | Up to 5 reviews on this page             |

Page number is selected with `?page=N`. There is no `previous` and no
`page_size` override.

## Error Cases

### Course Does Not Exist

```http
404 Not Found
```

```json
{
  "detail": "No Course matches the given query."
}
```

> The course is looked up **without** a `published` filter, so a course that has
> been unpublished still exposes its reviews list. This mirrors the enroll
> endpoint, which also does not filter by `published`.

---

# 2. Create a Review

## Endpoint

```http
POST /api/courses/{course_id}/reviews/
```

## Authentication

Required.

```http
Authorization: Bearer <access_token>
```

## Request Body

```json
{
  "rating": 4,
  "comment": "Great pacing, but the last section felt rushed."
}
```

`rating` is required; `comment` is optional. Both `student` and `course` are
ignored in the body — the reviewer is the authenticated user and the course
comes from the URL.

## Who Can Review

| Caller                                    | Result                        |
| ----------------------------------------- | ----------------------------- |
| Student with an **active** enrollment     | Allowed                       |
| Enrolled student, enrollment **suspended**| Rejected (`403`)              |
| User with no enrollment in the course     | Rejected (`403`)              |
| Instructor, on **their own** course       | Rejected (`400`)              |
| Instructor, on **another** course         | Allowed if actively enrolled  |
| Anonymous                                 | Rejected (`401`)              |

## Eligibility Rules

Checks run in this order, and the first failure is returned:

1. The course must exist — otherwise `404`.
2. The caller must not be the course's own instructor.
3. The caller must have an **active** enrollment (`Enrollment.Status.ACTIVE`).
   Suspended enrollments do not count.
4. The caller must not already have a review on this course.

## Success

```http
201 Created
```

```json
{
  "id": 12,
  "student": {
    "id": 4,
    "username": "reviewer"
  },
  "rating": 4,
  "comment": "Great pacing, but the last section felt rushed.",
  "created_at": "2026-09-01T12:30:19.998161Z"
}
```

## Error Cases

### Course Does Not Exist

```http
404 Not Found
```

```json
{
  "detail": "No Course matches the given query."
}
```

### Instructor Reviewing Their Own Course

```http
400 Bad Request
```

```json
{
  "detail": "Instructors cannot review their own courses."
}
```

### No Active Enrollment

```http
403 Forbidden
```

```json
{
  "detail": "An active enrollment is required to review this course."
}
```

Returned both for a user with no enrollment at all and for a user whose only
enrollment is `suspended`.

### Already Reviewed

```http
400 Bad Request
```

```json
{
  "detail": "You have already reviewed this course."
}
```

Returned both by the pre-check and by the unique-constraint fallback, so
concurrent duplicate requests produce the same message rather than a `500`.

### Rating Out of Range

```http
400 Bad Request
```

```json
{
  "rating": ["Ensure this value is greater than or equal to 1."]
}
```

And for the upper bound:

```json
{
  "rating": ["Ensure this value is less than or equal to 5."]
}
```

### Missing Access Token

```http
401 Unauthorized
```

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Invalid or Expired Access Token

```http
401 Unauthorized
```

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid"
    }
  ]
}
```

### Wrong Method

```http
405 Method Not Allowed
```

```json
{
  "detail": "Method \"PUT\" not allowed."
}
```

Only `POST` and `GET` are supported on this route.

---

# 3. Retrieve a Review

## Endpoint

```http
GET /api/reviews/{id}/
```

## Authentication

Required, and the caller must be the review's author.

A review can only be read by the user who wrote it. There is no public
single-review endpoint — public consumers should use the course reviews list
(section 1).

## Success

```http
200 OK
```

```json
{
  "id": 12,
  "student": {
    "id": 4,
    "username": "reviewer"
  },
  "rating": 4,
  "comment": "Great pacing, but the last section felt rushed.",
  "created_at": "2026-09-01T12:30:19.998161Z"
}
```

## Error Cases

### Not the Author

```http
403 Forbidden
```

```json
{
  "detail": "You can only modify your own reviews."
}
```

### Review Does Not Exist

```http
404 Not Found
```

```json
{
  "detail": "No Review matches the given query."
}
```

---

# 4. Update a Review

## Endpoint

```http
PATCH /api/reviews/{id}/
```

## Authentication

Required, author only.

## Request Body

Partial updates are supported. Send any of:

```json
{ "rating": 5 }
```

```json
{ "comment": "Changed my mind — actually excellent." }
```

## Success

```http
200 OK
```

```json
{
  "id": 12,
  "student": {
    "id": 4,
    "username": "reviewer"
  },
  "rating": 5,
  "comment": "Changed my mind — actually excellent.",
  "created_at": "2026-09-01T12:30:19.998161Z"
}
```

## Error Cases

- `403` — caller is not the author (same body as section 3).
- `404` — review does not exist.
- `400` — `rating` out of range (same body as section 2).
- `401` — missing/invalid token.

---

# 5. Delete a Review

## Endpoint

```http
DELETE /api/reviews/{id}/
```

## Authentication

Required, author only.

## Success

```http
204 No Content
```

No response body. The review is removed permanently; deleting the course or the
student cascades to their reviews as well.

## Error Cases

- `403` — caller is not the author.
- `404` — review does not exist.
- `401` — missing/invalid token.

---

# Known Issues

- **No `updated_at` in responses.** The model tracks edits but the API does not
  expose them, so clients cannot distinguish a review from its edited form.
- **`GET /api/reviews/{id}/` is author-only.** There is no public single-review
  endpoint. If the frontend needs to deep-link to a review, it must use the
  course list.
- **Reviews survive unpublished courses.** Neither the list nor the create
  endpoint filters by `published`, consistent with the enroll contract. A
  course removed from the catalogue still shows its reviews.

---

# Future Milestones

Intentionally **out of scope** for this contract:

- Aggregated `avg_rating` / `review_count` on course list, course detail, and
  instructor analytics endpoints (next issue in this milestone)
- Edit timestamps surfaced to clients
- Review moderation (flagging, hiding)
- Sorting by rating or by "most helpful"
- Pagination cursor beyond the current `next`-only envelope
- Instructor replies to reviews
