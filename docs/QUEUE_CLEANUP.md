# Queue Cleanup Documentation

## Overview

The `cleanup_old_queues` management command automatically deletes old completed queue records from the `rqueue_rqueue` table to prevent database bloat.

## Why Cleanup is Needed

Queue records accumulate over time. With 10,000+ records, the database can become slow and consume unnecessary storage. This command safely removes old completed records while preserving recent data for auditing and debugging.

## Usage

### Basic Usage

```bash
# Delete all completed records older than 30 days (default)
python manage.py cleanup_old_queues

# Delete records older than 60 days
python manage.py cleanup_old_queues --days=60

# Preview what would be deleted without actually deleting
python manage.py cleanup_old_queues --days=30 --dry-run

# Verbose output with detailed information
python manage.py cleanup_old_queues --verbose
```

### Advanced Usage - Different Retention by Status

```bash
# Keep FINISHED for 30 days, ABORTED for 60 days, FAILED for 90 days
python manage.py cleanup_old_queues \
  --finished-days=30 \
  --aborted-days=60 \
  --failed-days=90

# Dry run with custom retention
python manage.py cleanup_old_queues \
  --finished-days=7 \
  --aborted-days=14 \
  --failed-days=30 \
  --dry-run \
  --verbose
```

## Command Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--days` | int | None | Delete all completed records older than N days (overrides individual settings) |
| `--finished-days` | int | 30 | Delete FINISHED records older than N days |
| `--aborted-days` | int | 60 | Delete ABORTED records older than N days |
| `--failed-days` | int | 90 | Delete FAILED records older than N days |
| `--dry-run` | flag | False | Preview deletion without actually deleting |
| `--verbose` | flag | False | Show detailed information |

## Recommended Retention Policy

Based on typical usage patterns:

- **FINISHED**: 30 days - Successful locks, large volume, low debugging value
- **ABORTED**: 60 days - Manual interruptions, may need investigation
- **FAILED**: 90 days - Errors, important for troubleshooting patterns

## Safety Features

1. **Only deletes completed queues** - Never touches PENDING or INITIALIZING records
2. **Transaction safety** - All deletions happen in a single atomic transaction
3. **Dry-run mode** - Preview deletions before executing
4. **Status-specific retention** - Different retention periods for different statuses

## Automation Options

### Option 1: OpenShift CronJob (Recommended)

Create a CronJob to run the cleanup automatically:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: rlocker-cleanup-queues
  namespace: your-namespace
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            app: rlocker-cleanup
        spec:
          containers:
          - name: cleanup
            image: your-rlocker-image:latest
            command:
            - python
            - manage.py
            - cleanup_old_queues
            - --days=30
            - --verbose
            env:
            - name: DJANGO_SECRET
              valueFrom:
                secretKeyRef:
                  name: rlocker-secrets
                  key: django-secret
            - name: POSTGRESQL_DATABASE
              value: "rlocker"
            - name: POSTGRESQL_USER
              valueFrom:
                secretKeyRef:
                  name: postgresql-secret
                  key: username
            - name: POSTGRESQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgresql-secret
                  key: password
            - name: DATABASE_SERVICE_NAME
              value: "postgresql"
          restartPolicy: OnFailure
```

Deploy the CronJob:

```bash
oc apply -f cronjob-cleanup.yaml
```

Monitor CronJob execution:

```bash
# List all jobs
oc get cronjobs

# View job history
oc get jobs

# View logs from latest job
oc logs -l app=rlocker-cleanup --tail=100
```

### Option 2: Manual Cron on Server

If running on a traditional server, add to crontab:

```bash
# Edit crontab
crontab -e

# Add line (runs daily at 2 AM)
0 2 * * * cd /path/to/rlocker && /path/to/venv/bin/python manage.py cleanup_old_queues --days=30 >> /var/log/rlocker-cleanup.log 2>&1
```

### Option 3: Manual Execution

Run manually as needed:

```bash
# Activate virtual environment
source venv/bin/activate

# Run cleanup
python manage.py cleanup_old_queues --days=30
```

## Example Output

### Dry Run Mode

```
============================================================
  Queue Cleanup - DRY RUN MODE
============================================================

Status: FINISHED       Retention: 30 days  Count: 8234
Status: ABORTED        Retention: 60 days  Count: 456
Status: FAILED         Retention: 90 days  Count: 12

------------------------------------------------------------
Total records to process: 8702

Would delete 8702 record(s).
Run without --dry-run to actually delete.

============================================================
```

### Actual Deletion

```
============================================================
  Queue Cleanup - DELETION MODE
============================================================

Status: FINISHED       Retention: 30 days  Count: 8234
Status: ABORTED        Retention: 60 days  Count: 456
Status: FAILED         Retention: 90 days  Count: 12

------------------------------------------------------------
Total records to process: 8702

✓ Successfully deleted 8702 old queue record(s).

------------------------------------------------------------
Retention Policy Applied:
  • FINISHED: 30 days
  • ABORTED:  60 days
  • FAILED:   90 days

============================================================
```

## Monitoring

To check the current state of the queue table:

```sql
-- Count by status
SELECT status, COUNT(*)
FROM rqueue_rqueue
GROUP BY status
ORDER BY COUNT(*) DESC;

-- Count old records (30+ days)
SELECT status, COUNT(*)
FROM rqueue_rqueue
WHERE time_requested < NOW() - INTERVAL '30 days'
GROUP BY status;

-- Find oldest records
SELECT status, MIN(time_requested) as oldest, MAX(time_requested) as newest
FROM rqueue_rqueue
GROUP BY status;
```

## Troubleshooting

### Command not found

Ensure you're in the correct directory and virtual environment:

```bash
cd /path/to/rlocker
source venv/bin/activate
python manage.py cleanup_old_queues --help
```

### No records deleted

Check if records actually exist:

```sql
SELECT COUNT(*) FROM rqueue_rqueue
WHERE status IN ('FINISHED', 'ABORTED', 'FAILED')
AND time_requested < NOW() - INTERVAL '30 days';
```

### Database connection errors

Verify environment variables are set:

```bash
echo $DATABASE_SERVICE_NAME
echo $POSTGRESQL_DATABASE
```

## Best Practices

1. **Start with dry-run** - Always test with `--dry-run` first
2. **Monitor initial runs** - Watch the first few automated runs
3. **Adjust retention** - Tune retention periods based on your needs
4. **Schedule off-peak** - Run during low-traffic hours (2-4 AM)
5. **Keep logs** - Redirect output to log files for auditing
6. **Alert on failures** - Monitor CronJob failures in OpenShift

## Related Files

- Command implementation: `rqueue/management/commands/cleanup_old_queues.py`
- Model definition: `rqueue/models.py`
- Status constants: `rqueue/constants.py`
