## Script (Python) "folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##
from Products.CMFPlone import transaction_note
ids=context.REQUEST.get('ids', None)



status='failure'
message='Please select one or more items to delete.'

if ids:

    status='success'
    message=', '.join(ids)+' has been deleted.'
    transaction_note(message)        
    context.manage_delObjects(ids)


return context.portal_navigation.getNext(
                      context,
                      script.getId(),
                      status,
                      portal_status_message=message)
