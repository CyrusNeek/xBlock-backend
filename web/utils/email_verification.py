from django.apps import apps

# Define a list of models that use the email field and is_email_verified field
EMAIL_MODELS = [
    'web.BrandOwner',
    'web.Unit',
    'web.User',
]

def get_model_instance_by_email(email):
    for model_name in EMAIL_MODELS:
        Model = apps.get_model(model_name)
        try:
            if model_name  == 'web.User':
                instance = Model.objects.filter(email=email).first() or Model.objects.filter(secondary_email=email).first()
            else:
                instance = Model.objects.get(email=email)
            return instance
        except Model.DoesNotExist:
            continue
    return None
