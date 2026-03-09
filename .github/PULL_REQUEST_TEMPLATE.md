## What This PR Does

<!-- One paragraph: what plugin/skill/hook is added or changed -->

## Why

<!-- What real-world problem does this solve? -->

## Type of Change

- [ ] New plugin
- [ ] New skill for an existing plugin
- [ ] Hook addition or modification
- [ ] Bug fix
- [ ] Documentation improvement

## Checklist

- [ ] Plugin follows the required directory structure (see CONTRIBUTING.md)
- [ ] Agent has Live Documentation Rule with official source URLs
- [ ] `tools` field is a comma-separated string, not a YAML list
- [ ] Hook scripts use only Python standard library
- [ ] Plugin README is complete with installation, usage, skill table, and references
- [ ] Root README updated (if adding a new plugin or changing skill counts)
- [ ] Tested with Claude Code:
  - [ ] `/agents` shows the subagent
  - [ ] `/plugin` shows no errors
  - [ ] Skills invoke correctly
  - [ ] Hooks fire as expected

## Attribution

<!-- Credit any protocol specs, docs, or sample code that inspired this work -->

## Testing Notes

<!-- Which Claude Code features did you verify? Any edge cases tested? -->
