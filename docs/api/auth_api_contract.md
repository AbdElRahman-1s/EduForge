# Authentication API Contract

**Project:** EduForge
**Version:** v4
**Base URL:** `http://localhost:8000/api/auth/`

---

# Authentication Flow

```text
Register (Choose Role)
        ↓
Login
        ↓
Receive Access Token
+
Browser stores Refresh Token in HttpOnly Cookie
        ↓
Access Protected APIs
        ↓
Access Token Expires
        ↓
POST /token/refresh/
(Browser automatically sends Refresh Cookie)
        ↓
Receive New Access Token
        ↓
Logout
(Browser sends Refresh Cookie)
```

---

# Authentication Strategy

- Access Token is returned in the response body.
- Refresh Token is stored as an **HttpOnly Cookie**.
- JavaScript **cannot access** the Refresh Token.
- The browser automatically sends the Refresh Cookie when calling:
  - `POST /api/auth/token/refresh/`
  - `POST /api/auth/logout/`

- Backend is responsible for setting and deleting the Refresh Cookie.

## Token Lifetimes

| Item                        | Value      |
| --------------------------- | ---------- |
| Access token lifetime       | 15 minutes |
| Refresh token lifetime      | 15 days    |
| Refresh **cookie** max-age  | 7 days     |

> The cookie expires before the token it carries. After 7 days the browser drops
> the cookie and the user must log in again, even though the refresh token
> itself is still valid for 15 days.

## Refresh Rotation

`POST /api/auth/token/refresh/` issues a **new access token only**. It does not
rotate the refresh token and does not update the cookie. The same refresh token
stays valid until it expires or the user logs out.

> The project's JWT settings enable `ROTATE_REFRESH_TOKENS` and
> `BLACKLIST_AFTER_ROTATION`, but the refresh endpoint is a custom view that
> does not use SimpleJWT's rotating serializer, so those settings have no effect
> on this flow.

---

# User Roles

EduForge currently supports two user roles.

| Role         | Description                                                         |
| ------------ | ------------------------------------------------------------------- |
| `student`    | Can browse courses, enroll in courses, and track learning progress. |
| `instructor` | Can create, update, and manage their own courses.                   |

Endpoints enforce permissions based on the authenticated user's role. See
`courses_api_contract.md` and `curriculum_api_contract.md`.

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

## Expired or Malformed Access Token

Access-token failures are produced by SimpleJWT and carry extra keys beyond
`detail`:

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

Clients should treat any `401` on a protected endpoint as "refresh and retry",
rather than matching on the message text.

---

# 1. Register

## Endpoint

```http
POST /api/auth/register/
```

## Request

```json
{
  "username": "abdallah",
  "email": "abdallah@example.com",
  "password": "StrongPassword123!",
  "confirm_password": "StrongPassword123!",
  "role": "student"
}
```

---

## Validation Rules

| Field            | Rules                                                            |
| ---------------- | ---------------------------------------------------------------- |
| username         | Required, unique, letters/numbers/underscores only, 3–30 chars    |
| email            | Required, valid email, unique                                     |
| password         | Required, validated using Django password validators              |
| confirm_password | Must match password                                               |
| role             | Optional, `student` or `instructor`, defaults to `student`         |

> `role` is **not** required. Omitting it creates a student account.

---

## Success

```http
201 Created
```

```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "username": "abdallah",
    "email": "abdallah@example.com",
    "role": "student"
  }
}
```

Registration does not log the user in. No tokens are issued and no cookie is
set — the client must call `POST /api/auth/login/` next.

---

## Error Cases

All registration errors return `400 Bad Request`.

### Passwords Don't Match

```json
{
  "confirm_password": ["Passwords do not match."]
}
```

### Invalid Role

```json
{
  "role": ["\"admin\" is not a valid choice."]
}
```

### Invalid Username

Wrong length or disallowed characters:

```json
{
  "username": [
    "Username can only contain letters, numbers, and underscores (3-30 chars)"
  ]
}
```

Characters rejected by Django's own username validator are reported first, with
a different message:

```json
{
  "username": [
    "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."
  ]
}
```

