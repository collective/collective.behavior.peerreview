from Products.CMFPlone.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from collective.behavior.peerreview import MessageFactory as _
from collective.behavior.peerreview.behaviors import IMasterReviewerMarker
from collective.behavior.peerreview.subscribers import IReviewInProgress
from collective.behavior.peerreview.subscribers import email_param
from copy import deepcopy
from persistent.dict import PersistentDict
from plone import api
from plone.app.widgets.dx import TinyMCEWidget
from plone.autoform import directives as form
from plone.autoform.form import AutoExtensibleForm
from plone.memoize import instance
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

SUBMIT_REVIEW_KEY = 'collective.behaviour.peerreview.forms.SubmitReview'


class ISubmitReview(model.Schema):

    form.widget('review', TinyMCEWidget)
    review = schema.Text(
        title=_(u'label_review', u'Review'),
        description=_(
            u'help_review',
            default=u"Write freeform review of the document."
        ),
        required=True,
    )


class SubmitReview(AutoExtensibleForm, Form):

    template = ViewPageTemplateFile('templates/submit_review.pt')
    schema = ISubmitReview

    def __init__(self, request, context):
        super(SubmitReview, self).__init__(request, context)
        self.annotations = IAnnotations(self.context)
        if not SUBMIT_REVIEW_KEY in self.annotations:
            self.annotations[SUBMIT_REVIEW_KEY] = PersistentDict()

    @instance.memoize
    def getContent(self):
        content = {}

        reviewer = api.get_current()
        # import pdb; pdb.set_trace()
        annotation = self.annotations.get(SUBMIT_REVIEW_KEY, None)
        if annotation and reviewer in annotation:
            content.update(annotation[reviewer])

        return content

    def update(self):
        super(SubmitReview, self).update()
        reviewer = self.request.get('form.widgets.reviewer', None)
        if IMasterReviewerMarker.providedBy(self.context):
            self.is_reviewer = reviewer in self.context.reviewers or\
                reviewer == self.context.master_reviewer
        else:
            self.is_reviewer = reviewer in self.context.reviewers
        self.is_review_in_progress = IReviewInProgress.providedBy(self.context)

    @buttonAndHandler(u'Submit')
    def handleSubmit(self, action):
        data, errors = self.extractData()

        if errors and not self.is_review_in_progress:
            return

        registry = getUtility(IRegistry)

        new_data = deepcopy(data)
        del new_data['reviewer']
        self.annotations[SUBMIT_REVIEW_KEY][data['reviewer']] = \
            PersistentDict(new_data)

        emails_subject = registry.get(
            'collective.behavior.peerreview.emails.subject', {})
        emails_body = registry.get(
            'collective.behavior.peerreview.emails.body', {})
        exit = registry.get('collective.behavior.peerreview.exit', None)

        workflow_tool = getToolByName(self.context, 'portal_workflow')
        workflow = workflow_tool.getWorkflowsFor(self.context)[0]
        workflow_id = workflow.getId()

        if IMasterReviewerMarker.providedBy(self.context) and \
           self.context.master_reviewer == data['reviewer']:
            with api.env.adopt_roles(['Manager']):
                api.content.transition(self.context, exit[workflow_id])

        elif len(self.annotations[SUBMIT_REVIEW_KEY]) ==\
                len(self.context.reviewers):

            if IMasterReviewerMarker.providedBy(self.context):
                self.context.manage_setLocalRoles(
                    self.context.master_reviewer, ["Reader"])

                recipient = api.user.get(self.context.master_reviewer)
                recipient_email = recipient.getProperty('email')
                if recipient_email:
                    subject = emails_subject.get(
                        'review_started_notify_reviewers', '')
                    body = emails_body.get(
                        'review_started_notify_reviewers', '')
                    api.portal.send_email(
                        recipient=recipient_email,
                        subject=subject.format(
                            **email_param(self.context, recipient)),
                        body=body.format(
                            **email_param(self.context, recipient)),
                        )
            else:
                with api.env.adopt_roles(['Manager']):
                    api.content.transition(self.context, exit[workflow_id])

        messages = IStatusMessage(self.request)
        messages.add(_(u"Review submitted."), type=u"info")

        redirect = self.request.response.redirect
        redirect(self.context.absolute_url())

    @buttonAndHandler(u'Cancel')
    def handleCancel(self, action):

        messages = IStatusMessage(self.request)
        messages.add(_(u"Review submission canceled"), type=u"info")

        redirect = self.request.response.redirect
        redirect(self.context.absolute_url())
