# Authentication API Contract

**Project:** EduForge
**Version:** v3
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

---

# User Roles

EduForge currently supports two user roles.

| Role         | Description                                                         |
| ------------ | ------------------------------------------------------------------- |
| `student`    | Can browse courses, enroll in courses, and track learning progress. |
| `instructor` | Can create, update, and manage their own courses.                   |

Future endpoints will enforce permissions based on the authenticated user's role.

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

| Field            | Rules                                                |
| ---------------- | ---------------------------------------------------- |
| username         | Required, unique, 3–30 characters                    |
| email            | Required, valid email, unique                        |
| password         | Required, validated using Django password validators |
| confirm_password | Must match password                                  |
| role             | Required, must be either `student` or `instructor`   |

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

---

## Error Cases

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

Validation errors for username, email, and password remain unchanged.

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
HttpOnly;
Secure;
SameSite=Lax;
Path=/api/auth/
```

> During local development, `Secure` may be disabled.

---

## Error Cases

### Invalid Credentials

```json
{
  "detail": "Invalid email or password."
}
```

Other validation errors remain unchanged.

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

---

## Error Cases

### Refresh Cookie Missing

```json
{
  "detail": "Refresh token not provided."
}
```

### Invalid or Expired Refresh Token

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

The backend blacklists the Refresh Token and removes the cookie from the browser.

---

## Error Cases

### Missing Refresh Cookie

```json
{
  "detail": "Refresh token not provided."
}
```

### Invalid Refresh Token

```json
{
  "detail": "Invalid refresh token."
}
```

### Missing Access Token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

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

---

## Error Cases

### Missing Access Token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Invalid or Expired Access Token

```json
{
  "detail": "Token is invalid or expired."
}
```
