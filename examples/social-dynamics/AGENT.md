# Social experiments

Use only exported sunholo/social_dynamics APIs. Config/policy choices live here,
not in the library or game. Read README before changing recordings. Regenerate
path lock with ailang lock. `make -f examples/social-dynamics/Makefile validate`
runs native tests, five outcome controls, replay and strict-VM parity. IO only;
no provider calls. Main loop variable IO counts are bounded by run.sh input limits.
