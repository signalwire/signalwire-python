"""Example: Control an active call with media operations (play, record, transcribe, denoise).

NOTE: These commands require an active call. The call_id used here is
illustrative — in production you would obtain it from a dial response or
inbound call event.

Set these env vars (or pass them directly to RestClient):
  SIGNALWIRE_PROJECT_ID   - your SignalWire project ID
  SIGNALWIRE_API_TOKEN    - your SignalWire API token
  SIGNALWIRE_SPACE        - your SignalWire space (e.g. example.signalwire.com)

For full HTTP debug output:
  SIGNALWIRE_LOG_LEVEL=debug
"""

from signalwire.rest import RestClient, SignalWireRestError

client = RestClient()


def main():
    # 1. Dial an outbound call
    print("Dialing outbound call...")
    try:
        call = client.calling.dial(
            from_="+15559876543",
            to="+15551234567",
            url="https://example.com/call-handler",
        )
        call_id = call.get("id", "demo-call-id")
        print(f"  Call initiated: {call_id}")
    except SignalWireRestError as e:
        print(f"  Dial failed (expected in demo): {e.status_code}")
        call_id = "demo-call-id"

    # 2. Play TTS audio
    #    The control_id ties later pause/resume/stop commands to this playback.
    control_id = "demo-play-control-id"
    print("\nPlaying TTS on call...")
    try:
        client.calling.play(
            call_id,
            play=[{"type": "tts", "params": {"text": "Welcome to SignalWire."}}],
            control_id=control_id,
        )
        print("  Play started")
    except SignalWireRestError as e:
        print(f"  Play failed (expected in demo): {e.status_code}")

    # 3. Pause, resume, adjust volume, stop playback
    print("\nControlling playback...")
    for action, fn in [
        ("Pause", lambda: client.calling.play_pause(call_id, control_id=control_id)),
        ("Resume", lambda: client.calling.play_resume(call_id, control_id=control_id)),
        (
            "Volume +2dB",
            lambda: client.calling.play_volume(
                call_id, control_id=control_id, volume=2.0
            ),
        ),
        ("Stop", lambda: client.calling.play_stop(call_id, control_id=control_id)),
    ]:
        try:
            fn()
            print(f"  {action}: OK")
        except SignalWireRestError as e:
            print(f"  {action}: failed ({e.status_code})")

    # 4. Record the call
    rec_control_id = "demo-record-control-id"
    print("\nRecording call...")
    try:
        client.calling.record(
            call_id,
            control_id=rec_control_id,
            audio={"format": "mp3", "beep": True},
        )
        print("  Recording started")
    except SignalWireRestError as e:
        print(f"  Record failed (expected in demo): {e.status_code}")

    # 5. Pause, resume, stop recording
    print("\nControlling recording...")
    for action, fn in [
        (
            "Pause",
            lambda: client.calling.record_pause(call_id, control_id=rec_control_id),
        ),
        (
            "Resume",
            lambda: client.calling.record_resume(call_id, control_id=rec_control_id),
        ),
        (
            "Stop",
            lambda: client.calling.record_stop(call_id, control_id=rec_control_id),
        ),
    ]:
        try:
            fn()
            print(f"  {action}: OK")
        except SignalWireRestError as e:
            print(f"  {action}: failed ({e.status_code})")

    # 6. Transcribe the call
    print("\nTranscribing call...")
    try:
        transcribe_control_id = "demo-transcribe-control-id"
        client.calling.transcribe(call_id, control_id=transcribe_control_id)
        print("  Transcription started")
        client.calling.transcribe_stop(call_id, control_id=transcribe_control_id)
        print("  Transcription stopped")
    except SignalWireRestError as e:
        print(f"  Transcribe failed (expected in demo): {e.status_code}")

    # 7. Denoise the call
    print("\nEnabling denoise...")
    try:
        client.calling.denoise(call_id)
        print("  Denoise started")
        client.calling.denoise_stop(call_id)
        print("  Denoise stopped")
    except SignalWireRestError as e:
        print(f"  Denoise failed (expected in demo): {e.status_code}")

    # 8. End the call
    print("\nEnding call...")
    try:
        client.calling.end(call_id, reason="hangup")
        print("  Call ended")
    except SignalWireRestError as e:
        print(f"  End call failed (expected in demo): {e.status_code}")


if __name__ == "__main__":
    main()
