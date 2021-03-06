from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse

class UserProfile(models.Model):
    """
    A model representing the profile of each user.
    """
    # to associate each user with one UserProfile
    user = models.OneToOneField(User, related_name="profile")

    # Other fields here
    summary = models.TextField(blank=True)

    def __unicode__(self):
        return self.user.username

    def get_best_name(self):
        """
        Returns the best possible name for the user.
        - If both the first name and last name are defined, then it uses a concatenation of the two.
        - If only the first_name is defined, then it uses it.
        - If none are defined, then it uses the username.
        """
        if self.user.first_name and self.user.last_name:
            return self.user.get_full_name()
        elif self.user.first_name:
            return self.user.first_name
        else:
            return self.user.username
    
    def get_absolute_url(self):
        return reverse('account_user_profile_with_username', kwargs={'username': self.user.username})

def create_user_profile(sender, instance, created, **kwargs):
    """
    When a new user is created, a profile needs to be associated with
    that user. This method is used to do so by attaching it as a 
    listener to the post_save signal for the User model.
    """
    if created:
        UserProfile.objects.create(user=instance)

# Make sure that a new profile is created when a new user is
# created using the create_user_profile function.
post_save.connect(create_user_profile, sender=User)

