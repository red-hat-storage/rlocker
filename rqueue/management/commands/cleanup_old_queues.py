"""
Django management command to clean up old completed queue records.

This command deletes old queue records that are in completed status
(FINISHED, ABORTED, FAILED) to prevent database bloat.

Usage:
    python manage.py cleanup_old_queues --days=30
    python manage.py cleanup_old_queues --days=30 --dry-run
    python manage.py cleanup_old_queues --finished-days=30 --aborted-days=60 --failed-days=90
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from rqueue.models import Rqueue
from rqueue.constants import Status


class Command(BaseCommand):
    help = "Delete old completed queue records to prevent database bloat"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Delete all completed records older than N days (default: 30)",
        )
        parser.add_argument(
            "--finished-days",
            type=int,
            default=30,
            help="Delete FINISHED records older than N days (default: 30)",
        )
        parser.add_argument(
            "--aborted-days",
            type=int,
            default=60,
            help="Delete ABORTED records older than N days (default: 60)",
        )
        parser.add_argument(
            "--failed-days",
            type=int,
            default=90,
            help="Delete FAILED records older than N days (default: 90)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed information about deletion",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verbose = options["verbose"]

        # If --days is specified, use it for all statuses
        if options["days"] is not None:
            finished_days = aborted_days = failed_days = options["days"]
        else:
            finished_days = options["finished_days"]
            aborted_days = options["aborted_days"]
            failed_days = options["failed_days"]

        # Calculate cutoff dates
        now = timezone.now()
        finished_cutoff = now - timedelta(days=finished_days)
        aborted_cutoff = now - timedelta(days=aborted_days)
        failed_cutoff = now - timedelta(days=failed_days)

        # Build querysets for each status
        deletion_plan = [
            {
                "status": Status.FINISHED,
                "cutoff": finished_cutoff,
                "days": finished_days,
                "queryset": Rqueue.objects.filter(
                    status=Status.FINISHED, time_requested__lt=finished_cutoff
                ),
            },
            {
                "status": Status.ABORTED,
                "cutoff": aborted_cutoff,
                "days": aborted_days,
                "queryset": Rqueue.objects.filter(
                    status=Status.ABORTED, time_requested__lt=aborted_cutoff
                ),
            },
            {
                "status": Status.FAILED,
                "cutoff": failed_cutoff,
                "days": failed_days,
                "queryset": Rqueue.objects.filter(
                    status=Status.FAILED, time_requested__lt=failed_cutoff
                ),
            },
        ]

        # Display header
        mode = "DRY RUN MODE" if dry_run else "DELETION MODE"
        self.stdout.write(self.style.WARNING(f"\n{'=' * 60}"))
        self.stdout.write(self.style.WARNING(f"  Queue Cleanup - {mode}"))
        self.stdout.write(self.style.WARNING(f"{'=' * 60}\n"))

        total_to_delete = 0
        total_deleted = 0

        # Process each status
        for plan in deletion_plan:
            status = plan["status"]
            cutoff = plan["cutoff"]
            days = plan["days"]
            queryset = plan["queryset"]
            count = queryset.count()
            total_to_delete += count

            if count > 0:
                self.stdout.write(
                    f"Status: {self.style.HTTP_INFO(status.ljust(15))} "
                    f"Retention: {days} days  "
                    f"Count: {self.style.WARNING(str(count))}"
                )

                if verbose and count > 0:
                    oldest = queryset.order_by("time_requested").first()
                    if oldest:
                        self.stdout.write(
                            f"  └─ Oldest record: {oldest.time_requested} (ID: {oldest.id})"
                        )

        # Perform deletion
        self.stdout.write(f"\n{'-' * 60}")
        self.stdout.write(
            f"Total records to process: {self.style.WARNING(str(total_to_delete))}\n"
        )

        if total_to_delete == 0:
            self.stdout.write(self.style.SUCCESS("✓ No old records found. Database is clean!"))
            return

        if dry_run:
            self.stdout.write(
                self.style.NOTICE(
                    f"Would delete {total_to_delete} record(s).\n"
                    f"Run without --dry-run to actually delete."
                )
            )
        else:
            # Confirm before deletion
            if total_to_delete > 1000:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠ Warning: About to delete {total_to_delete} records."
                    )
                )

            # Delete records in a transaction
            try:
                with transaction.atomic():
                    for plan in deletion_plan:
                        queryset = plan["queryset"]
                        if queryset.count() > 0:
                            deleted_count, _ = queryset.delete()
                            total_deleted += deleted_count

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Successfully deleted {total_deleted} old queue record(s)."
                    )
                )

                # Show retention summary
                self.stdout.write(f"\n{'-' * 60}")
                self.stdout.write("Retention Policy Applied:")
                self.stdout.write(f"  • FINISHED: {finished_days} days")
                self.stdout.write(f"  • ABORTED:  {aborted_days} days")
                self.stdout.write(f"  • FAILED:   {failed_days} days")

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error during deletion: {str(e)}")
                )
                raise

        self.stdout.write(f"\n{'=' * 60}\n")
