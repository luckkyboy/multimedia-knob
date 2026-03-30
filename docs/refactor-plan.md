# Multimedia Knob Refactor Plan

> For this repository, the scope is intentionally conservative: preserve current behavior, improve structure and maintainability, and clean up the repo so future changes are lower risk.

**Goal:** Refactor the CircuitPython firmware and repository layout without changing hardware wiring, mode count, or current user-facing behavior.

**Architecture:** Move the current monolithic firmware logic toward a small, explicit structure built around configuration, HID actions, mode mapping, and runtime state. Keep the runtime simple enough for CircuitPython while removing duplicated branching and improving error visibility.

**Tech Stack:** CircuitPython on Raspberry Pi Pico, `adafruit_hid`, `adafruit_rgbled`, `button_handler`, rotary encoder input, HID consumer control, keyboard, and mouse.

---

## Scope

### In Scope
- Preserve the current 3-mode behavior and GPIO mapping.
- Refactor firmware structure for readability and maintainability.
- Improve runtime diagnostics and error recovery behavior.
- Align `boot.py` behavior and documentation.
- Clean up repository metadata and documentation.

### Out of Scope
- Adding new modes or new button semantics.
- Changing hardware wiring or supported boards.
- Introducing a complex build, packaging, or CI system.
- Replacing third-party `.mpy` dependencies.

## Current Problems

1. Mode behavior is hard-coded in multiple places inside `pico/code.py`.
2. Error handling is too broad and mostly silent when `debug` is disabled.
3. LED state is updated on every loop iteration instead of only on state changes.
4. Some functions and imports appear unused, which adds noise and confusion.
5. `boot.py` behavior and `README.md` descriptions are not fully aligned.
6. Repository hygiene is weak: IDE files are tracked and dependency provenance is undocumented.

## Target File Layout

### Firmware
- `pico/boot.py`
  - Only decide whether USB storage is exposed at boot and indicate that state clearly.
- `pico/code.py`
  - Minimal entrypoint: initialization, runtime setup, main loop.
- `pico/config.py`
  - Pin assignments, timing thresholds, debug switch, LED colors, and fixed constants.
- `pico/actions.py`
  - Encapsulated HID actions used by modes.
- `pico/modes.py`
  - Mode definitions mapping mode id to actions and LED color.
- `pico/runtime.py`
  - Runtime state, mode switching, encoder handling, button dispatch, and recovery helpers.

### Repository
- `.gitignore`
  - Ignore IDE and local noise consistently.
- `README.md`
  - Hardware, flashing, dependency, troubleshooting, and upgrade guidance.
- `docs/refactor-plan.md`
  - This document, used as the implementation reference.

## Design Rules

1. Preserve behavior first. If a refactor changes behavior, treat that as a regression unless explicitly intended.
2. Keep imports and abstractions small. This is CircuitPython, not a desktop Python app.
3. Centralize all mode behavior in one place.
4. Distinguish normal debug logs from real errors.
5. Update LED output only when state changes.
6. Document third-party binary dependencies and version assumptions.

## Execution Plan

### Task 1: Baseline and Behavior Lock

**Files:**
- Inspect: `pico/code.py`
- Inspect: `pico/boot.py`
- Inspect: `README.md`

- [ ] Record the current behavior contract before changing code.
  - Mode 0:
    - CW: volume up
    - CCW: volume down
    - Short press: play/pause
    - Double press: mute
  - Mode 1:
    - CW: mouse wheel down
    - CCW: mouse wheel up
    - Short press: left click
    - Double press: `COMMAND+L`, then mode advance
  - Mode 2:
    - CW: brightness up
    - CCW: brightness down
    - Short press: no-op
    - Double press: `ENTER`, `9287`, `ENTER`, then mode advance
  - Long press:
    - Advance mode cyclically across 3 modes
  - LED:
    - Mode 0: blue
    - Mode 1: magenta/red
    - Mode 2: green

