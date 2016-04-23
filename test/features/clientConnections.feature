@SystemTest
Feature: Establish Connection Between the Server and the Client with Minimal Latency

  Background:
    Given: The "TX1" Server is online

  @wip
  Scenario: I should be able to establish a full connection with the server
    Given I have valid credentials to access the server
    When I attempt to retrieve the video stream from the server
    Then I should be able to see a video strema from the server
    And I should see no errors

  @wip
  Scenario: Invalid Credentials should disallow access to the server
    Given I have no valid credentials to access the server
    When I attempt to retrieve the video stream from the server
    Then I should recieve an error indicating I am unauthorized

  @wip
  Scenario: Latency from the server should be tolerable
    Given I have valid credentials to access the server
    And I am allowing a tolerance of 0 to 100ms for latency
    When I attempt to retrieve the video stream from the server
    And I keep track of the time taken to access each frame
    Then I should see each frame coming back within the specified tolerance
