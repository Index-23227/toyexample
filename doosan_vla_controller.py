"""
ROS2 Node: VLA Inference Server → Doosan E0509 제어
로봇 없이 코드 구조만 미리 완성. 현장에서 IP/port만 설정.

실행:
  ros2 launch dsr_bringup2 dsr_bringup2.launch.py mode:=real model:=e0509 host:=192.168.127.100
  python doosan_vla_controller.py
"""

import time
import numpy as np
import requests
from typing import Optional

# ============================================================
# VLA Inference Client
# ============================================================

class VLAInferenceClient:
    """VLA inference server (port 8000)에 HTTP 요청"""

    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url

    def predict(self, image: np.ndarray, state: np.ndarray, instruction: str) -> np.ndarray:
        """
        Args:
            image: RGB image (H, W, 3) uint8
            state: [j1..j6, grip] 7-dim
            instruction: 자연어 명령 (한국어)
        Returns:
            action: [Δj1..Δj6, grip] 7-dim (또는 action chunk)
        """
        import base64
        from io import BytesIO
        from PIL import Image

        # Image → base64
        img_pil = Image.fromarray(image)
        buffer = BytesIO()
        img_pil.save(buffer, format="JPEG")
        img_b64 = base64.b64encode(buffer.getvalue()).decode()

        payload = {
            "image": img_b64,
            "state": state.tolist(),
            "instruction": instruction,
        }

        try:
            resp = requests.post(
                f"{self.server_url}/predict",
                json=payload,
                timeout=2.0  # 2초 timeout
            )
            resp.raise_for_status()
            data = resp.json()
            return np.array(data["actions"])  # shape: (horizon, 7) or (7,)
        except Exception as e:
            print(f"[VLA] Inference failed: {e}")
            return None


# ============================================================
# Doosan Robot Interface (via dsr_msgs2 / DRCF)
# ============================================================

class DoosanRobotInterface:
    """
    두산 로봇 ROS2 인터페이스.
    현장에서 실제 연결 후 테스트할 것.

    두 가지 방식 지원:
    1. ROS2 FollowJointTrajectory action
    2. 두산 DRCF TCP 직접 통신 (servoj)
    """

    def __init__(self, mode: str = "drcf", robot_ip: str = "192.168.127.100"):
        self.mode = mode
        self.robot_ip = robot_ip
        self.drcf_port = 12345

        if mode == "ros2":
            self._init_ros2()
        elif mode == "drcf":
            self._init_drcf()

    def _init_ros2(self):
        """ROS2 action client 초기화"""
        # 현장에서 구현
        # rclpy.init()
        # self.node = ...
        # self.action_client = ActionClient(node, FollowJointTrajectory, ...)
        pass

    def _init_drcf(self):
        """DRCF TCP 직접 연결"""
        import socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 현장에서: self.sock.connect((self.robot_ip, self.drcf_port))
        print(f"[DRCF] Will connect to {self.robot_ip}:{self.drcf_port}")

    def get_current_state(self) -> dict:
        """
        현재 로봇 상태 읽기.
        Returns: {'joint_positions': [6,], 'gripper': float}
        """
        # --- 현장 구현 ---
        # ROS2: /dsr01e0509/joint_states topic subscribe
        # DRCF: get_current_posj() 호출

        # Placeholder (테스트용)
        return {
            'joint_positions': np.zeros(6),
            'gripper': 0.0,
        }

    def send_joint_target(self, joint_targets: np.ndarray, duration_sec: float = 0.1):
        """
        Joint position 명령 전송.

        Args:
            joint_targets: [j1..j6] in radians
            duration_sec: 이 시간 안에 도달
        """
        # 두산은 degree 단위로 받음!
        joint_deg = np.rad2deg(joint_targets).tolist()

        if self.mode == "drcf":
            # servoj(pos, vel, acc, time)
            # 현장에서: self._send_drcf_command(f"servoj({joint_deg}, 0, 0, {duration_sec})")
            pass
        elif self.mode == "ros2":
            # FollowJointTrajectory goal 전송
            pass

        # Debug
        print(f"[CMD] Target (deg): [{', '.join(f'{d:.1f}' for d in joint_deg)}]")

    def set_gripper(self, open_cmd: bool):
        """그리퍼 열기/닫기"""
        # 현장에서 구현: 두산 Tool I/O 또는 Robotiq 제어
        state_str = "OPEN" if open_cmd else "CLOSE"
        print(f"[GRIPPER] {state_str}")


