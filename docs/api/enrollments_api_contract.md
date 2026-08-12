# Enrollments API Contract

**Project:** EduForge  
**Version:** v2  
**Base URL:** `http://localhost:8000/api/`

---

# Scope

This contract covers student enrollment into a course and listing the
authenticated user's own enrollments.

Only **free enrollment** is implemented. Paid enrollment requires the payments
milestone and is rejected by this endpoint today.

## Supported Endpoints

- `POST /api/courses/{course_id}/enroll/`
- `GET /api/enrollments/mine/`

---

# Data Model

An enrollment is a link between a user and a course.

| Field         | Type     | Notes                                 |
| ------------- | -------- | ------------------------------------- |
| `id`          | integer  | Primary key                           |
| `student`     | FK user  | The authenticated user who enrolled   |
| `course`      | FK course| The course enrolled into              |
| `enrolled_at` | datetime | Set automatically on creation         |

`(student, course)` is unique — a user cannot enroll twice in the same course.

Enrollments are ordered newest-first (`-enrolled_at`) at the model level.

There is no `status` or `progress` field on the model yet. The
`progress_percent` value exposed by `GET /api/enrollments/mine/` is a hardcoded
placeholder — see section 2.

---

# Error Response Format

General errors:

```json
{
  "detail": "Error message."
}
```

This endpoint returns **only** `detail`-style errors. It performs no field-level
validation, so the `{"field": ["..."]}` form never appears here.

---

# 1. Enroll in a Course

## Endpoint

```http
POST /api/courses/{course_id}/enroll/
```

## Authentication

Required.

```http
Authorization: Bearer <access_token>
```

## Request Body

None.

The course is taken from the URL. Any body sent is ignored — including a
`course_id` key, which cannot be used to enroll in a different course.

---

## Who Can Enroll

| Caller                                    | Result                        |
| ----------------------------------------- | ----------------------------- |
| Student                                   | Allowed                       |
| Instructor, on **another** instructor's course | Allowed                  |
| Instructor, on **their own** course       | Rejected (`400`)              |
| Anonymous                                 | Rejected (`401`)              |

Role is not restricted to `student`. The only role-based rule is that an
instructor cannot enroll in a course they own.

---

## Eligibility Rules

Checks run in this order, and the first failure is returned:

1. The course must exist — otherwise `404`.
2. The caller must not be the course's own instructor.
3. The course must be published.
4. The course must be free (`price` equal to `0`).
5. The caller must not already be enrolled.

---

## Success

```http
201 Created
```

```json
{
  "id": 1,
  "course_id": 1,
  "enrolled_at": "2026-08-11T12:30:19.998161Z"
}
```

The response contains the enrollment only. It does not embed the course or the
student.

---

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

Applies to unpublished courses as well — see the note below.

### Instructor Enrolling in Their Own Course

```http
400 Bad Request
```

```json
{
  "detail": "Instructors cannot enroll in their own courses"
}
```

### Course Is Not Published

```http
400 Bad Request
```

```json
{
  "detail": "Course is not published"
}
```

> Note: unpublished courses are **not** hidden by this endpoint. The course is
> looked up without a `published` filter, so an unpublished course returns this
> `400` rather than a `404`. This differs from `GET /api/courses/{id}/`, which
> returns `404` for unpublished courses the caller does not own.

### Course Is Not Free

```http
400 Bad Request
```

```json
{
  "detail": "Course is not free"
}
```

Returned for any course with `price` greater than `0`. Paid enrollment is not
supported yet.

### Already Enrolled

```http
400 Bad Request
```

```json
{
  "detail": "You are already enrolled in this course."
}
```

