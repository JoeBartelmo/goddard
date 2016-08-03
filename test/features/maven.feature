Feature: Maven (streams) Interactions
    Should function as an independant bash application, and function as initially intended

  @maven
  Scenario: Default Usage
    Given I have 3 known physical cameras plugged in
    When I launch the maven script
    Then I should see RTSP streams open on the following ports:
      | 8554 |
      | 8555 |
      | 8556 |
    And I should see the following video files in my local directory:
      | test-FrontFacingCamera.mp4 |
      | test-LeftFacingCamera.mp4  |
      | test-RightFacingCamera.mp4 |

  @maven
  Scenario: Help menu
    When I launch the maven script with "--help" as my options
    Then I should see a message indicating usage of the program
    And I should see no RTSP streams

  @maven
  Scenario: No exception thrown when < 3 cameras initiated
    Given I have 2 known physical cameras plugged in
    When I launch the maven script
    Then I should see 2 RTSP stream initiated
    And I should see no errors

  @maven
  Scenario: Closing an open maven stream
    Given I have 3 known physical cameras plugged in
    When I launch the maven script
    And I wait 5 seconds
    And I launch the maven script with "--close" as my options
    Then I should see no RTSP streams
    And I should see no errors

  @maven
  Scenario: Compound options changes how maven launches the RTSP streams
    Given I have 3 known physical cameras plugged in
    When I launch the maven script with "-p 553 -w 1000 -h 1000 -b 1000 -f compound-test -fps 20" as my options
    Then I should see my options reflected in maven's log
    And I should see RTSP streams open on the following ports:
      | 553 |
      | 554 |
      | 555 |
    And I should see the following video files in my local directory:
      | compound-test-FrontFacingCamera.mp4 |
      | compound-test-LeftFacingCamera.mp4  |
      | compound-test-RightFacingCamera.mp4 |
