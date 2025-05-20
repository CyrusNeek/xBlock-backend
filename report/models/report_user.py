from django.db import models
from web.models import Brand


class ReportUserManager(models.Manager):
    def create_safe(
        self, email, phone, brand, first_name="Unknown", last_name="Unknown"
    ):
        if email or phone:
            user = (
                self.get_queryset()
                .filter(email=email, phone=phone, brand=brand)
                .first()
            )

            if user:
                user._fill_user_name(first_name, last_name)
                user.save()
                return user

            user_by_email = self.get_queryset().filter(email=email).first()
            user_by_phone = self.get_queryset().filter(phone=phone).first()

            if user_by_email and user_by_phone:
                if user_by_email != user_by_phone:
                    for reservation in user_by_phone.resyreservation_set.all():
                        reservation.user = user_by_email
                        reservation.save()
                    for order in user_by_phone.toastorder_set.all():
                        order.user = user_by_email
                        order.save()
                    for connection in user_by_phone.tockbooking_set.all():
                        connection.user = user_by_email
                        connection.save()

                    user_by_email._fill_user_name(first_name, last_name)
                    user_by_email.save()

                    user_by_phone.delete()
                    return user_by_email

            elif user_by_email:
                user_by_email._fill_user_name(first_name, last_name)
                if not user_by_email.phone or user_by_email.phone == "+-":
                    user_by_email.phone = phone
                user_by_email.save()
                return user_by_email

            elif user_by_phone:
                user_by_phone.email = email
                user_by_phone._fill_user_name(first_name, last_name)
                user_by_phone.save()
                return user_by_phone

        return self.create(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            brand=brand,
        )


class ReportUser(models.Model):
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.CASCADE)

    uploaded = models.BooleanField(default=False)

    objects = ReportUserManager()

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

    def _fill_user_name(self, first_name="Unknown", last_name="Unknown"):
        if "Unknown" in self.first_name and first_name != "Unknown":
            self.first_name = first_name

        if "Unknown" in self.last_name and last_name != "Unknown":
            self.last_name = last_name

    class Meta:
        unique_together = ["email", "phone", "brand"]
