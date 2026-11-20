# harness.launcher

Launches one browser run with no automation framework: a fresh temporary profile, quiet browser settings,
the run configuration in the page URL and, when asked, `taskset` inside a
systemd scope. It waits until the page has posted its result to
the results server, then stops the browser, kills what it left behind and
stores the run context next to the result.

```bash
python3 -m harness.launcher --browser chrome --executable PATH --run ID --query "workload=filter&..."
```

## Main pieces

| File | Responsibility |
|---|---|
| `commands.py` | `ChromeCommand`, `FirefoxCommand`: flags, preferences and version command |
| `url.py` | `run_url`: the page URL with run id, environment and start delay |
| `launcher.py` | `Launcher`: profile, launch, wait, teardown and context |
| `outcome.py` | `RunStatus`, `RunOutcome` and what a launch recorded (the passes of the query included) |
| `processes.py` | Stopping the process group and killing leftovers on the profile |
| `cli.py`, `__main__.py` | Command line |

## Flow

```mermaid
flowchart TD
    run[Launcher.run] --> reuse{run files exist?}
    reuse -->|yes| refuse[FileExistsError]
    reuse -->|no| profile[fresh profile]
    profile --> start[CPU usage start]
    start --> popen[browser in taskset / scope]
    popen --> wait{csv, error, exit or timeout}
    wait --> teardown[CPU time, escaped processes, stop scope, stop group, kill leftovers]
    teardown --> context[RunContext into .json or .error.json]
    context --> cleanup[remove profile]
```
