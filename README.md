# Aegis

Mech Royale bot using the official standard-library protocol wrapper.
Survival and safe-circle positioning drive movement. A static arena grid supplies
routes, local steering avoids walls and incoming bullets, and combat uses predictive
aim with actual-torso alignment. Low health favors disengagement and regeneration.

Build: `docker build -t aegis .`

Run the official `check/check.py` with `python -u bot.py`, then with the scorer's
Docker sandbox flags and map mount. The reference stream is not a simulation.
Local conformance passed 300/300 decisions within 50 ms; Linux sandbox and real
match quality require separate verification. No match-performance claim is made.

The aiming candidate restores the 4.23-point movement baseline and tests actual
firing rays against conservative target cylinders. Enemy dimensions scale with
their uncapped cube count using the live configuration. Charging lasers aim at
the present target while gun eligibility retains its separate intercept point.
Run `python -m unittest test_aim.py` for independent geometric regression checks.
