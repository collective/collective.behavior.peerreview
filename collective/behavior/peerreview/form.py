from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.behavior.peerreview import MessageFactory as _
from collective.behavior.peerreview.subscribers import IReviewInProgress
from copy import deepcopy
from persistent.dict import PersistentDict
from plone.app.widgets.dx import TinyMCEWidget
from plone.autoform import directives as form
from plone.autoform.form import AutoExtensibleForm
from plone.supermodel import model
from z3c.form.button import buttonAndHandler
from z3c.form.form import Form
from zope import schema
from zope.annotation.interfaces import IAnnotations

SUBMIT_REVIEW_KEY = 'collective.behaviour.peerreview.forms.SubmitReview'


class ISubmitReview(model.Schema):

    form.mode(reviewer='hidden')
    reviewer = schema.TextLine(
        title=_(u'label_reviewer', u'Reviewer'),
        description=_(
            u'help_reviewer',
            default=u'TODO: write description'
        ),
        required=True,
    )

    form.widget('review', TinyMCEWidget)
    review = schema.Text(
        title=_(u'label_review', u'Review'),
        description=_(
            u'help_review',
            default=u"TODO: write description"
        ),
        required=True,
    )


class SubmitReview(AutoExtensibleForm, Form):

    template = ViewPageTemplateFile('templates/submit_review.pt')
    schema = ISubmitReview
    #ignoreContext = True

    def __init__(self, request, context):
        super(SubmitReview, self).__init__(request, context)
        self.annotations = IAnnotations(self.context)
        if not SUBMIT_REVIEW_KEY in self.annotations:
            self.annotations[SUBMIT_REVIEW_KEY] = PersistentDict()

    # TODO: add instance memoize
    def getContent(self):
        content = {}

        reviewer = self.request.get('form.widgets.reviewer', None)
        if reviewer:
            content['reviewer'] = reviewer

        annotation = self.annotations.get(SUBMIT_REVIEW_KEY, None)
        if annotation and reviewer in annotation:
            content.update(annotation[reviewer])

        return content

    def update(self):
        super(SubmitReview, self).update()
        reviewer = self.request.get('form.widgets.reviewer', None)
        self.is_reviewer = reviewer in self.context.reviewers
        self.is_review_in_progress = IReviewInProgress.providedBy(self.context)

    @buttonAndHandler(u'Submit')
    def handleSubmit(self, action):
        data, errors = self.extractData()

        if errors and not self.is_review_in_progress:
            return

        new_data = deepcopy(data)
        del new_data['reviewer']
        self.annotations[SUBMIT_REVIEW_KEY][data['reviewer']] = \
            PersistentDict(new_data)

        # TODO:
        # if master reviewer submitted his review then
        #   trigger exit transition
        # if last reviewer submited its review then
        #   if we have master reviewer
        #       notify him that he needs to submit his review 
        #   else
        #       trigger exit transition

        # TODO: add status message

        redirect = self.request.response.redirect
        redirect(self.context.absolute_url())

    @buttonAndHandler(u'Cancel')
    def handleCancel(self, action):

        # TODO: add status message

        redirect = self.request.response.redirect
        redirect(self.context.absolute_url())
