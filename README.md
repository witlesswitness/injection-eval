# injection-eval

A small, reproducible study of prompt-injection susceptibility and reasoning-based
monitoring in LLM agents.

## What this is

A simulated customer-support agent is given file tools in a sandbox and asked to handle
a support ticket. Some tickets hide malicious instructions that try to make the agent
exfiltrate a secret (a benign canary token). We measure how often the agent gets hijacked
across injection styles, models, and a defense, and whether a separate monitor can catch it.

Everything runs in a simulated sandbox with a fake canary credential. No real systems and
no jailbreaking of safety training; this is defensive measurement of injection susceptibility.

## Headline findings (482 episodes)

- **Subtlety beats bluntness.** A plausibly-framed "verification" injection hijacked ~15%
  of the time overall, vs ~0–6% for crude "ignore your instructions" style injections.
- **Subtlety beats capability.** Crude injections never hijacked the stronger model
  (Sonnet, 0%), but the plausible one hijacked it as often as the weaker model (both 30%,
  no defense). A more capable model was not automatically a safer one.
- **A one-paragraph "spotlighting" defense eliminated hijacks** (10.5% → 0% across 200
  defended episodes).
- **A separate monitor caught 100% of hijacks.** Giving it the agent's reasoning, not just
  its actions, cut false positives (3% → 2%).

See `figures/` for the charts and charlestimmons.com/research for the full writeup.

## Repo layout

| File | Role |
|---|---|
| `sandbox.py` | Simulated filesystem + agent tools + the hijack check |
| `scenarios.py` | 6 support tickets + 5 injection styles |
| `run_agent.py` | The agent loop, scoring, and per-episode saving |
| `monitor.py` | Separate monitor model; two views (actions-only vs with-reasoning) |
| `runner.py` | Sweeps the full condition grid |
| `analyze.py` | Hijack rates (Wilson CIs) + monitor detection |
| `rescore.py` | Re-scores saved episodes with a hardened monitor |
| `figures.py` | Generates the figures |

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install anthropic python-dotenv matplotlib numpy
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
python3 runner.py      # runs the sweep -> data/
python3 analyze.py     # prints the result tables
python3 figures.py     # writes figures/
```

## Method notes (lessons worth recording)

- **Pilot floor effect.** Blatant injections were refused almost 100% of the time, which
  forced a pivot to subtler, plausibly-framed injections before any signal appeared.
- **A benign task can lure an agent toward secrets.** The agent read the secret file during
  an honest password-reset, which confounds a naive "attempted" metric, so a hijack is
  defined as the canary leaking *anywhere* it is produced.
- **Leaks route around a narrow detector.** The agent often pasted the secret into its reply
  rather than the expected outbox, so detection has to cover every output channel.
- **Monitors can silently fail on the scariest cases** (token starvation / over-refusal);
  the monitor had to be hardened to always return a verdict.

## Scope & ethics

Simulated sandbox, benign canary, defensive measurement. This is not a vulnerability
disclosure; prompt-injection susceptibility is a known, open research problem.

## Acknowledgment

Built as a pair-programming exercise with Claude (Anthropic). All research decisions,
analysis, and interpretation are my own.
