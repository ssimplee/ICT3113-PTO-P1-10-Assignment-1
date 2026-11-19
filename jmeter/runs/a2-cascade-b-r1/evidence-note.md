# Evidence note: a2-cascade-b-r1

The files in this folder were produced under the run ID `a2-cascade-b-r1-retry` and
moved here afterwards. Their contents are unchanged, so `manifest.json`,
`server-ready.json`, `server-finish.json`, `client-start.json` and
`server.override.json` still name the retry ID.

## What happened

1. The server was prepared and warmed up for `a2-cascade-b-r1` on 19 November 2026 at
   21:22:45 SGT (`not-started/server-ready.json`).
2. That ready record was committed at 21:27:59 and reached the load generator at
   21:28:20, 5 minutes 35 seconds after the warm-up. Ollama unloads an idle model after
   5 minutes, so the two models could no longer be assumed loaded.
3. JMeter was not started for that preparation. No workload ticket was sent.
4. An identical bundle was generated as `a2-cascade-b-r1-retry`: same plan, tickets,
   arrival seed and file hashes, with only the run ID and preparation revision
   different. The server was prepared again and JMeter started 45 seconds after the
   warm-up.
5. The retry run completed: 30 tickets sent, 30 completed, 0 errors, 30 stored by the
   service.

This is the only repeat-1 run of Cascade Setting B. No measured run was discarded or
replaced.
