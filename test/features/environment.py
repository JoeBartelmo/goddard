from behave import *
from contextModules.marsContext import MarsTestbed

def before_tag(context, tag):
    print 'before tag'
    if tag.startswith("mars"):
        context.mars = MarsTestbed()

def after_tag(context, tag):
    if tag.startswith("mars"):
        context.mars.closeConnectionToMars(forceful = True)
    context.mars = None
