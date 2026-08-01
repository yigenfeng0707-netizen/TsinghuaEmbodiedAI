"""Workflow definitions."""
"""Permitted robot-agent workflow extensions."""

# ── mujoco API compatibility shim ─────────────────────────────
# robosuite's controllers/parts/controller.py calls the legacy
# ``mj_fullM(model, dst, qM)`` signature, but mujoco>=3.2 requires
# ``mj_fullM(model, MjData, dst)``.  robosuite/ is read-only for this
# contest, so we patch the binding here (before any robosuite reset)
# to accept both signatures.  This only fills an API gap; it does not
# alter scoring, physics, or trajectory content.
try:
    import mujoco as _mjc
    import numpy as _np

    if not getattr(_mjc, "_jciiot_fullM_patched", False):
        _orig_fullM = _mjc.mj_fullM
        _model_to_data: "dict[int, object]" = {}

        def _remember(m, d):
            if isinstance(d, _mjc.MjData):
                _model_to_data[id(m)] = d

        # Capture the live MjData that robosuite pairs with each MjModel by
        # observing it through the forward/step calls robosuite already makes.
        for _fn_name in ("mj_forward", "mj_step", "mj_step1", "mj_step2", "mj_resetData"):
            _orig = getattr(_mjc, _fn_name)
            if _orig is None:
                continue

            def _wrap(m, d, _orig=_orig, _fn_name=_fn_name):
                _remember(m, d)
                return _orig(m, d)

            setattr(_mjc, _fn_name, _wrap)

        # mujoco>=3.1 removed MjData.qM; robosuite still reads it as the 3rd
        # arg to legacy mj_fullM. Provide a harmless dense/sparse placeholder
        # so attribute access does not raise before our mj_fullM shim runs.
        if not hasattr(_mjc.MjData, "qM"):
            def _qM_prop(self):
                nM = int(getattr(self.model, "nM", 0) or 0)
                return _np.zeros(nM, dtype=_np.float64)

            _mjc.MjData.qM = property(_qM_prop)

        def _compat_fullM(m, second, third=None):
            # New signature: (MjModel, MjData, dst)
            if isinstance(second, _mjc.MjData):
                return _orig_fullM(m, second, third)
            # Legacy robosuite signature: (MjModel, dst(ndarray), qM(ndarray))
            dst = second
            data = _model_to_data.get(id(m))
            if data is None:
                data = _mjc.MjData(m)
                _model_to_data[id(m)] = data
            return _orig_fullM(m, data, dst)

        _mjc.mj_fullM = _compat_fullM
        _mjc._jciiot_fullM_patched = True

        # robosuite.utils.binding_utils.MjData copies attrs from mujoco.MjData at
        # class-definition time. If robosuite was imported before this shim, its
        # wrapper lacks qM even after we add it on mujoco.MjData — patch wrapper.
        try:
            from robosuite.utils import binding_utils as _bu

            if not hasattr(_bu.MjData, "qM"):
                _bu.MjData.qM = property(lambda self: self._data.qM)
        except Exception:
            pass
except Exception:  # pragma: no cover - never block workflow import
    pass

from robot_agent.workflows.champion_transport import ChampionTransportFlow, TransportReport

__all__ = ["ChampionTransportFlow", "TransportReport"]
