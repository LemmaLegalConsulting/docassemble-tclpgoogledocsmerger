@end_to_end
Feature: Select commercial climate clauses and download a merged document

  # Seeded with ALDashboard's static fixture generator, then reviewed against the interview.
  Scenario: Complete the interview and reach its final document screen
    Given I start the interview at "search_and_download.yml"
    And the maximum seconds for each Step in this Scenario is 240
    And the user gets to "download filled" with this data:
      | var | value |
      | selected_vals['Practice Area']['Commercial'] | True |
    Then I should see the phrase "Download Your Completed Document"
