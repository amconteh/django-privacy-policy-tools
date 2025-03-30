
# Copyright (c) 2022-2023 Josef Wachtler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This module provides some middleware for the package privacy_policy_tools.
"""
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from privacy_policy_tools.utils import get_setting, get_active_policies, get_by_py_path
from privacy_policy_tools.models import PrivacyPolicyConfirmation

class PrivacyPolicyMiddleware:
    """
    This middleware class forces the user to confirm the privacy policies.
    """

    def __init__(self, get_response):
        """
        Constructor: sets get_response
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Processes the request and redirects to the privacy policy if
        the user has not confirmed the latest version yet.

        Keyword arguments:
            - request -- calling HttpRequest
        """
        response = self.get_response(request)
        enabled = get_setting('ENABLED')
        if not enabled:
            return response

        url = get_setting('POLICY_PAGE_URL', 'terms/and/conditions')
        ignore_urls = get_setting('IGNORE_URLS', [])

        if not request.user.is_authenticated or \
        url in request.path_info or \
        any(ignore in request.path_info for ignore in ignore_urls):
            return response

        start_hook = get_setting('START_HOOK')
        if start_hook:
            start_hook = get_by_py_path(start_hook)
            if start_hook(request) is False:
                return response

        policies = get_active_policies()
        if not policies:
            return response

        for policy in policies:
            if self._policy_applies_to_user(request.user, policy):
                # Check for confirmation with matching version
                confirmation = PrivacyPolicyConfirmation.objects.filter(
                    privacy_policy__id=policy.id,
                    privacy_policy__version=policy.version,  # Added version check
                    user=request.user
                ).first()

                if not confirmation:
                    next_view = self._generate_next(request)
                    return HttpResponseRedirect(reverse(
                        'privacy_policy_tools.views.confirm',
                        args=(policy.id, next_view,)
                    ))
                else:
                    second_confirmation = self._second_confirmation(request, confirmation)
                    if second_confirmation:
                        return second_confirmation

        return response

    def _policy_applies_to_user(self, user, policy):
        """
        Determines if a policy applies to a user based on group membership.
        """
        default_policy = get_setting('DEFAULT_POLICY', True)
        if default_policy:
            return policy.for_group is None or policy.for_group in user.groups.all()
        else:
            return (policy.for_group is None and not user.groups.exists()) or \
                   policy.for_group in user.groups.all()

    def _second_confirmation(self, request, confirmation):
        """
        Checks if a second confirmation is required and returns a redirect if so.
        """
        required_hook = get_setting('SECOND_CONFIRMATION_REQUIRED_HOOK')
        if not required_hook:
            return None

        required_hook = get_by_py_path(required_hook)
        if required_hook(request, confirmation) is False:
            return None

        if confirmation.second_confirmed_at is not None:
            return None

        return HttpResponseRedirect(reverse(
            'privacy_policy_tools.views.second_confirm_required',
            args=(confirmation.id,)
        ))

    def _generate_next(self, request):
        """
        Generates the 'next' URL for redirecting after policy confirmation.
        """
        return request.path_info
