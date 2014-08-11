import zope.interface
import zope.component
from zope import schema

from Products.CMFPlone import PloneMessageFactory as _

class IResourceRegistry(zope.interface.Interface):

    url = schema.ASCIILine(
        title=_(u"Resources base URL"),
        required=False)

    js = schema.ASCIILine(
        title=_(u"Main js file"),
        required=False)

    css = schema.List(
        title=_(u"CSS/LESS files"),
        value_type=schema.ASCIILine(title=_(u"URL")),
        default=[],
        required=False)

    css_deps = schema.ASCIILine(
        title=_(u"CSS dependencies"),
        description=_(u"Coma separated values of resources to load their CSS before this one"),
        required=False)

    init = schema.ASCIILine(
        title=_(u"Init instruction for shim"),
        required=False)

    deps = schema.ASCIILine(
        title=_(u"Dependencies for shim"),
        description=_(u"Coma separated values of resource for shim"),
        required=False)

    export = schema.ASCIILine(
        title=_(u"Export vars for shim"),
        required=False)

    conf = schema.Text(
        title=_(u"Configuration in JSON for the widget"),
        description=_(u"Should be accessible on @@getWCconfig?id=name"),
        required=False)

    force = schema.Bool(
        title=_(u"Force to load it at the end without a bundle"),
        description=_(u"This if intended to be used with legacy js"),
        required=False)


class IBundleRegistry(zope.interface.Interface):

    jscompilation = schema.ASCIILine(
        title=_(u"URL of the last js compilation"),
        required=False)

    csscompilation = schema.ASCIILine(
        title=_(u"URL of the last css compilation"),
        required=False)

    last_compilation = schema.Datetime(
        title=_(u"Last compiled date"),
        description=_(u"Date time of the last compilation of this bundle"),
        required=False)

    expression = schema.ASCIILine(
        title=_(u"Expression to render"),
        description=_(u"In case its a bundle we can have a condition to render it"),
        required=False)

    cooked_expression = schema.ASCIILine(
        title=_(u"Coocked expression to render"),
        description=_(u"Filled automatic"),
        required=False)

    conditionalcomment = schema.ASCIILine(
        title=_(u"Conditional comment"),
        description=_(u"In case you want to render this resource on conditional comment"),
        required=False)

    resource = schema.ASCIILine(
        title=_(u"Main resource"),
        description=_(u"The resource that is going to be loaded on this bundle"),
        required=False)

    enabled = schema.Bool(
        title=_(u"It's enabled?"),
        default=True,
        required=False)

    depends = schema.ASCIILine(
        title=_(u"Depends on another bundle"),
        description=_(u"In case you want to be the last: *, in case its the first should be empty"),
        required=False)