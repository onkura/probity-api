
# Negative Case Walkthrough

## Scenario
An AI system issues a large refund incorrectly.

Logs show:
- API call succeeded
- User request existed

Logs do not show:
- why refund threshold was interpreted as met
- who the system attributed responsibility to

## Without Probity
Investigation cannot determine the decision environment.
Teams debate configuration vs model behavior.

## With Probity
The decision snapshot shows:
- referenced policy version
- perceived eligibility signal
- attributed actor

Investigation focuses on the true cause.