- [ ] Confirm syntax still passes before refactor.
  - Run: `python3 -m py_compile pico/boot.py pico/code.py`
  - Expected: no output

### Task 2: Extract Static Configuration

**Files:**
- Create: `pico/config.py`
- Modify: `pico/code.py`

- [ ] Move all fixed values into `pico/config.py`.
  - Pins: encoder, switch, RGB LED
  - Constants: total modes, button timing config, debug flag
  - LED colors: one named constant per mode and one error color

- [ ] Replace inline constants in `pico/code.py` with imports from `pico/config.py`.

- [ ] Keep names explicit and consistent.
  - Prefer `TOTAL_MODES` over `totalMode`
  - Prefer `current_mode` for mutable runtime state

- [ ] Re-run syntax validation.
  - Run: `python3 -m py_compile pico/boot.py pico/code.py pico/config.py`
  - Expected: no output

### Task 3: Extract HID Actions

**Files:**
- Create: `pico/actions.py`
- Modify: `pico/code.py`

- [ ] Move concrete HID operations into dedicated functions.
  - `volume_up`
  - `volume_down`
  - `toggle_mute`
  - `mouse_scroll_up`
  - `mouse_scroll_down`
  - `mouse_left_click`
  - `brightness_up`
  - `brightness_down`
  - `host_mode_1_double_press_action`
  - `host_mode_2_double_press_action`

- [ ] Keep action functions thin and side-effect focused.
  - They should use the HID device objects passed in, or be grouped in a tiny actions object.
  - Avoid storing unrelated global state in this layer.

- [ ] Mark host-specific actions in comments so they are clearly not general-purpose behavior.

- [ ] Re-run syntax validation.
  - Run: `python3 -m py_compile pico/boot.py pico/code.py pico/config.py pico/actions.py`
  - Expected: no output

### Task 4: Replace Branching with Mode Definitions

**Files:**
- Create: `pico/modes.py`
- Modify: `pico/code.py`
- Modify: `pico/actions.py`

- [ ] Define each mode in a single table-like structure.
  - Each mode should include:
    - `name`
    - `led_color`
    - `on_cw`
    - `on_ccw`
    - `on_short_press`
    - `on_double_press`

- [ ] Remove duplicated `if currentMode == ...` branches from rotation and press handlers.

- [ ] Keep long press mode switching outside per-mode config, since it is global behavior.

- [ ] Verify mode parity manually by checking the new mapping against Task 1.

- [ ] Re-run syntax validation.
  - Run: `python3 -m py_compile pico/boot.py pico/code.py pico/config.py pico/actions.py pico/modes.py`
  - Expected: no output

### Task 5: Introduce Runtime State and Recovery Helpers

**Files:**
- Create: `pico/runtime.py`
- Modify: `pico/code.py`
- Modify: `pico/modes.py`

- [ ] Move mutable state into a dedicated runtime object or small stateful helper.
  - Current mode
  - Last encoder position
  - Last LED color written
  - HID handles needed for recovery

- [ ] Add explicit methods for:
  - `set_mode(index)`
  - `advance_mode()`
  - `handle_rotation(delta)`
  - `handle_short_press()`
  - `handle_double_press()`
  - `recover_hid(force=False)`

- [ ] Update LED only when color changes.

- [ ] Keep the main loop thin: read input, compute delta, dispatch to runtime.

- [ ] Re-run syntax validation.
  - Run: `python3 -m py_compile pico/boot.py pico/code.py pico/config.py pico/actions.py pico/modes.py pico/runtime.py`
  - Expected: no output

### Task 6: Tighten Error Handling

**Files:**
- Modify: `pico/code.py`
- Modify: `pico/runtime.py`

- [ ] Replace silent broad exception handling with structured logging.
  - `log_debug(...)` respects the debug flag.
  - `log_error(...)` always prints.

- [ ] Distinguish two recovery levels.
  - Button/HID operation failures:
    - Log error
    - Attempt HID reinitialization
    - Continue loop
  - Main loop failures:
    - Log error with current mode and exception
    - Attempt controlled recovery
    - Set LED to error color if recovery fails repeatedly

