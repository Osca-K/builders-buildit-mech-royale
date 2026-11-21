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

This experiment starts from the4.25-point entry(f11c16c9496a) and adds mortar
pickup and ballistic firing. A flight-time solver includes target velocity,
gravity and the forward barrel displacement, considers low/high arcs, and checks
terrain/buildings and torso pitch limits. It avoids shots within20m or whose
predicted impact threatens our own body. The gun resumes its normal aim as soon
as the mortar enters cooldown. Lightning remains the preferred pickup and can
replace a mortar. Existing loot arrival and obstacle escape policy are retained.
Fifteen regression tests cover reachable motion, impacts, cover, aim gating,
self-splash avoidance and resuming gun fire. Run
`python -m unittest test_motion.py test_mortar.py`.
These physics checks do not measure match quality; only official practice does.
Upgrade selection tied at4.23; close-range mech target priority scored4.15;
cylinder aiming and arrival distance each scored3.85. All were reverted from
the release baseline, with their submitted commits preserved in history.
Only official practice matches measure performance; protocol conformance checks
cannot predict placement.
