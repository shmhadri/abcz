from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


ROLE_PERMISSIONS = {
    "Payment Manager": {
        "phonics": {
            "view_paymentorder",
            "view_paymentwebhookevent",
            "view_paymentactivationreview",
            "view_adminauditlog",
            "run_payment_reconciliation",
        },
    },
    "Marketing Viewer": {
        "phonics": {"view_operations_dashboard"},
    },
    "Support Agent": {
        "auth": {"view_user"},
        "phonics": {
            "view_studentprofile",
            "view_usersubscription",
            "view_paymentorder",
        },
    },
    "Content Editor": {
        "phonics": {
            "view_externalgame", "add_externalgame", "change_externalgame",
            "view_cvcword", "add_cvcword", "change_cvcword",
            "view_cvcsentence", "add_cvcsentence", "change_cvcsentence",
            "view_cvcstory", "add_cvcstory", "change_cvcstory",
            "view_topgoalunit", "add_topgoalunit", "change_topgoalunit",
            "view_topgoalvocabulary", "add_topgoalvocabulary", "change_topgoalvocabulary",
            "view_topgoalsentence", "add_topgoalsentence", "change_topgoalsentence",
            "view_topgoalquiz", "add_topgoalquiz", "change_topgoalquiz",
        },
    },
    "Read-only Analyst": {
        "phonics": {"view_operations_dashboard"},
    },
}


PROTECTED_MODEL_MUTATION_PERMISSIONS = {
    f"{action}_{model_name}"
    for action in ("add", "change", "delete")
    for model_name in (
        "adminauditlog",
        "paymentactivationreview",
        "paymentorder",
        "paymentwebhookevent",
        "usersubscription",
    )
}


def _permissions_for(specification):
    permissions = []
    missing = []
    for app_label, codenames in specification.items():
        found = Permission.objects.filter(
            content_type__app_label=app_label,
            codename__in=codenames,
        )
        found_by_codename = {permission.codename: permission for permission in found}
        permissions.extend(found_by_codename.values())
        missing.extend(
            f"{app_label}.{codename}"
            for codename in sorted(codenames - found_by_codename.keys())
        )
    if missing:
        raise CommandError(
            "Missing permissions. Run migrations before setting up roles: "
            + ", ".join(missing)
        )
    return permissions


class Command(BaseCommand):
    help = "Create or synchronize least-privilege Django Admin role groups."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate permissions and show the planned role setup without writing.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        super_admin_permissions = list(
            Permission.objects.filter(content_type__app_label="phonics").exclude(
                codename__in=PROTECTED_MODEL_MUTATION_PERMISSIONS
            )
        )
        super_admin_permissions.extend(
            Permission.objects.filter(
                content_type__app_label="auth",
                codename__in={"view_user", "view_group"},
            )
        )
        roles = {
            "Super Admin": super_admin_permissions,
            **{
                role_name: _permissions_for(specification)
                for role_name, specification in ROLE_PERMISSIONS.items()
            },
        }

        for role_name, permissions in roles.items():
            if dry_run:
                self.stdout.write(
                    f"Would configure {role_name} with {len(permissions)} permission(s)."
                )
                continue
            group, _ = Group.objects.get_or_create(name=role_name)
            group.permissions.set(permissions)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Configured {role_name} with {len(permissions)} permission(s)."
                )
            )

        if dry_run:
            transaction.set_rollback(True)
