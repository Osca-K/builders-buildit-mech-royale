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

This candidate starts from the4.25-point entry(f11c16c9496a). Ground routes now
use the live mech radius and height after cube growth. The original fixed9m
mask routed a10-cube/13.5m mech through a real underpass it could not enter.
Additional body checks are cached on demand, with four dimension caches and a
12ms route search budget. A timed-out search returns its safe partial route.
Loot goals also require arrival inside the pickup volume, while circle goals
retain5m arrival. Obstacle escape now requires intended travel. These two
changes are tested together: stopping5m from a3.5m pickup and then jetting
because of deliberate rest prevented the old controller from collecting it.
Twelve tests include a reactive loot/energy micro-scenario and real blockage;
it models documented movement rules but is not a full match simulator.
Run `python -m unittest test_motion.py test_navigation.py test_harvest.py`.
Mortar and pitch-targeting regressions are excluded.
Only official practice matches measure placement; these checks do not predict it.
Upgrade selection tied at4.23; close-range mech target priority scored4.15;
cylinder aiming and arrival distance each scored3.85. All were reverted from
the release baseline, with their submitted commits preserved in history.
Only official practice matches measure performance; protocol conformance checks
cannot predict placement.
