# Vérification / verification

From the GMT directory, with requirements installed:

- `python tests/verify.py`: exact affine-element consistency and orthotropic rotation.
- `python tests/api.py`: local HTTP integration, including rejection of stale geometry.
- `node tests/signal.mjs`: optional JavaScript DSP/WAV checks (Node.js needed only for this test).
- `python tests/benchmarks.py`: independent cantilever bending and rectangular rigid-cavity analytical frequencies.
- `python tests/verify.py --full`: all six guitar templates at 55 mm maximum mesh size, 16 structural modes and eight cavity modes. This is a construction/integration check, **not a converged guitar calculation**.

All generated outputs go to `data/verification` unless `--output` is supplied. The full test creates meshes and requires Gmsh's native libraries. Tests do not require opening a browser.

Current audit reports are in `examples/verification_v1_3`; 1.2 reports are retained in `examples/verification_v1_2`; 1.1 reports describe the previous cutaways; historical 1.0 numerical reports are in `examples/legacy_v1_0/verification`. See VERIFICATION.md for mesh-dependence and untested scope.

- `python tests/contours.py`: outline dimensions, cutaway depth/side, opening containment, display/CAD error bound and legacy JSON compatibility.
- `python tests/contours.py --mesh`: conformal volume meshes for six templates × four cutaway styles.

- `python tests/cutaway_physics.py`: four cutaway cases through modes, FRF and string synthesis; finite physical outputs and modal/passivity checks.

- `python tests/reduction.py`: independent dense-system reference for residual static compliance, mass orthogonality and dynamic response.
- JavaScript DSP tests also check preservation of high overtones outside the FE modal band and time/frequency selection filtering.

The release additionally exercised the interface with a minimal DOM and real CPU canvas renderer (mock HTTP/audio/Three constructor) and checked Three.js quadratic geometry on the CPU. This is not a browser or GPU interaction test.

- `python tests/bands.py`: narrow modal band, independent synthesis band and neck/free/rim support checks. Reports the actual residual compliance error; the free-body test uses a 1% recovery tolerance.

- `python tests/audit.py`: independent dense coupled solve, curved wood frames, exact time shift, zero pre-attack samples, superposition, concurrent cache and input validation.
- `python tests/server_guards.py`: local-only request checks, FFT validation, queued-solve deduplication and queue limits; no FE computation.
- `python tests/startup.py`: real local server launch, second-launch detection and occupied-port handling; no browser is opened.
- JavaScript DSP tests include DC calibration and extrema-preserving waveforms. The 1.3 DOM/CPU-Canvas harness also exercises stale results, Stop during synthesis, live gain and snapshots (see AUDIT.md; browser services are simulated).
