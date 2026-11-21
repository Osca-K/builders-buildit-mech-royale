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

The upgrade-selection candidate tied the best score at 4.23. The current
candidate keeps those upgrades and ignores NPC firing targets when a hostile
mech is within 85m, concentrating fire on the immediate combat threat.
The cylinder-aiming and arrival-distance experiments each scored 3.85 and were
reverted. Only official practice matches measure performance; protocol conformance
checks cannot predict placement.