# ============================================================
# Main Control Loop
# ============================================================

class VLAControlLoop:
    """
    메인 제어 루프: Camera → VLA → Adapter → Robot
    """

    def __init__(
        self,
        vla_url: str = "http://localhost:8000",
        robot_ip: str = "192.168.127.100",
        control_hz: float = 10.0,
        instruction: str = "저 긴 물체 좀 가져다줘",
    ):
        self.vla_client = VLAInferenceClient(vla_url)
        self.robot = DoosanRobotInterface(mode="drcf", robot_ip=robot_ip)

        from doosan_action_adapter import DoosanActionAdapter, DoosanSafetyConfig
        self.adapter = DoosanActionAdapter(
            safety_config=DoosanSafetyConfig(),
            norm_stats=None,  # 학습 후 채워넣기
        )

        self.control_hz = control_hz
        self.dt = 1.0 / control_hz
        self.instruction = instruction
        self.camera = None  # 현장에서 카메라 객체 연결

    def get_camera_image(self) -> np.ndarray:
        """카메라에서 RGB 이미지 캡처"""
        # 현장 구현: RealSense / USB cam / ROS2 topic
        # Placeholder
        return np.zeros((224, 224, 3), dtype=np.uint8)

    def run(self, max_steps: int = 200):
        """
        메인 루프 실행.
        max_steps=200 at 10Hz = 20초 에피소드
        """
        print(f"=== VLA Control Loop Start ===")
        print(f"  Instruction: {self.instruction}")
        print(f"  Control Hz: {self.control_hz}")
        print(f"  Max steps: {max_steps}")
        print()

        for step in range(max_steps):
            t0 = time.time()

            # 1. 로봇 상태 읽기
            state = self.robot.get_current_state()
            joint_pos = state['joint_positions']
            gripper = state['gripper']

            # Adapter에 현재 상태 전달
            obs_state = np.concatenate([joint_pos, [gripper]])  # [7,]
            self.adapter.set_current_state(joint_pos, gripper)

            # 2. 카메라 이미지
            image = self.get_camera_image()

            # 3. VLA inference
            raw_action = self.vla_client.predict(image, obs_state, self.instruction)

            if raw_action is None:
                print(f"[Step {step}] VLA inference failed, holding position")
                continue

            # action chunk인 경우 첫 번째만 사용
            if raw_action.ndim == 2:
                raw_action = raw_action[0]

            # 4. Action adapter (safety clamp 포함)
            cmd = self.adapter.convert(raw_action, dt=self.dt)

            # 5. 로봇에 명령 전송
            self.robot.send_joint_target(cmd['joint_targets'], duration_sec=self.dt)
            self.robot.set_gripper(cmd['gripper_open'])

            # 6. Timing
            elapsed = time.time() - t0
            sleep_time = self.dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                print(f"[Step {step}] Overrun: {elapsed:.3f}s > {self.dt:.3f}s")

            # 7. Logging
            if step % 20 == 0:
                print(f"[Step {step:3d}] clamp_ratio={cmd['clamp_ratio']:.1%} "
                      f"elapsed={elapsed*1000:.0f}ms")

        print(f"\n=== Control Loop Done ===")
        print(f"  Total clamp ratio: {cmd['clamp_ratio']:.1%}")


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vla-url", default="http://localhost:8000")
    parser.add_argument("--robot-ip", default="192.168.127.100")
    parser.add_argument("--hz", type=float, default=10.0)
    parser.add_argument("--instruction", default="저 긴 물체 좀 가져다줘")
    parser.add_argument("--max-steps", type=int, default=200)
    args = parser.parse_args()

    loop = VLAControlLoop(
        vla_url=args.vla_url,
        robot_ip=args.robot_ip,
        control_hz=args.hz,
        instruction=args.instruction,
    )
    loop.run(max_steps=args.max_steps)