Returned both by the pre-check and by the unique-constraint fallback, so
concurrent duplicate requests produce the same message rather than a `500`.

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
  "detail": "Method \"GET\" not allowed."
}
```

Only `POST` is supported on this route.

---

# 2. List My Enrollments

## Endpoint

```http
GET /api/enrollments/mine/
```

## Authentication

Required.

```http
Authorization: Bearer <access_token>
```

Any authenticated user may call this endpoint. It is not restricted to the
`student` role — an instructor who enrolled in another instructor's course sees
that enrollment here.

## Behavior

- Returns only the authenticated user's own enrollments. There is no way to read
  another user's enrollments.
- Ordered newest-first by `enrolled_at`.
- Courses that have since been **unpublished** are still returned. Enrollment
  survives the course leaving the catalogue.
- This endpoint is **not paginated**. It returns every enrollment in one
  response and the payload has no `next` or `previous` keys.

## Success

```http
200 OK
```

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "title": "Backend Development with Django",
      "thumbnail": "http://localhost:8000/media/courses/django.png",
      "badge": "new",
      "category": "Programming",
      "level": "beginner",
      "total_lessons": 4,
      "total_duration_seconds": 400,
      "instructor": {
        "id": 4,
        "username": "abdallah",
        "email": "abdallah@example.com"
      },
      "enrolled_at": "2026-08-12T07:19:48.088836Z",
      "progress_percent": 0
    },
    {
      "id": 2,
      "title": "Intro to React",
      "thumbnail": null,
      "badge": "none",
      "category": "Programming",
      "level": "beginner",
      "total_lessons": 0,
      "total_duration_seconds": 0,
      "instructor": {
        "id": 4,
        "username": "abdallah",
        "email": "abdallah@example.com"
      },
      "enrolled_at": "2026-08-12T07:19:48.089273Z",
      "progress_percent": 0
    }
  ]
}
```

Empty result:

```json
{
  "count": 0,
  "results": []
}
```

## Field Reference

| Field                    | Notes                                                       |
| ------------------------ | ----------------------------------------------------------- |
| `id`                     | **The course ID, not the enrollment ID** — see warning below |
| `title`                  | Course title                                                |
| `thumbnail`              | Absolute URL, or `null` when no image was uploaded          |
| `badge`                  | One of `bestseller`, `hot`, `new`, `none`                    |
| `category`               | Category **name**                                            |
| `level`                  | One of `beginner`, `intermediate`, `advanced`, `all`         |
| `total_lessons`          | Lesson count across all sections; `0` for an empty curriculum |
| `total_duration_seconds` | Summed lesson duration; `0` for an empty curriculum          |
| `instructor`             | Nested `{id, username, email}`                                |
| `enrolled_at`            | When the user enrolled                                       |
| `progress_percent`       | Always `0` — placeholder, see below                          |

> **`id` is the course ID.** The payload is shaped as a course card for the
> "My Learning" view, so `id` can be used directly with
> `GET /api/courses/{id}/`. The enrollment's own primary key is **not exposed
> anywhere** in this response, so there is currently no way for a client to
> address an individual enrollment.

> **`progress_percent` is hardcoded to `0`.** No progress is tracked yet. Do not
> build client logic that expects this value to change.

The payload deliberately omits `price`, `published`, and `description`. Clients
that need those must fetch `GET /api/courses/{id}/`.

## Error Cases

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

See the token error body in section 1.

### Wrong Method

```http
405 Method Not Allowed
```

```json
{
  "detail": "Method \"POST\" not allowed."
}
```

Only `GET` is supported. There is no unenroll endpoint.

---

# Known Issues

- **Published course with a `NULL` price returns `500`.** The free check
  compares `price > 0` without a null guard. Publishing through the API always
  sets a price, so this is only reachable for courses published through the
  Django admin or directly in the database.
- **`GET /api/enrollments/mine/` exposes no enrollment identifier.** `id` is the
  course ID, so an unenroll endpoint cannot be addressed by enrollment ID
  without changing this payload.

---

# Future Milestones

Intentionally **out of scope** for this contract:

- Unenrolling / cancellation
- Pagination on `GET /api/enrollments/mine/`
- Real `progress_percent` values
- An `is_enrolled` flag on the Course Details response
- Paid enrollment, checkout, and payment webhooks
- Lesson progress and course completion
- Unlocking locked lesson videos for enrolled students
