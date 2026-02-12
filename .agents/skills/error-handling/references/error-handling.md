## 13. Error handling

Error handling matters, but if it makes the main flow unreadable, it fails. Keep the happy path easy to see at a glance.

- In languages that support exceptions, prefer exceptions over error codes. This reduces “error checking” clutter in the caller’s main path.
- If you need to handle exceptions, separate responsibilities. Keep `try` as “one happy-path block,” and keep `catch` focused on “translate / record / cleanup.”
- Exceptions and errors from external APIs/DB/frameworks should be translated into your own domain language at the boundary, so inner code is not forced to depend on vendor-specific types or messages.
- Do not swallow exceptions. If you cannot continue, add context and rethrow. If you can continue, return a special-case value that restores the happy path.
- Do not default to returning or passing `null` (or `None` in Python). Prefer empty arrays, empty objects, or explicit special objects when possible.

### 13.1 Basic templates (by language)

Below are templates for “catch at the outer boundary, keep the inner code clean.” If the repository already has a preferred style, follow it.

#### Python

```python
class DomainError(RuntimeError):
    pass


def load_user(user_id: str) -> "User":
    try:
        row = repo.fetch_user_row(user_id)  # External boundary (DB/HTTP, etc.)
    except RepoError as e:
        raise DomainError(f"user load failed: user_id={user_id}") from e

    if row is None:  # If a boundary returns None, convert it here and fail fast
        raise DomainError(f"user not found: user_id={user_id}")

    return User.from_row(row)
```

#### C++

```cpp
class DomainError : public std::runtime_error {
 public:
  using std::runtime_error::runtime_error;
};

User LoadUser(UserId user_id, const UserRepository& repo) {
  try {
    const std::optional<UserRow> row = repo.FetchUserRow(user_id);  // External boundary (DB/HTTP, etc.)
    if (!row.has_value()) {
      throw DomainError("user not found: id=" + ToString(user_id));
    }
    return User::FromRow(*row);
  } catch (const RepoError& e) {
    const std::string msg =
        "user load failed: id=" + ToString(user_id) + " cause=" + std::string(e.what());
    throw DomainError(msg);
  }
}
```

#### Java

```java
public final class DomainException extends RuntimeException {
  public DomainException(String message, Throwable cause) { super(message, cause); }
  public DomainException(String message) { super(message); }
}

public User loadUser(String userId) {
  try {
    UserRow row = repo.fetchUserRow(userId); // External boundary (DB/HTTP, etc.)
    if (row == null) { // If you receive null at the boundary, convert it here
      throw new DomainException("user not found: userId=" + userId);
    }
    return User.fromRow(row);
  } catch (RepoException e) {
    throw new DomainException("user load failed: userId=" + userId, e);
  }
}
```

#### TypeScript

```ts
export class DomainError extends Error {
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
    this.name = "DomainError";
  }
}

export async function loadUser(userId: string): Promise<User> {
  try {
    const row = await repo.fetchUserRow(userId); // External boundary (DB/HTTP, etc.)
    if (row == null) { // Treat null/undefined together
      throw new DomainError(`user not found: userId=${userId}`);
    }
    return userFromRow(row);
  } catch (e) {
    if (e instanceof DomainError) throw e;
    throw new DomainError(`user load failed: userId=${userId}`, e);
  }
}
```

Notes:

- If you start doing multiple things inside a `try`, split the function. In general, a function with `try` should exist primarily to handle errors.
- If an external library “returns null/None,” absorb that in a thin wrapper and do not bring it into inner code.

