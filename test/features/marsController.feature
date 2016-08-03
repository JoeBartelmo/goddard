Feature: Mars Interactions
    Should be able to navigate through mars commands without Exceptions being raised
    Iff there is an exception it will be handled accoringly
    If I manipulate a configuration file, changes should be seen through mars.
    Data aquisition.

  @mars
  Scenario: Debug Functionality
    When I start the Mars Controller as a debug operator
    And I wait 5 seconds
    And I close the Mars Controller
    And I view the log
    Then I should see debug statements in the log

  @mars
  Scenario: When I launch Mars with queues, then Mars should receieve data through the queues
    When I start the Mars Controller as a client
    And I wait for the Mars Controller to initialize
    And I attempt to send "exit" to the Mars Controller
    Then I should see that the Mars Controller is Closed

