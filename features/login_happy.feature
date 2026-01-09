Feature: LLM generated login flows
  As a user of the sample web app
  I want to login and access the dashboard
  So that I can use the application features

  Scenario: Successful Login with Valid Credentials
      Given I am on the login page
      When I enter "validUser" into the "Username" field
      And I enter "validPassword123" into the "Password" field
      And I click the "Login" button
      Then I should be redirected to the "Dashboard" page
      And I should see a welcome message "Welcome, validUser!"

  Scenario: Unsuccessful Login with Invalid Password
      Given I am on the login page
      When I enter "existingUser" into the "Username" field
      And I enter "wrongPassword" into the "Password" field
      And I click the "Login" button
      Then I should remain on the "Login" page
      And I should see an error message "Invalid username or password."

  Scenario: Unsuccessful Login with Non-Existent User
      Given I am on the login page
      When I enter "nonExistentUser" into the "Username" field
      And I enter "anyPassword123" into the "Password" field
      And I click the "Login" button
      Then I should remain on the "Login" page
      And I should see an error message "Invalid username or password."

