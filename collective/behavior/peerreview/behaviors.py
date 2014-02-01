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


class IPeerReviewers(model.Schema):
    """Define peer reviewers field."""

    form.widget('peer_reviewers', AjaxSelectWidget,
                vocabulary="plone.app.vocabularies.Users",
                pattern_options={'allowNewItems': True})
    form.read_permission(peer_reviewers='cmf.ModifyPortalContent')
    form.write_permission(
        peer_reviewers='collective.behavior.peerreview.ManageReviewers')
    peer_reviewers = schema.Tuple(
        title=_(u'label_peer_reviewers', u'Peer reviewers'),
        description=_(
            u'help_peer_reviewers',
            default=u"Persons responsible for reviewing this document."
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )


class IPeerReviewersMarker(Interface):
    """Marker interface."""


class ILeadReviewer(model.Schema):
    """Define reviewers field."""

    form.widget('lead_reviewer', SelectWidget,
                vocabulary="plone.app.vocabularies.Users")
    form.read_permission(lead_reviewer='cmf.ModifyPortalContent')
    form.write_permission(
        lead_reviewer='collective.behavior.peerreview.ManageReviewers')
    lead_reviewer = schema.Choice(
        title=_(u'label_lead_reviewer', u'Lead reviewer'),
        description=_(
            u'help_lead_reviewer',
            default=u"Person responsible finishing review process."
        ),
        vocabulary="plone.app.vocabularies.Users",
        required=False,
    )


class ILeadReviewerMarker(IPeerReviewersMarker):
    """Marker interface."""


alsoProvides(IPeerReviewers, IFormFieldProvider)
alsoProvides(ILeadReviewer, IFormFieldProvider)


class PeerReviewers(object):
    """
    """

    implements(IPeerReviewers)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    peer_reviewers = context_property('peer_reviewers')


class LeadReviewer(object):
    """
    """

    implements(ILeadReviewer)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    lead_reviewer = context_property('lead_reviewer')
