from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from collective.behavior.peerreview.form import SUBMIT_REVIEW_KEY
from collective.behavior.peerreview.subscribers import IReviewInProgress
from zope.annotation.interfaces import IAnnotations


class ReviewStatus(ViewletBase):

    index = ViewPageTemplateFile('templates/review_status.pt')

    def update(self):
        self.is_owner = False
        self.is_reviewer = False
        self.current_user = api.user.get_current().getUserName()
        if self.current_user == self.context.Creator():
            self.is_owner = True
        elif self.current_user in self.context.reviewers or \
                self.current_user == self.context.master_reviewer:
            self.is_reviewer = IReviewInProgress.providedBy(self.context)

        self.reviews = {}
        if self.is_reviewer or self.is_owner:
            annotations = IAnnotations(self.context)
            if SUBMIT_REVIEW_KEY in annotations:
                self.reviews = annotations[SUBMIT_REVIEW_KEY]

    def submit_review_url(self):
        return '{}/@@submit-review?form.widgets.reviewer={}'.format(
            self.context.absolute_url(), self.current_user)
