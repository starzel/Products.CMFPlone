from Products.CMFCore.utils import _verifyActionPermissions, \
     getToolByName, getActionContext
from Products.CMFCore.Skinnable import SkinnableObjectManager
from OFS.Folder import Folder
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.CMFCorePermissions import View, ManageProperties, \
     ListFolderContents
from Products.CMFCore.CMFCorePermissions import AddPortalFolders, \
     AddPortalContent
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.interfaces.DublinCore import DublinCore as IDublinCore
from Products.CMFCore.interfaces.Contentish import Contentish as IContentish
from AccessControl import Permissions, getSecurityManager, \
     ClassSecurityInfo, Unauthorized
from Products.CMFCore import CMFCorePermissions
from Acquisition import aq_base, aq_inner, aq_parent
from Globals import InitializeClass
from webdav.WriteLockInterface import WriteLockInterface

from OFS.ObjectManager import REPLACEABLE
from ComputedAttribute import ComputedAttribute

from PloneUtilities import log

class ReplaceableWrapper:
    """ A wrapper around an object to make it replaceable """
    def __init__(self, ob):
        self.__ob = ob

    def __getattr__(self, name):
        if name == '__replaceable__':
            return REPLACEABLE
        return getattr(self.__ob, name)

factory_type_information = { 'id'             : 'Folder'
                             , 'meta_type'      : 'Plone Folder'
                             , 'description'    : """\
Plone folders can define custom 'view' actions, or will behave like directory listings without one defined."""
                             , 'icon'           : 'folder_icon.gif'
                             , 'product'        : 'CMFPlone'
                             , 'factory'        : 'addPloneFolder'
                             , 'filter_content_types' : 0
                             , 'immediate_view' : 'folder_listing'
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'string:${folder_url}/folder_listing'
                                  , 'permissions'   :
                                     (CMFCorePermissions.View,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'local_roles'
                                  , 'name'          : 'Local Roles'
                                  , 'action'        : 'string:${folder_url}/folder_localrole_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ChangePermissions,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'string:${folder_url}/folder_edit_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                )
                             }

class PloneFolder ( SkinnedFolder, DefaultDublinCoreImpl ):
    meta_type = 'Plone Folder'

    security=ClassSecurityInfo()

    __implements__ = (SkinnedFolder.__implements__ ,
                      DefaultDublinCoreImpl.__implements__ ,
                      WriteLockInterface)

    manage_options = Folder.manage_options + \
                     CMFCatalogAware.manage_options
    # fix permissions set by CopySupport.py
    __ac_permissions__=(
        ('Modify portal content',
         ('manage_cutObjects', 'manage_copyObjects', 'manage_pasteObjects',
          'manage_renameForm', 'manage_renameObject', 'manage_renameObjects',)),
        )

    def __init__(self, id, title=''):
        DefaultDublinCoreImpl.__init__(self)
        self.id=id
        self.title=title

    def __call__(self):
        """ Invokes the default view. """
        view = _getViewFor(self, 'view', 'folderlisting')
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, self.REQUEST))
        else:
             return view()

    def index_html(self):
        """ Acquire if not present. """
        _target = aq_parent(aq_inner(self)).aq_acquire('index_html')
        return ReplaceableWrapper(aq_base(_target).__of__(self))

    index_html = ComputedAttribute(index_html, 1)

    security.declareProtected(AddPortalFolders, 'manage_addPloneFolder')
    def manage_addPloneFolder(self, id, title='', REQUEST=None):
        """ adds a new PloneFolder """
        ob=PloneFolder(id, title)
    	self._setObject(id, ob)
    	if REQUEST is not None:
            return self.folder_contents(self, REQUEST, portal_status_message='Folder added') #XXX HARDCODED FIXME!

    manage_addFolder = manage_addPloneFolder

    def __browser_default__(self, request):
        """ Set default so we can return whatever we want instead of index_html """
        return self.browserDefault(request)

    security.declareProtected( ListFolderContents, 'listFolderContents')
    def listFolderContents( self, spec=None, contentFilter=None, suppressHiddenFiles=0 ):
        """
        Hook around 'contentValues' to let 'folder_contents'
        be protected.  Duplicating skip_unauthorized behavior of dtml-in.

        In the world of Plone we do not want to show objects that begin with a .
        So we have added a simply check.  We probably dont want to raise an
        Exception as much as we want to not show it.

        """

        items = self.contentValues(spec=spec, filter=contentFilter)
        l = []
        for obj in items:
            id = obj.getId()
            v = obj
            try:
                if suppressHiddenFiles and id[:1]=='.':
                    raise Unauthorized(id, v)
                if getSecurityManager().validate(self, self, id, v):
                    l.append(obj)
            except (Unauthorized, 'Unauthorized'):
                pass
        return l
InitializeClass(PloneFolder)

manage_addPloneFolder=PloneFolder.manage_addPloneFolder
def addPloneFolder( self, id, title='', description='', REQUEST=None ):
    """ adds a Plone Folder """
    sf = PloneFolder(id, title=title)
    sf.description=description
    self._setObject(id, sf)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

#--- Helper function that can figure out what 'view' action to return
def _getViewFor(obj, view='view', default=None):
    ti = obj.getTypeInfo()
    context = getActionContext(obj)

    if ti is not None:
        actions = ti.listActions()
        for action in actions:
            _action = action.getAction(context)
            if _action.get('id', None) == default:
                default=action
            if _action.get('id', None) == view:
                if _verifyActionPermissions(obj, action) and _action['url']!='':
                    computed_action = obj.restrictedTraverse(_action['url'])
                    if computed_action is not None:
                        return computed_action

        if default is not None:
            _action = default.getAction(context)
            if _verifyActionPermissions(obj, default):
                return obj.restrictedTraverse(_action['url'])

        # "view" action is not present or not allowed.
        # Find something that's allowed.
        #for action in actions:
        #    if _verifyActionPermissions(obj, action)  and action.get('action','')!='':
        #        return obj.restrictedTraverse(action['action'])
        raise 'Unauthorized', ('No accessible views available for %s' %
                               '/'.join(obj.getPhysicalPath()))
    else:
        raise 'Not Found', ('Cannot find default view for "%s"' %
                            '/'.join(obj.getPhysicalPath()))