- [ ] Avoid infinite silent failure loops.
  - If repeated recovery fails, keep the device alive but visible as unhealthy.

- [ ] Re-run syntax validation after every recovery-path change.

### Task 7: Clean Up `boot.py`

**Files:**
- Modify: `pico/boot.py`
- Modify: `README.md`

- [ ] Make the boot logic explicit and easy to read.
  - If button not held at boot:
    - disable USB drive
  - If button held at boot:
    - leave USB drive enabled
    - show write-mode LED indication

- [ ] Ensure comments and behavior match exactly.

- [ ] Decide one LED behavior and document that exact behavior.
  - If it should blink, implement real alternating transitions.
  - If it should stay solid red, document it that way.

- [ ] Re-run syntax validation.
  - Run: `python3 -m py_compile pico/boot.py pico/code.py pico/config.py pico/actions.py pico/modes.py pico/runtime.py`
  - Expected: no output

### Task 8: Repository Hygiene

**Files:**
- Modify: `.gitignore`
- Remove from tracking: `.idea/*` as appropriate

- [ ] Expand `.gitignore` to cover local IDE files and similar workspace noise.

- [ ] Stop tracking `.idea` files that are not part of the project deliverable.

- [ ] Keep repository contents focused on firmware, assets, and docs.

### Task 9: Rewrite `README.md`

**Files:**
- Modify: `README.md`

- [ ] Restructure the README into clear sections:
  - Project overview
  - Features
  - Hardware list
  - GPIO wiring
  - Flashing CircuitPython
  - Copying firmware files
  - Dependency files in `pico/lib`
  - Boot/write mode behavior
  - Troubleshooting
  - Source attribution

- [ ] Document binary dependency provenance.
  - Which files are bundled in `pico/lib`
  - Which CircuitPython release the bundled UF2 corresponds to
  - That `.mpy` files may need regeneration or replacement when upgrading CircuitPython

- [ ] Clarify the limits of current host-side behavior.
  - Especially the host-specific keyboard sequence in mode 2

### Task 10: Verification Pass

**Files:**
- Verify: `pico/boot.py`
- Verify: `pico/code.py`
- Verify: `pico/config.py`
- Verify: `pico/actions.py`
- Verify: `pico/modes.py`
- Verify: `pico/runtime.py`
- Verify: `README.md`
- Verify: `.gitignore`

- [ ] Run the final syntax check.
  - Run: `python3 -m py_compile pico/boot.py pico/code.py pico/config.py pico/actions.py pico/modes.py pico/runtime.py`
  - Expected: no output

- [ ] Diff review checklist:
  - No behavior changes introduced unintentionally
  - No unused imports remain
  - No stale helper functions remain
  - README matches actual code behavior
  - `.idea` is no longer part of the maintained repository surface

- [ ] Hardware sanity checklist after deployment to Pico:
  - Encoder rotation works in all 3 modes
  - Short press works in all expected modes
  - Double press still triggers the same behavior as before
  - Long press cycles modes correctly
  - LED color changes only when mode changes
  - Write mode still works when holding the button during plug-in

## Practical Notes

- Keep the split small. If `runtime.py` or `actions.py` would end up being tiny wrappers, it is acceptable to collapse them later, but only after mode behavior is centralized.
- Avoid introducing features disguised as cleanup.
- Keep comments short and only where the hardware or host coupling is non-obvious.

## Recommended Commit Sequence

1. `refactor: extract firmware config and action helpers`
2. `refactor: centralize mode definitions and runtime state`
3. `fix: improve runtime error handling and boot flow clarity`
4. `docs: clean repository metadata and rewrite setup docs`

## Exit Criteria

This refactor is complete when:
- Current behavior is preserved.
- Mode behavior is defined in one place.
- Runtime errors are visible and recoverable.
- `boot.py` behavior and documentation match.
- Repository setup and dependency story are understandable to a new user.
