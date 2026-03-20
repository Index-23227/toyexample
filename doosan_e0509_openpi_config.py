"""
Doosan E0509 config for OpenPI (π₀ / π₀.5) fine-tuning.
openpi/src/openpi/training/config.py에 추가할 TrainConfig.
"""

# ============================================================
# OpenPI config.py에 추가할 코드
# ============================================================

"""
# --- 아래를 openpi/src/openpi/training/config.py의 _CONFIGS 리스트에 추가 ---

TrainConfig(
    name="pi05_doosan_e0509",
    model=pi0_config.Pi0Config(
        pi05=True,
        action_dim=7,       # 6 joints + 1 gripper
        action_horizon=16,  # action chunk length
        max_token_len=180,
    ),
    data=LeRobotDataConfig(
        repo_id="local/doosan_e0509_demos",
        base_config=DataConfig(prompt_from_task=True),
        assets=AssetsConfig(
            assets_dir="./assets/doosan_e0509",
            asset_id="doosan_e0509",
        ),
        # NOTE: delta action transform 적용 여부
        # 수집 데이터가 absolute joint position이면 아래 활성화
        # use_delta_joint_actions=True,
    ),
    weight_loader=weight_loaders.CheckpointWeightLoader(
        "gs://openpi-assets/checkpoints/pi05_base/params"
    ),
    # Fine-tuning hyperparams (50 demos 기준)
    num_train_steps=5_000,    # 50 demos → 5k steps 충분
    batch_size=32,            # V100 16GB → bs=32 가능할 수도
    # LoRA 설정 (VRAM 절약)
    freeze_filter=pi0_config.Pi0Config(
        pi05=True,
        paligemma_variant="gemma_2b_lora",
        action_expert_variant="gemma_300m_lora",
        action_dim=7,
        action_horizon=16,
        max_token_len=180,
    ).get_freeze_filter(),
    ema_decay=None,  # LoRA에서는 EMA off
),
"""


# ============================================================
# RepackTransform for Doosan E0509 (LeRobot format)
# ============================================================

class DoosanE0509RepackTransform:
    """데모 데이터의 key를 openpi가 기대하는 형식으로 매핑"""

    def __call__(self, sample):
        return {
            "images": {
                "cam_ext": sample["observation.images.cam_ext"],
                # wrist cam이 있다면:
                # "cam_wrist": sample["observation.images.cam_wrist"],
            },
            "state": sample["observation.state"],   # [j1..j6, grip] 7-dim
            "actions": sample["action"],              # [Δj1..Δj6, grip] 7-dim
        }
