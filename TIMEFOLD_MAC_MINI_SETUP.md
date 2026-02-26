# Timefold config on Mac Mini (agent host)

**Host:** `appcaire-mac-mini.local` (VNC: `vnc://appcaire-mac-mini.local`)

The agent service on the Mac Mini sources `~/.config/caire/env` when running compound scripts. Add the Timefold keys there so FSR research (fetch, submit, continuity-compare) works.

## Steps (run on the Mac Mini)

1. **VNC in** to the Mac Mini (e.g. Screen Sharing to `appcaire-mac-mini.local`).

2. **Open Terminal** and run:

   ```bash
   mkdir -p ~/.config/caire
   touch ~/.config/caire/env
   chmod 600 ~/.config/caire/env
   ```

3. **Edit the env file** and add the Timefold variables (get real keys from your Timefold account / secrets; do not commit them):

   ```bash
   open -e ~/.config/caire/env
   ```

   Add these lines (replace the placeholder values with real keys):

   ```bash
   # Timefold FSR + ESS (for agent-run research)
   export TIMEFOLD_API_KEY=<prod-or-stage-key>
   export TIMEFOLD_ESS_API_KEY=<ess-staging-key>
   ```

   If `~/.config/caire/env` already exists (e.g. for `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`), append the two `export` lines instead of overwriting.

4. **Save** and close the file. No restart needed; the next agent run will pick up the vars.

## Verify

On the Mac Mini:

```bash
source ~/.config/caire/env
echo "TIMEFOLD_API_KEY set: $(if [ -n "$TIMEFOLD_API_KEY" ]; then echo yes; else echo no; fi)"
```

You should see `TIMEFOLD_API_KEY set: yes`.

## Reference

- Variable names and optional URLs: [docs/timefold.env.example](timefold.env.example)
- Full env doc: [docs/TIMEFOLD_ESS_FSR_ENV.md](TIMEFOLD_ESS_FSR_ENV.md)
