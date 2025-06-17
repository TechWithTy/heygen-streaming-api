(Alpha) Interactive Avatar Realtime API

Create real-time interactive avatars for dynamic experiences
Suggest Edits

This alpha-stage API goes a step further by adding interactivity, allowing avatars to not just stream video, but also use the realtime voice model. Note: It's still in early development (alpha), so it’s likely evolving and may have limited access or features.
Getting Started

    NextJS Demo (Frontend): to showcase the frontend implementation of interactive avatars.
    Pipecat Demo (Backend): to demonstrate backend integration for speech processing leverage Pipecat.

Architecture Diagram

Sequence Diagram:

Endpoint

The Interactive Avatar Realtime API is a stateful, server-side, event-driven WebSocket API. The WebSocket connection details are provided at session initialization.

    wss://webrtc-signaling.heygen.io/v2-alpha/interactive-avatar/session/<session_id>

    The WebSocket server address is assigned at the start of each new session and returned in the realtime_endpoint field from the /v1/streaming.new API call.

Event-Based Communication

The WebSocket API follows an event-driven model. Each message is formatted as JSON with the following base structure:

{
  "type": "<event_type>",
  "event_id": "<event_id>"
}

Client Events (Sent to Server)
agent.audio_buffer_append

Appends audio data to the avatar's buffer.

{
  "type": "agent.audio_buffer_append",
  "event_id": "<event_id>",
  "audio": "<base64_encoded_PCM_16bit_24khz_audio>"
}

Note: Limit audio segments to 1-4 seconds for optimal performance.
agent.audio_buffer_commit

Commits buffered audio for immediate processing.

{
  "type": "agent.audio_buffer_commit",
  "event_id": "<event_id>",
  "audio": "<base64_encoded_PCM_16bit_24khz_audio>"
}

agent.audio_buffer_clear

Clears all buffered audio data.

{
  "type": "agent.audio_buffer_clear",
  "event_id": "<event_id>"
}

agent.interrupt

Stops the avatar’s current task and resets it to an idle animation.

{
  "type": "agent.interrupt",
  "event_id": "<event_id>"
}

agent.start_listening

Triggers the avatar's listening animation (only if currently idle).

{
  "type": "agent.start_listening",
  "event_id": "<event_id>"
}

agent.stop_listening

Stops the listening animation (only if currently in listening state).

{
  "type": "agent.stop_listening",
  "event_id": "<event_id>"
}

Feedback & Improvements

This API is under continuous development for improved integration and performance. If you have any feedback, please share it with us!

Updated 21 days ago 