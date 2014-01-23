# -*- coding: utf-8 -*-

from collective.behavior.peerreview import MessageFactory as _
from collective.behavior.peerreview.utils import context_property
from plone.app.widgets.dx import AjaxSelectWidget, SelectWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides, implements, Interface


class IReviewers(model.Schema):
    """Define reviewers field."""

    form.widget('reviewers', AjaxSelectWidget,
                vocabulary="plone.app.vocabularies.Users",
                pattern_options={'allowNewItems': True})
    form.read_permission(reviewers='cmf.ModifyPortalContent')
    form.write_permission(
        reviewers='collective.behavior.peerreview.ManageReviewers')
    reviewers = schema.Tuple(
        title=_(u'label_reviewers', u'Reviewers'),
        description=_(
            u'help_reviewers',
            default=u"Persons responsible for reviewing this document."
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )


class IReviewersMarker(Interface):
    """Marker interface."""


class IMasterReviewer(model.Schema):
    """Define reviewers field."""

    form.widget('master_reviewer', SelectWidget,
                vocabulary="plone.app.vocabularies.Users")
    form.read_permission(master_reviewer='cmf.ModifyPortalContent')
    form.write_permission(
        master_reviewer='collective.behavior.peerreview.ManageReviewers')
    master_reviewer = schema.Choice(
        title=_(u'label_master_reviewer', u'Master reviewer'),
        description=_(
            u'help_master_reviewer',
            default=u"Person responsible finishing review process."
        ),
        vocabulary="plone.app.vocabularies.Users",
        required=False,
    )


class IMasterReviewerMarker(IReviewersMarker):
    """Marker interface."""


alsoProvides(IReviewers, IFormFieldProvider)
alsoProvides(IMasterReviewer, IFormFieldProvider)


class Reviewers(object):
    """
    """

    implements(IReviewers)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    reviewers = context_property('reviewers')


class MasterReviewer(object):
    """
    """

    implements(IMasterReviewer)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    master_reviewer = context_property('master_reviewer')
