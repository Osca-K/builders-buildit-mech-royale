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

The current candidate starts from the 4.25-point entry (f11c16c9496a), whose
projectile avoidance models acceleration, air control, movement speed and mortar
gravity. Target selection now checks torso pitch limits: an unreachable close
target must not prevent firing at a valid farther one. If part of a tall body
is reachable, it aims there; nearby lightning retains yaw-only targeting.
Eleven regression tests cover motion and targeting boundary cases.
Run `python -m unittest test_motion.py test_targeting.py`.
Loot arrival, upgrade priorities and movement goals retain the original policy.
Upgrade selection tied at4.23; close-range mech target priority scored4.15;
cylinder aiming and arrival distance each scored3.85. All were reverted from
the release baseline, with their submitted commits preserved in history.
Only official practice matches measure performance; protocol conformance checks
cannot predict placement.
