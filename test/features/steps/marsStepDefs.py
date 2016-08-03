from behave import *
import time

@when('I start the Mars Controller as a debug operator')
def step_impl(context):
    context.mars.startConnectionToMars(True)

@when('I start the Mars Controller as a client')
def step_impl(context):
    context.mars.startConnectionToMars()

@when('I close the Mars Controller')
def step_impl(context):
    context.mars.stopConnectionToMars()

@then('I should see debug statements in the log')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should see debug statements in the log')

@when('I attempt to send "{command}" to the Mars Controller')
def step_impl(context, command):
    context.mars.sendCommandToMars(command)

@then('I should see that the Mars Controller is Closed')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then I should see that the Mars Controller is Closed')

@then('I wait {seconds} seconds')
def iWaitForXSeconds(context, seconds):
    time.sleep(int(seconds))

@when('I wait for the Mars Controller to initialize')
def iWaitForXSeconds(context):
    time.sleep(5)
