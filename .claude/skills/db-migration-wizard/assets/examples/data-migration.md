# SQLModel Migration Script

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session
from app.models import Base, Task
import asyncio

async def migrate_add_due_date():
    """Add due_date column to tasks table."""
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        # Add column using raw SQL
        session.execute(
            "ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP"
        )
        session.execute(
            "CREATE INDEX ix_tasks_due_date ON tasks(due_date)"
        )
        session.commit()

    print("✅ Migration completed: Added due_date column")

if __name__ == "__main__":
    asyncio.run(migrate_add_due_date())
```

## Data Migration

```python
async def migrate_user_data():
    """Migrate user data from old schema to new."""
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        # Read from old table
        result = session.execute("SELECT * FROM old_users")

        for row in result:
            # Transform and insert into new table
            session.execute(
                "INSERT INTO users (email, full_name) VALUES (:email, :name)",
                {"email": row.email, "name": f"{row.first_name} {row.last_name}"}
            )

        session.commit()

    print("✅ Data migration completed")
```
