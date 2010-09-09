from django.db import models
import utils # relative import

class UserManager(models.Manager):

    def user_by_password(self, email, raw_password):
        """
        Returns a User object for the given e-mail and raw password. If the
        e-mail address exists but the password is incorrect, returns None.
        """
        try:
            user = self.get(email=email)
        except self.model.DoesNotExist:
            return None
        if user.check_password(raw_password):
            return user
        return None

class User(models.Model):
    email = models.EmailField(unique=True) # Stored in all-lowercase.

    # Password uses '[algo]$[salt]$[hexdigest]', just like Django's auth.User.
    password = models.CharField(max_length=128)

    # The SHORT_NAME for the user's metro when they created the account.
    main_metro = models.CharField(max_length=32)

    creation_date = models.DateTimeField()
    is_active = models.BooleanField()

    objects = UserManager()

    def __unicode__(self):
        return self.email

    def set_password(self, new_password):
        self.password = utils.make_password_hash(new_password)

    def check_password(self, raw_password):
        "Returns True if the given raw password is correct for this user."
        return utils.check_password_hash(raw_password, self.password)

# Note that this class does *not* use the multidb Manager.
# It's city-specific because pending user actions are city-specific.

class PendingUserAction(models.Model):
    email = models.EmailField(db_index=True) # Stored in all-lowercase.
    callback = models.CharField(max_length=50)
    data = models.TextField() # Serialized into JSON.
    action_date = models.DateTimeField() # When the action was created (so we can clear out expired ones).

    def __unicode__(self):
        return u'%s for %s' % (self.callback, self.email)
