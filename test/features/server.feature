Feature: Server Stability
  Verify that the server is resiliant and will close without a lingering
  port open. Additionaly verify that mars has been wired through properly

  @server
  Scenario: Server launches and waits for a connection
    When I launch the server
    Then I should see that port 1337 is receiving connections
    And I should see an indication that the server is waiting for a client
    
  @server
  Scenario: Server connects and accepts invalid config file
    When I launch the server
    And a client connects to the server
    And the client sends an invalid configuration file
    Then the client should recieve an indication that the connection was terminated
    And the server should terminate the connection to the client
    And I should see that port 1337 is receiving connections
    And I should see an indication that the server is waiting for a client
    
  @server @system
  Scenario: Server connects and accepts valid config file, launching mars
    When I launch the server
    And a client connects to the server
    And the client sends a valid configuration file
    Then the client should recieve an indication that the connection was established
    And the server should be sending information through ports:
      | 1338 |
      | 1339 |
