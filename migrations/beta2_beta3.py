from Products.CMFPlone import MigrationTool
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore import CMFCorePermissions

def twothree(portal):
    """ Upgrade from Plone 1.0 Beta 2 to Beta 3 """
    typesTool = portal.portal_types
    # lines 78
    # register Btree folder if aint there
    try:
        typesTool.manage_addTypeInformation('Factory-based Type Information',
                                            'BTree Folder', 
                                            'BTreeFolder2: CMF BTree Folder')
    # ugh, this is bad                                            
    except:
        pass
    
    # line 148
    # portal workflow change
    wf_tool=portal.portal_workflow
    folder_wf = wf_tool['folder_workflow']
    folder_wf.states.visible.permission_roles[CMFCorePermissions.ListFolderContents]=['Manager', 'Owner']

    # line 223
    # some additions to validators
    form_tool = portal.portal_form
    form_tool.setValidators('folder_rename_form', ['validate_folder_rename'])
    form_tool.setValidators('sendto_form', ['validate_sendto'])

    # line 251
    # add columns to the calatog 
    catalog = portal.portal_catalog
    if not catalog._catalog.schema.has_key('getId'):
        catalog.addColumn('getId', None)
    if not catalog._catalog.schema.has_key('meta_type'):
        catalog.addColumn('meta_type', None)

    # line 195
    # add in site properties sheet
    prop_tool = portal.portal_properties
    if 'site_properties' not in prop_tool.objectIds():
        prop_tool.manage_addPropertySheet('site_properties', 'Site Properties')

    p = prop_tool.site_properties
    
    # line 195
    # add in auth cookie length
    _ids = p.propertyIds()
    if 'auth_cookie_length' not in _ids:
        p._setProperty('auth_cookie_length', 0, 'int')
    # line 110
    if 'allow_sendto' not in _ids:
        p._setProperty('allow_sendto', 0, 'boolean')
    if 'enable_navigation_logging' not in _ids:
        p._setProperty('enable_navigation_logging', 0, 'int')
    # /adding

    #moving properties from CMF Site object to portal_properties/site_properties
    policy=DefaultCustomizationPolicy()
    policy.addSiteProperties(portal)

    #adding navigation properties
    nav_tool=portal.portal_navigation
    nav_tool.addTransitionFor('default', 'createObject', 'success', 'action:edit')
    nav_tool.addTransitionFor('default', 'sendto_form', 'success', 'script:sendto')
    nav_tool.addTransitionFor('default', 'sendto_form', 'failure', 'sendto_form')
    nav_tool.addTransitionFor('default', 'sendto', 'success', 'action:view')
    nav_tool.addTransitionFor('default', 'sendto', 'failure', 'action:view')

def registerMigrations():
    # so the basic concepts is you put a bunch of migrations is here
    MigrationTool.registerUpgradePath(
            '1.0beta2', 
            '1.0beta3', 
            twothree
            )
    # it will run through them all until its upto date
    # etc
    # MigrationTool.registerUpgradePath('1.0beta3', '1.0beta4', beta3two4)

if __name__=='__main__':
    registerMigrations()

