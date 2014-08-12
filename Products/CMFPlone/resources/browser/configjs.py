from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IBundleRegistry, IResourceRegistry, IJSManualResource
from zope.component import getMultiAdapter
from zope.component import getUtility

from urlparse import urlparse
import re


configjs = """requirejs.config({
    baseUrl: '%s',
    paths: %s,
    shim: %s,
    optimize: 'uglify',
    wrapShim: true
});

"""


class RequireJsView(BrowserView):
<<<<<<< HEAD

    @property
    def registry(self):
        return getUtility(IRegistry)    

    def registryResources(self):
        return self.registry.collectionOfInterface(IResourceRegistry, prefix="Products.CMFPlone.resources")
=======
    def registry(self):
        registryUtility = getUtility(IRegistry)
        return registryUtility.collectionOfInterface(IResourceRegistry, prefix="Products.CMFPlone.resources")
>>>>>>> 7695eaa99df0500e1cb585c2526aab5fd7b6c15b

    def base_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                name=u'plone_portal_state')
        site_url = portal_state.portal_url()
        return site_url

<<<<<<< HEAD
    def get_requirejs_config(self):
        """
        Returns the information for requirejs configuration
        """
        registry = self.registryResources()
=======



class ConfigJsView(RequireJsView):
    """ config.js for requirejs for script rendering. """

    def get_config(self):
        registry = self.registry()
>>>>>>> 7695eaa99df0500e1cb585c2526aab5fd7b6c15b

        paths = {}
        shims = {}
        mains = []
        norequire = []
        for requirejs, script in registry.items():
            if script.js:
                src = re.sub(r"\.js$", "", script.js)
                paths[requirejs] = src
                exports = script.export
                deps = script.deps
                inits = script.init
                if exports != '' or deps != '' or inits != '':
                    shims[requirejs] = {}
                    if exports != '' and exports is not None:
                        shims[requirejs]['exports'] = exports
                    if deps != '' and deps is not None:
                        shims[requirejs]['deps'] = deps.split(',')
                    if inits != '' and inits is not None:
                        shims[requirejs]['init'] = inits

        shims_str = str(shims).replace('\'deps\'', 'deps').replace('\'exports\'', 'exports').replace('\'init\': \'', 'init: ').replace('}\'}', '}}')
        return (self.base_url(), str(paths), shims_str)

<<<<<<< HEAD
class ConfigJsView(RequireJsView):
    """ config.js for requirejs for script rendering. """

    def __call__(self):
        (baseUrl, paths, shims) = self.get_requirejs_config()
=======
    def __call__(self):
        (baseUrl, paths, shims) = self.get_config()
>>>>>>> 7695eaa99df0500e1cb585c2526aab5fd7b6c15b
        self.request.response.setHeader("Content-Type", "application/javascript")
        return configjs % (baseUrl, paths, shims)


bbbplone = """require([
<<<<<<< HEAD
  'jquery'  
], function($) {
=======
  'jquery',
  'plone'
], function($, Plone) {
>>>>>>> 7695eaa99df0500e1cb585c2526aab5fd7b6c15b
  'use strict';

  require(%s, function(undefined){
    // initialize only if we are in top frame
    if (window.parent === window) {
      $(document).ready(function() {
        $('body').addClass('pat-bbbplone');
      });
    }
  })
});"""


class BBBConfigJsView(RequireJsView):
    """ bbbplone.js for non-requirejs code """

    def get_bbb_scripts(self):
<<<<<<< HEAD
        return self.registry.collectionOfInterface(IJSManualResource, prefix="Products.CMFPlone.manualjs")

    def get_bbb_order(self):
        return self.registry.collectionOfInterface(IJSManualResource, prefix="Products.CMFPlone.jslist")
=======
        registryUtility = getUtility(IRegistry)
        return registryUtility.collectionOfInterface(IJSManualResource, prefix="Products.CMFPlone.manualjs")

    def get_bbb_order(self):
        registryUtility = getUtility(IRegistry)
        return registryUtility.collectionOfInterface(IJSManualResource, prefix="Products.CMFPlone.jslist")
>>>>>>> 7695eaa99df0500e1cb585c2526aab5fd7b6c15b

    def get_data(self, script):
        """
        Get the src for the script and check expression
        """
        src = None
        if script.enabled:
            if script.expression:
                    if script.cooked_expression:
                        expr = Expression(script.expression)
                        script.cooked_expression = expr
                    if self.evaluateExpression(script.cooked_expression, context):
                        return src
            url = urlparse(script.url)
            if url.netloc == '':
                # Local
                src = "%s/%s" % (self.base_url(), script.url)
            else:
                src = "%s" % (script.url)
        return src

    def get_config(self):
        norequire = []
<<<<<<< HEAD
        # Load the ordered list of js
        list_of_js = self.registry.records['Products.CMFPlone.jslist']
=======
        registryUtility = getUtility(IRegistry)
        # Load the ordered list of js
        list_of_js = registryUtility.records['Products.CMFPlone.jslist']
>>>>>>> 7695eaa99df0500e1cb585c2526aab5fd7b6c15b
        scripts = self.get_bbb_scripts()
        loaded = []
        for script_id in list_of_js.value:
            if script_id in scripts:
                loaded.append(script_id)
                src = self.get_data(scripts[script_id])
                if src:
                    norequire.append(src)

        # The rest of scripts
        for key, script in scripts.items():
            if key not in loaded:
                src = self.get_data(script)
                if src:
                    norequire.append(src)
        return norequire

    def __call__(self):
        norequire = self.get_config()
        self.request.response.setHeader("Content-Type", "application/javascript")
        return bbbplone % (norequire)


<<<<<<< HEAD

=======
optimize = """requirejs.optimize({
    baseUrl: '%s',
    paths: %s,
    shims: %s,
    optimize: "none",
    include: %s,
    out: function (text) {
        document.getElementById('output').value = text;
    }
}, function (buildText) {
    document.getElementById('buildMessages').value = buildText;
});
"""


class OptimizeJS(ConfigJsView):

    def get_bundles(self):
        bundles = self.registry.collectionOfInterface(IBundleRegistry, prefix="Products.CMFPlone.bundles")
        mains = []
        for key, bundle in bundles.items():
            mains.append(key)
        return mains


    def optimize(self):
        (baseUrl, paths, shims) = self.get_config()
        mains = self.get_bundles()
        return optimize % (baseUrl, paths, shims, mains)


class SaveOpimalJS(BrowserView):

    def __call__(self):
        # We need to check auth, valid js
        # TODO
        if self.request.get('text', None):
            # Save the file on the resource directory .. registry ...
            pass
>>>>>>> 7695eaa99df0500e1cb585c2526aab5fd7b6c15b
