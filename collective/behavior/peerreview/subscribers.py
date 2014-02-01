from Products.CMFPlone.utils import getToolByName
from Products.Five.utilities.marker import mark
from Products.Five.utilities.marker import erase
from collective.behavior.peerreview.behaviors import IMasterReviewerMarker
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import Interface


class IReviewInProgress(Interface):
    """Marker interface for content in peer review process."""


def email_param(context, recipient):
    return {
        'context_url': context.absolute_url(),
        'context_title': context.Title(),
        'recipient_username': recipient.getUserName(),
        'recipient_fullname': recipient.getProperty('fullname'),
        'recipient_email': recipient.getProperty('email'),
        }


def notify_reviewers(context, event):
    registry = getUtility(IRegistry)
    emails_subject = registry.get(
        'collective.behavior.peerreview.emails.subject', {})
    emails_body = registry.get(
        'collective.behavior.peerreview.emails.body', {})

    workflow_tool = getToolByName(context, 'portal_workflow')
    enter = registry.get('collective.behavior.peerreview.enter', None)
    exit = registry.get('collective.behavior.peerreview.exit', None)

    workflow = workflow_tool.getWorkflowsFor(context)[0]
    workflow_id = workflow.getId()

    if enter is not None and \
       workflow_id in enter.keys() and \
       event.action == enter[workflow_id]:

        mark(context, IReviewInProgress)

        for reviewer in context.reviewers:
            context.manage_setLocalRoles(reviewer, ["Reader"])

            recipient = api.user.get(reviewer)
            recipient_email = None
            if recipient:
                recipient_email = recipient.getProperty('email')

            if recipient_email:
                subject = emails_subject.get(
                    'review_started_notify_reviewers', '')
                body = emails_body.get(
                    'review_started_notify_reviewers', '')
                api.portal.send_email(
                    recipient=recipient_email,
                    subject=subject.format(**email_param(context,
                                                         recipient)),
                    body=body.format(**email_param(context, recipient)),
                    )

    if exit is not None and \
       workflow_id in exit.keys() and \
       event.action == exit[workflow_id] and \
       IReviewInProgress.providedBy(context):

        erase(context, IReviewInProgress)

        for reviewer in context.reviewers:
            context.manage_delLocalRoles([reviewer])

        if IMasterReviewerMarker.providedBy(context):
            context.manage_delLocalRoles([context.master_reviewer])

        recipient = api.user.get(context.Creator())
        recipient_email = recipient.getProperty('email')
        if recipient_email:
            subject = emails_subject.get('review_ended_notify_owner', '')
            body = emails_body.get('review_ended_notify_owner', '')
            api.portal.send_email(
                recipient=recipient_email,
                subject=subject.format(**email_param(context, recipient)),
                body=body.format(**email_param(context, recipient)),
                )
