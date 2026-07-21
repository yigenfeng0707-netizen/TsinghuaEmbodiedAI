# JCIIOT Tiago Transport — Tote Grasp Analysis (L2/L3/L5)

## Current Score: 35/100 (L1=10 + L4=25, stable)

## Tote Object Geometry (L2 green_tote_b01_upper)
- Basket is HOLLOW (open-top container with walls)
- Center: [11.868, 4.625, 1.200]
- Walls (collision geoms):
  - bottom: [11.868, 4.625, 1.009] size [0.3, 0.2, 0.009]
  - front: [11.868, 4.432, 1.200] size [0.3, 0.007, 0.2] (y=4.432)
  - back: [11.868, 4.818, 1.200] size [0.3, 0.007, 0.2] (y=4.818)
  - left: [11.575, 4.625, 1.200] size [0.007, 0.2, 0.2] (x=11.575)
  - right: [12.161, 4.625, 1.200] size [0.007, 0.2, 0.2] (x=12.161)
- Grasp sites (INSIDE basket):
  - right: [12.033, 4.410, 1.400] (x between 11.575 and 12.161 = inside)
  - left: [11.703, 4.410, 1.400]

## Why Current Scripted Grasp Fails on Tote
- Scripted grasp does: up → xy → down → settle → close grippers
- "down" sends eef to below_target (site_z - 0.035 = 1.365)
- eef arrives at site position which is INSIDE the hollow basket
- Closing grippers inside hollow space → no wall contact (fingerpads in air)
- Result: grasp_status = False (no fingerpad contact)

## Wall-Clamp Approach (attempted, partial success)
- Base at [12.6, 4.625, 0.0], yaw=-pi (face -x)
- Move both arms to OUTSIDE walls: right→x=12.155, left→x=11.585, z=1.2
- After close grippers:
  - left right_fingerpad: True (CONTACT!)
  - right fingerpads: False (no contact)
- Issue: Robotiq140 fingerpads orient in y-direction (gripper sides), not x
- Right arm reaches wall x but fingerpads don't clamp the x-direction wall
- Need to rotate eef orientation so fingerpads face x-direction (the wall)

## Next Steps for Tote
1. Determine Robotiq140 fingerpad orientation (which axis the fingers clamp)
2. Set eef quaternion so fingerpads face the wall (x-direction)
3. Or: approach from y-direction (front/back walls) where fingerpads naturally clamp
4. Front wall at y=4.432, back wall at y=4.818 — if base is at y side, arms approach along y
5. Base at [11.868, 5.4, 0.0] (behind back wall), yaw=-pi/2 (face -y), arms reach -y to clamp front/back walls

## Key Files
- robosuite_backend.py: _scripted_grasp_in_wrapped_env (line ~260), _SCRIPTED_GRASP_DEFAULTS
- load_factory_sorting_1_3fo3erfhisem_collect.py: move_along_linear_segment, build_action, get_target_positions
- task_config.json: grasp_poses_by_level (offset 0.45 for tote, 0.65 for container)

## Commits
- 7313f5d: GLFW fix + scripted grasp for L1
- f6674f6: per-level poses + L4 success
- 53a5f78: tote tuning
- c05fc96: tote analysis + L1/L4 stable
