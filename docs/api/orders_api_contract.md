# Orders API Contract

**Project:** EduForge  
**Version:** v1  
**Base URL:** `http://localhost:8000/api/`

---

# Overview

This contract covers the paid-enrollment lifecycle: creating a Stripe Checkout
Session, Stripe webhook fulfillment, and (planned) order history.

A paid course follows this flow:

```text
student → POST /checkout/  → Stripe hosted page → pays/cancels
   ↓ (webhook)
Stripe → POST /webhooks/stripe/  → Order paid + active Enrollment
```

The webhook-created enrollment is an ordinary `Enrollment` row — identical to a
free enrollment — so paid students unlock lesson videos, reviews, and
`is_enrolled` through the same active-only entitlement definition. See
`enrollments_api_contract.md`.

## Supported Endpoints

- `POST /api/courses/{course_id}/checkout/`
- `POST /api/webhooks/stripe/`

Order **history** (listing a user's orders) is not implemented yet — see
Future Work.

---

# Data Model

## Order

An order is a **purchase attempt**, not ownership. It snapshots the price at
checkout time; ownership is created separately as an `Enrollment`.

| Field                | Type     | Notes                                            |
| -------------------- | -------- | ------------------------------------------------ |
| `id`                 | integer  | Primary key                                      |
| `student`            | FK user  | The student who is buying                        |
| `course`             | FK course| The course being bought                          |
| `amount`             | decimal  | Price snapshot (`max_digits=7`, `decimal_places=2`) |
| `status`             | string   | `pending`, `paid`, `failed`, `refunded`, `expired` |
| `provider_reference` | string   | Stripe Checkout Session id                       |
| `created_at`         | datetime | Set automatically                                |
| `updated_at`         | datetime | Set automatically                                |

A `pending` order becomes `paid` only when the webhook confirms payment. A
`paid` order is the single source of truth for "this payment succeeded".

There is **no** `unique_together(student, course)` on orders — a student may
have several attempts. The single-enrollment invariant lives on `Enrollment`.

## Enrollment (created on fulfillment)

When an order is fulfilled, the webhook creates `Enrollment(student, course,
status=active)`. Because `Enrollment` has `unique_together(student, course)`,
at most one enrollment per student/course ever exists; a replayed webhook
cannot create a second one.

---

# Error Response Format

All orders endpoints return `detail`-style errors:

```json
{
  "detail": "Error message."
}
```

No field-level validation is performed on these routes.

---

# 1. Checkout

## Endpoint

```http
POST /api/courses/{course_id}/checkout/
```

## Authentication

Required.

```http
Authorization: Bearer <access_token>
```

## Request Body

None. The course is taken from the URL; any body sent is ignored.

## Behavior

1. Validates the request (see Guard Rails below).
2. Expires any earlier `pending` order for the same (student, course) — only one
   live checkout per course.
3. Creates a fresh `pending` `Order` snapshotting `amount = course.price`.
4. Creates a Stripe Checkout Session (`mode=payment`) through `gateways.py` —
   the only module that talks to Stripe.
5. Stores the session id in `provider_reference` and returns the hosted
   checkout URL.

## Guard Rails

Checks run in this order; the first failure is returned:

| Caller / course state                        | Result                                        |
| -------------------------------------------- | --------------------------------------------- |
| Missing or invalid token                     | `401`                                         |
| Course does not exist                        | `404`                                         |
| Course's own instructor                      | `400` "Instructors cannot purchase their own courses." |
| Course not published                         | `400` "Course is not published"               |
| Course is free (`price` null or `0`)         | `400` "Course is free, use /api/courses/{course_id}/enroll/" |
| Caller already actively enrolled             | `400` "You are already enrolled in this course." |
| Stripe API call fails                        | `500`; the order is marked `failed`           |

A **suspended** enrollment does not block checkout (the student may buy again).

## Success

```http
200 OK
```

```json
{
  "order_id": 12,
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...fidn..."
}
```

`checkout_url` is the Stripe-hosted Checkout page. The client should redirect
the browser there. After payment, Stripe redirects to `STRIPE_SUCCESS_URL`; if
the student cancels, to `STRIPE_CANCEL_URL` (both default to the course page).

> The order stays `pending` until the webhook confirms the payment — the
> checkout response does **not** enroll the student.

---

# 2. Webhook

## Endpoint

```http
POST /api/webhooks/stripe/
```

## Authentication

None — this endpoint is **not** under JWT. It is `AllowAny` + `@csrf_exempt`.
Stripe's request signature is the credential.

Headers:

```http
Stripe-Signature: t=...,v1=...
```

The raw request body and this header are verified with
`stripe.Webhook.construct_event` using `STRIPE_WEBHOOK_SECRET`. A bad signature
is rejected with `400` before any business logic runs.

## Events Handled

### `checkout.session.completed`

The order is looked up by `provider_reference == session.id`, then:

1. **Amount integrity** — `session.amount_total` (cents) must equal
   `order.amount × 100`. On mismatch the order is marked `failed` and no
   enrollment is created.
2. **Atomic claim** — the order moves `pending → paid` via one conditional
   update, so a duplicate delivery can never double-claim.
3. **Enrollment** — `Enrollment(student, course, status=active)` is created.
   `unique_together(student, course)` is the cross-database backstop: an
   `IntegrityError` is swallowed and the event still returns `200`.

### `checkout.session.payment_failed`

The matching `pending` order is marked `failed`. No enrollment is created.

## Idempotency

The transition is strictly `pending → paid`. A replayed `completed` event on an
already-`paid` order returns `200` without re-enrolling or changing state.
Stripe retries failed deliveries, and the endpoint returns `200` to acknowledge
a handled event (or `5xx` on a transient error, prompting Stripe to retry).

## Responses

| Outcome                 | Status |
| ----------------------- | ------ |
| Event handled           | `200`  |
| Invalid signature       | `400`  |
| Transient failure       | `5xx` (Stripe retries) |

---

# Future Work

- **Order history** — a `GET` endpoint listing the authenticated user's orders
  (e.g. `GET /api/orders/mine/`), returning `OrderSerializer` fields:
  `id`, `course_id`, `amount`, `status`, `provider_reference`, `created_at`.
  The serializer already exists in `apps/orders/serializers.py`.
- Refunds / `checkout.session.refunded`-style reconciliation
- Automatic expiry of abandoned `pending` orders