### Duplicate Email

```json
{
  "email": ["user with this email already exists."]
}
```

### Weak Password

Django's password validators return every failure at once:

```json
{
  "password": [
    "This password is too short. It must contain at least 8 characters.",
    "This password is too common.",
    "This password is entirely numeric."
  ]
}
```

---

# 2. Login

## Endpoint

```http
POST /api/auth/login/
```

## Request

```json
{
  "email": "abdallah@example.com",
  "password": "StrongPassword123!"
}
```

---

## Success

```http
200 OK
```

### Response Body

```json
{
  "access": "jwt_access_token",
  "user": {
    "id": 1,
    "username": "abdallah",
    "email": "abdallah@example.com",
    "role": "student"
  }
}
```

### Response Headers

```http
Set-Cookie:
refresh=<jwt_refresh_token>;
Max-Age=604800;
HttpOnly;
Secure;
SameSite=Lax;
Path=/api/auth/
```

> `Secure` is set only when `DEBUG` is off. During local development the flag is
> omitted.

Because `Path` is `/api/auth/`, the cookie is sent only to auth endpoints. It is
not attached to course or enrollment requests.

---

## Error Cases

### Invalid Credentials

```http
401 Unauthorized
```

```json
{
  "detail": "Invalid email or password."
}
```

The same response is returned for an unknown email and for a wrong password.

### Missing or Malformed Fields

```http
400 Bad Request
```

```json
{
  "email": ["This field is required."]
}
```

---

# 3. Refresh Access Token

## Endpoint

```http
POST /api/auth/token/refresh/
```

## Authentication

The browser automatically sends the Refresh Cookie.

No Authorization header is required.

---

## Request Body

None.

---

## Success

```http
200 OK
```

```json
{
  "access": "new_access_token"
}
```

No new cookie is set — see "Refresh Rotation" above.

---

## Error Cases

### Refresh Cookie Missing

```http
401 Unauthorized
```

```json
{
  "detail": "Refresh token not provided."
}
```

### Invalid, Expired, or Blacklisted Refresh Token

```http
401 Unauthorized
```

```json
{
  "detail": "Token is invalid or expired."
}
```

---

# 4. Logout

## Endpoint

```http
POST /api/auth/logout/
```

## Headers

```http
Authorization: Bearer <access_token>
```

The browser automatically includes the Refresh Cookie.

Both credentials are required: a valid access token **and** the refresh cookie.

---

## Request Body

None.

---

## Success

```http
205 Reset Content
```

```json
{
  "message": "Logged out successfully."
}
```

### Response Headers

```http
Set-Cookie:
refresh=;
Max-Age=0;
HttpOnly;
Secure;
SameSite=Lax;
Path=/api/auth/
```

The backend blacklists the Refresh Token and removes the cookie from the
browser.

---

## Error Cases

### Missing Refresh Cookie

```http
401 Unauthorized
```

```json
{
  "detail": "Refresh token not provided."
}
```

### Invalid Refresh Token

```http
401 Unauthorized
```

```json
{
  "detail": "Invalid refresh token."
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

> When the access token is missing or expired, logout fails and the cookie is
> left in place. Clients should refresh the access token first, then log out.

---

# 5. Profile

## Endpoint

```http
GET /api/auth/me/
```

## Headers

```http
Authorization: Bearer <access_token>
```

---

## Success

```http
200 OK
```

```json
{
  "id": 1,
  "first_name": "Abdallah",
  "last_name": "Rabie",
  "username": "abdallah",
  "email": "abdallah@example.com",
  "role": "student",
  "date_joined": "2026-07-10T18:32:14Z"
}
```

`first_name` and `last_name` are empty strings unless set through the Django
admin — registration does not collect them.

`date_joined` is the account's `created_at` timestamp.

This endpoint is read-only. There is no profile update endpoint yet.

---

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

See "Expired or Malformed Access Token" above for the exact body.

---

# Future Milestones

Intentionally **out of scope** for this contract:

- Email verification
- Password reset / change
- Profile update and avatar upload
- Social login
- Refresh token rotation on the refresh endpoint
