""" Token generators module"""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """ Email confirmation token """

    def _make_hash_value(self, user, timestamp):
        """
        Make hash for token
        :param user: user object
        :param timestamp: timestamp
        :return: hash
        """
        return six.text_type(user.pk) + six.text_type(timestamp)


account_activation_token = AccountActivationTokenGenerator()
