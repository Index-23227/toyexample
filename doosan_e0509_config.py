"""
Doosan E0509 Embodiment Configuration for GR00T N1.6
미리 작성 가능 — 현장에서 joint limits만 실측 확인 후 업데이트
"""

import numpy as np

# ============================================================
# Doosan E0509 Embodiment Registration
# ============================================================

DOOSAN_E0509_CONFIG = {
    "embodiment_name": "doosan_e0509",
    "num_joints": 6,
    "num_actions": 7,  # 6 joints + 1 gripper

    # --- Joint Names (ROS2 doosan-robot2 convention) ---
    "joint_names": [
        "joint1", "joint2", "joint3",
        "joint4", "joint5", "joint6",
    ],

    # --- Joint Limits (radians) ---
    # ⚠️ 현장 실측 후 업데이트할 것
    "joint_limits_lower": np.deg2rad([-350, -95, -145, -350, -350, -350]),
    "joint_limits_upper": np.deg2rad([+350, +95, +145, +350, +350, +350]),

    # --- Joint Max Velocities (rad/s) ---
    "joint_max_velocities": np.deg2rad([120, 120, 150, 225, 225, 225]),

    # --- Gripper ---
    "gripper_range": [0.0, 1.0],  # 0=closed, 1=open (normalize at adapter)

    # --- Action Space ---
    "action_type": "joint_delta",  # state-relative delta
    "action_dim": 7,               # [Δj1, Δj2, Δj3, Δj4, Δj5, Δj6, grip]

    # --- Observation Space ---
    "state_dim": 7,                # [j1, j2, j3, j4, j5, j6, grip]

    # --- Control ---
    "control_frequency_hz": 10,    # target Hz (두산 E0509: 5~15Hz 가능)
    "action_horizon": 16,          # GR00T default chunk size
}

# ============================================================
# Normalization Statistics (placeholder — 데모 수집 후 계산)
# ============================================================

DOOSAN_NORM_STATS = {
    # 학습 전에 데모 데이터에서 mean/std 계산해서 채워넣기
    "action_mean": np.zeros(7),
    "action_std": np.ones(7),
    "state_mean": np.zeros(7),
    "state_std": np.ones(7),
}


def get_doosan_config():
    """GR00T N1.6 embodiment 등록 시 호출"""
    return DOOSAN_E0509_CONFIG


def compute_norm_stats(demo_dataset):
    """
    데모 수집 후 호출하여 normalization stats 계산.

    Args:
        demo_dataset: list of episodes, 각 episode는 dict with 'actions', 'states'
    Returns:
        dict with action_mean, action_std, state_mean, state_std
    """
    all_actions = np.concatenate([ep['actions'] for ep in demo_dataset], axis=0)
    all_states = np.concatenate([ep['states'] for ep in demo_dataset], axis=0)

    return {
        "action_mean": all_actions.mean(axis=0),
        "action_std": all_actions.std(axis=0).clip(min=1e-6),
        "state_mean": all_states.mean(axis=0),
        "state_std": all_states.std(axis=0).clip(min=1e-6),
    }
