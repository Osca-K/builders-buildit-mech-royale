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

The current candidate starts from the original 4.23-point entry (b94d7c441285).
Obstacle-escape jumping and jetting now require intended horizontal travel.
The previous horizontal-progress timer treated deliberate arrival as blockage,
triggered a jump after0.8s of rest and then spent energy jetting upward.
Four regressions distinguish deliberate rest from real blocked travel, both
grounded and airborne. Run `python -m unittest test_stuck.py`.
Loot arrival, projectile avoidance, upgrades and combat retain the original baseline.
Upgrade selection tied at4.23; close-range mech target priority scored4.15;
cylinder aiming and arrival distance each scored3.85. All were reverted from
the release baseline, with their submitted commits preserved in history.
Only official practice matches measure performance; protocol conformance checks
cannot predict placement.
