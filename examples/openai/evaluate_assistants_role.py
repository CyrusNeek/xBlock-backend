
from report.tasks.periodic.update_assistant_vector_files import *
from roles.models import *




def main():
    roles = Role.objects.all()

    for role in roles:
        evaluate_role_update(role.pk)



if __name__ == "django.core.management.commands.shell":
    main()










