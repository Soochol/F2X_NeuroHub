# Quick Start - F2X NeuroHub MES Database Deployment

## One-Command Deployment

```bash
# Navigate to database directory
cd /path/to/F2X_NeuroHub/database

# Run deployment (database must exist)
psql -U postgres -d f2x_neurohub_mes -f deploy.sql
```

## Prerequisites Checklist

- [ ] PostgreSQL 14+ installed
- [ ] User has superuser or database owner privileges
- [ ] Database `f2x_neurohub_mes` exists (or will be created)
- [ ] All DDL files present in `ddl/` directory

## What Gets Created

### Functions (5)
- `update_timestamp()` - Auto-updates timestamps
- `prevent_audit_modification()` - Protects audit logs
- `log_audit_event()` - Audit trail logging
- `prevent_process_deletion()` - Protects processes
- `prevent_user_deletion()` - Protects users

### Tables (7)
1. `product_models` - Product definitions
2. `processes` - 8 manufacturing processes (pre-loaded)
3. `users` - System users
4. `lots` - Production batches
5. `serials` - Individual units
6. `process_data` - Process execution records
7. `audit_logs` - Audit trail (with 3 partitions)

## Dependency Tree

```
Functions
  └─> product_models, processes, users (Group A)
        └─> lots (Group B)
              └─> serials (Group C)
                    └─> process_data (Group D)

users
  └─> audit_logs (Group E)
```

## Execution Time

**Total**: 15-25 seconds (on standard hardware)

## Verification Commands

```sql
-- Connect to database
\c f2x_neurohub_mes

-- Check table count (should be 10: 7 tables + 3 partitions)
SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';

-- Check function count (should be 5)
SELECT COUNT(*) FROM pg_proc WHERE pronamespace = 'public'::regnamespace AND prokind = 'f';

-- Check process data (should be 8)
SELECT COUNT(*) FROM processes;

-- Check database size
SELECT pg_size_pretty(pg_database_size(current_database()));
```

## Common Issues

### Database doesn't exist?
```bash
createdb -U postgres f2x_neurohub_mes
```

### Permission denied?
```bash
psql -U postgres -d f2x_neurohub_mes -f deploy.sql
```

### Files not found?
```bash
# Make sure you're in the database directory
pwd  # Should show: /path/to/F2X_NeuroHub/database
```

### Need to start fresh?
```sql
-- WARNING: Deletes all data!
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

## Post-Deployment (Essential)

```sql
-- 1. Create system user (required for audit logging)
INSERT INTO users (username, full_name, role, email, is_active)
VALUES ('system', 'System User', 'SYSTEM', 'system@example.com', TRUE);

-- 2. Create admin user
INSERT INTO users (username, full_name, role, email, is_active)
VALUES ('admin', 'Administrator', 'ADMIN', 'admin@example.com', TRUE);

-- 3. Create audit partitions for next 6 months
SELECT create_future_audit_partitions(6);
```

## Next Steps

1. Review [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions
2. Insert initial product models
3. Configure application roles and permissions
4. Set up database backups
5. Configure monitoring

## Support

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for comprehensive troubleshooting and configuration guides.

---

**Deployment Script**: `deploy.sql`
**Full Guide**: `DEPLOYMENT_GUIDE.md`
**Database Version**: PostgreSQL 14+
