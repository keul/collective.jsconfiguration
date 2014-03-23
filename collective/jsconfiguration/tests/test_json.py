# -*- coding: utf-8 -*-

import unittest
from collective.jsconfiguration.interfaces import IJSConfigurationLayer
from collective.jsconfiguration.interfaces import IJSONDataProvider
from collective.jsconfiguration.testing import JS_CONFIGURATION_INTEGRATION_TESTING
from collective.jsconfiguration.tests.base import BaseTestCase
from zope.interface import implements
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component import provideAdapter
from zope.component import getGlobalSiteManager
from zope.publisher.interfaces.browser import IHTTPRequest
from Products.ATContentTypes.interfaces import IATDocument


class JSONConfiguration(object):
    implements(IJSONDataProvider)
    
    def __init__(self, context, request, view):
        self.name = u''
        self.context = context
        self.request = request
        self.view = view
        
    def __call__(self):
        return {'name' : self.name}


class SpecialJSONConfiguration(JSONConfiguration):

    def __call__(self):
        return {'name' : self.name.upper()}


class TestJSON(BaseTestCase):

    layer = JS_CONFIGURATION_INTEGRATION_TESTING

    def setUp(self):
        super(TestJSON, self).setUp()
        portal = self.layer['portal']
        portal.invokeFactory(type_name='Document', id='page', title="A Page",
                             text="<p>lorem ipsum</p>")
        provideAdapter(
                JSONConfiguration,
                (Interface,
                 IHTTPRequest,
                 Interface),
                provides=IJSONDataProvider,
                name=u'foo.json.data'
            )

    def tearDown(self):
        super(TestJSON, self).tearDown()
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(JSONConfiguration,
                              required=(Interface,
                                        IHTTPRequest,
                                        Interface),
                              name=u'foo.json.data')
        gsm.unregisterAdapter(SpecialJSONConfiguration,
                              required=(Interface,
                                        IHTTPRequest,
                                        Interface),
                              name=u'foo.json.data')
        gsm.unregisterAdapter(JSONConfiguration,
                              required=(Interface,
                                        IHTTPRequest,
                                        Interface),
                              name=u'bar.json.data')

    def test_configurtion_on_portal(self):
        portal = self.layer['portal']
        self.assertTrue("""<script type="text/collective.jsconfiguration.json">"""
                        """{"name": "foo.json.data"}</script>""" in portal())

    def test_configurtion_on_page(self):
        portal = self.layer['portal']
        self.assertTrue("""<script type="text/collective.jsconfiguration.json">"""
                        """{"name": "foo.json.data"}</script>""" in portal.page())

    def test_override(self):
        portal = self.layer['portal']
        provideAdapter(
                SpecialJSONConfiguration,
                (IATDocument,
                 IHTTPRequest,
                 Interface),
                provides=IJSONDataProvider,
                name=u'foo.json.data'
            )
        self.assertTrue("""<script type="text/collective.jsconfiguration.json">"""
                        """{"name": "foo.json.data"}</script>""" in portal())
        self.assertFalse("""<script type="text/collective.jsconfiguration.json">"""
                        """{"name": "foo.json.data"}</script>""" in portal.page())
        self.assertTrue("""<script type="text/collective.jsconfiguration.json">"""
                        """{"name": "FOO.JSON.DATA"}</script>""" in portal.page())

    def test_multiple_registration(self):
        portal = self.layer['portal']
        provideAdapter(
                JSONConfiguration,
                (IATDocument,
                 IHTTPRequest,
                 Interface),
                provides=IJSONDataProvider,
                name=u'bar.json.data'
            )
        self.assertTrue("""<script type="text/collective.jsconfiguration.json">"""
                        """{"name": "foo.json.data"}</script>""" in portal.page())
        self.assertTrue("""<script type="text/collective.jsconfiguration.json">"""
                        """{"name": "bar.json.data"}</script>""" in portal.page())
