# Commit message (da commit san)
feat: write query F3 for topics with most thumbs-down

# PR title
feat: write query F3 for topics with most thumbs-down

# PR description
## Summary
Add query F3 ("Which topics got the most thumbs-down?") to `sql/my_queries.sql`.

- JOIN `interaction` with `feedback` on `request_id`
- Filter `rating = -1` (thumbs-down only)
- GROUP BY topic, ORDER BY count descending

## Query
```sql
SELECT i.topic, COUNT(*) AS thumbs_down
FROM interaction i
JOIN feedback f ON f.request_id = i.request_id
WHERE f.rating = -1
GROUP BY i.topic
ORDER BY thumbs_down DESC;
```

## Result (seeded with `python scripts/seed.py assistant.db 300`)
| topic   | thumbs_down |
|---------|-------------|
| NULL    | 17          |
| H26-5.3 | 8           |
| H26-4.2 | 8           |
| H26-7.2 | 2           |

`NULL` = interactions without a topic (fee, office, greeting, unknown).

## How to test
```
python scripts/migrate.py assistant.db
python scripts/seed.py assistant.db 300
```
Then run the query in DB Browser for SQLite (Execute SQL).

Closes #36
