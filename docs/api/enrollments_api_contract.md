# Enrollments API Contract

**Project:** EduForge  
**Version:** v1  
**Base URL:** `http://localhost:8000/api/`

---

# Scope

This contract covers student enrollment into a course.

Only **free enrollment** is implemented. Paid enrollment requires the payments
milestone and is rejected by this endpoint today.

## Supported Endpoints

- `POST /api/courses/{course_id}/enroll/`

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

There is no `status` or `progress` field yet. Progress tracking is a future
milestone.

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

Only `POST` is supported. There is no way to read or cancel an enrollment yet.

---

# Known Issues

- **Published course with a `NULL` price returns `500`.** The free check
  compares `price > 0` without a null guard. Publishing through the API always
  sets a price, so this is only reachable for courses published through the
  Django admin or directly in the database.

---

# Future Milestones

Intentionally **out of scope** for this contract:

- Listing the authenticated user's enrollments
- Unenrolling / cancellation
- An `is_enrolled` flag on the Course Details response
- Paid enrollment, checkout, and payment webhooks
- Lesson progress and course completion
- Unlocking locked lesson videos for enrolled students
