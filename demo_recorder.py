"""
데모 수집 스크립트.
두산 Direct Teaching (Hand Guiding) + 카메라 동기 녹화.

현장에서 실행:
  python demo_recorder.py --robot-ip 192.168.127.100 --save-dir ./demos
"""

import os
import time
import json
import numpy as np
from pathlib import Path
from datetime import datetime


class DemoRecorder:
    """
    Direct Teaching 데모 녹화기.
    두산 Cockpit 버튼으로 teaching mode 진입 후,
    이 스크립트가 joint positions + camera를 동기 녹화.
    """

    def __init__(self, save_dir: str, robot_ip: str, record_hz: float = 10.0):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.robot_ip = robot_ip
        self.record_hz = record_hz
        self.dt = 1.0 / record_hz

        # 현장에서 초기화
        self.robot = None  # DoosanRobotInterface
        self.camera = None  # cv2.VideoCapture or RealSense

    def record_episode(self, task_instruction: str, episode_id: int) -> dict:
        """
        1 에피소드 녹화.
        Direct Teaching 중 joint states + camera를 동기 기록.

        Returns:
            episode dict with 'states', 'actions', 'images', 'instruction'
        """
        print(f"\n{'='*50}")
        print(f"  Episode {episode_id}")
        print(f"  Instruction: {task_instruction}")
        print(f"  [Enter]를 눌러 녹화 시작, [q]를 눌러 종료")
        print(f"{'='*50}")
        input("Press Enter to START recording...")

        states = []
        images = []
        timestamps = []

        print("Recording... (press Ctrl+C to stop)")

        try:
            while True:
                t0 = time.time()

                # 로봇 상태 읽기
                state = self._get_robot_state()  # [j1..j6, grip] 7-dim
                states.append(state)

                # 카메라 캡처
                img = self._get_camera_image()  # (H, W, 3) uint8
                images.append(img)

                timestamps.append(time.time())

                # Timing
                elapsed = time.time() - t0
                if self.dt - elapsed > 0:
                    time.sleep(self.dt - elapsed)

        except KeyboardInterrupt:
            print(f"\nRecording stopped. {len(states)} frames captured.")

        # Compute actions (delta between consecutive states)
        states_arr = np.array(states)
        actions = np.diff(states_arr, axis=0)  # (T-1, 7) delta
        # 마지막 action은 0 (정지)
        actions = np.vstack([actions, np.zeros((1, 7))])

        episode = {
            'instruction': task_instruction,
            'states': states_arr,           # (T, 7)
            'actions': actions,             # (T, 7) delta
            'images': np.array(images),     # (T, H, W, 3)
            'timestamps': timestamps,
            'metadata': {
                'episode_id': episode_id,
                'record_hz': self.record_hz,
                'robot': 'doosan_e0509',
                'recorded_at': datetime.now().isoformat(),
            }
        }

        # Save
        ep_dir = self.save_dir / f"episode_{episode_id:04d}"
        ep_dir.mkdir(exist_ok=True)
        np.savez_compressed(
            ep_dir / "data.npz",
            states=episode['states'],
            actions=episode['actions'],
        )
        # Save images separately (큰 파일)
        np.savez_compressed(ep_dir / "images.npz", images=episode['images'])
        # Save metadata
        with open(ep_dir / "metadata.json", 'w') as f:
            json.dump(episode['metadata'], f, indent=2)
            json.dump({'instruction': task_instruction}, f)

        print(f"Saved to {ep_dir}")
        return episode

    def _get_robot_state(self) -> np.ndarray:
        """현장 구현: 로봇 joint state + gripper 읽기"""
        # Placeholder
        return np.zeros(7)

    def _get_camera_image(self) -> np.ndarray:
        """현장 구현: 카메라 캡처"""
        # Placeholder
        return np.zeros((224, 224, 3), dtype=np.uint8)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--save-dir", default="./demos")
    parser.add_argument("--robot-ip", default="192.168.127.100")
    parser.add_argument("--hz", type=float, default=10.0)
    parser.add_argument("--instruction", default="파란 약병을 트레이에 옮겨줘")
    parser.add_argument("--num-episodes", type=int, default=50)
    args = parser.parse_args()

    recorder = DemoRecorder(args.save_dir, args.robot_ip, args.hz)

    for i in range(args.num_episodes):
        recorder.record_episode(args.instruction, episode_id=i)

        if i < args.num_episodes - 1:
            cont = input(f"\n다음 에피소드 ({i+1}/{args.num_episodes})? [Enter/q]: ")
            if cont.lower() == 'q':
                break

    print(f"\nDone! {i+1} episodes recorded in {args.save_dir}")
