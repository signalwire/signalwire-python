#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Example: Using tap and stop_tap virtual helpers

This example shows how to use the new virtual helpers to:
1. Start background call tapping for monitoring and analysis
2. Stream audio over WebSocket or RTP protocols
3. Control tap sessions with start/stop operations
4. Chain tap operations with other actions
"""

import json
from signalwire.core.function_result import FunctionResult


def basic_websocket_tap_example():
    """Simple WebSocket tap for monitoring."""
    print("=== Basic WebSocket Tap Example ===")
    
    result = FunctionResult("Starting call monitoring") \
        .tap("wss://monitoring.company.com/audio-stream") \
        .say("Call monitoring is now active")
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def basic_rtp_tap_example():
    """Basic RTP tap for real-time processing."""
    print("=== Basic RTP Tap Example ===")
    
    result = FunctionResult("Starting RTP monitoring") \
        .tap("rtp://192.168.1.100:5004") \
        .update_global_data({"rtp_monitoring": True})
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def advanced_compliance_monitoring():
    """Advanced compliance monitoring setup."""
    print("=== Advanced Compliance Monitoring ===")
    
    result = FunctionResult("Setting up compliance monitoring") \
        .tap(
            uri="wss://compliance.company.com/secure-stream",
            control_id="compliance_tap_001",
            direction="both",  # Monitor both sides of conversation
            codec="PCMA",
            status_url="https://api.company.com/compliance-events"
        ) \
        .set_metadata({
            "compliance_session": True,
            "agent_id": "agent_123",
            "recording_purpose": "regulatory_compliance"
        }) \
        .say("This call may be monitored for compliance purposes")
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def customer_service_monitoring():
    """Customer service quality monitoring."""
    print("=== Customer Service Monitoring ===")
    
    result = FunctionResult("Initializing quality monitoring") \
        .tap(
            uri="wss://quality.company.com/cs-monitoring",
            control_id="cs_quality_monitor",
            direction="speak",  # Only monitor agent speech
            status_url="https://api.company.com/quality-events"
        ) \
        .update_global_data({
            "quality_monitoring": True,
            "session_start": "2024-01-01T12:00:00Z"
        }) \
        .say("Welcome to customer service. How can I help you today?")
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def real_time_analytics_tap():
    """Real-time analytics with RTP streaming."""
    print("=== Real-Time Analytics Tap ===")
    
    result = FunctionResult("Starting real-time analytics") \
        .tap(
            uri="rtp://analytics.company.com:6000",
            control_id="analytics_stream",
            direction="both",
            codec="PCMU",
            rtp_ptime=30,  # 30ms packetization
            status_url="https://api.company.com/analytics-status"
        ) \
        .set_metadata({
            "analytics_type": "sentiment_analysis",
            "stream_quality": "high",
            "processing_mode": "real_time"
        })
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def stop_tap_examples():
    """Examples of stopping tap sessions."""
    print("=== Stop Tap Examples ===")
    
    # Stop most recent tap
    stop_recent = FunctionResult("Ending monitoring session") \
        .stop_tap() \
        .say("Call monitoring has been stopped")
    
    print("Stop most recent tap:")
    print(json.dumps(stop_recent.to_dict(), indent=2))
    print()
    
    # Stop specific tap by ID
    stop_specific = FunctionResult("Ending compliance monitoring") \
        .stop_tap("compliance_tap_001") \
        .update_global_data({"compliance_session": False}) \
        .say("Compliance monitoring has been deactivated")
    
    print("Stop specific tap:")
    print(json.dumps(stop_specific.to_dict(), indent=2))
    print()


def call_center_workflow():
    """Complete call center monitoring workflow."""
    print("=== Call Center Workflow ===")
    
    # Start monitoring when call begins
    start_monitoring = FunctionResult("Call center session starting") \
        .tap(
            uri="wss://callcenter.company.com/agent-monitoring",
            control_id="agent_monitor_001",
            direction="both",
            status_url="https://api.company.com/callcenter-events"
        ) \
        .set_metadata({
            "agent_id": "agent_456",
            "department": "technical_support",
            "shift": "morning",
            "monitoring_level": "full"
        }) \
        .update_global_data({
            "call_monitored": True,
            "monitor_start_time": "2024-01-01T09:15:00Z"
        }) \
        .say("Thank you for calling technical support. Your call may be monitored for quality assurance.")
    
    print("Start call center monitoring:")
    print(json.dumps(start_monitoring.to_dict(), indent=2))
    print()
    
    # End monitoring when call completes
    end_monitoring = FunctionResult("Ending call session") \
        .stop_tap("agent_monitor_001") \
        .update_global_data({
            "call_monitored": False,
            "monitor_end_time": "2024-01-01T09:35:00Z",
            "call_duration": 1200  # 20 minutes
        }) \
        .set_metadata({"session_complete": True})
    
    print("End call center monitoring:")
    print(json.dumps(end_monitoring.to_dict(), indent=2))
    print()


def security_incident_monitoring():
    """Emergency security incident monitoring."""
    print("=== Security Incident Monitoring ===")
    
    result = FunctionResult("SECURITY ALERT: Activating emergency monitoring") \
        .tap(
            uri="wss://security.company.com/incident-stream",
            control_id="security_incident_001",
            direction="both",
            codec="PCMA",
            status_url="https://api.company.com/security-alerts"
        ) \
        .set_metadata({
            "alert_level": "high",
            "incident_type": "suspicious_activity",
            "security_team_notified": True,
            "escalation_required": True
        }) \
        .update_global_data({
            "security_monitoring": True,
            "incident_active": True
        }) \
        .say("This call is being monitored for security purposes")
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def training_and_coaching():
    """Training and coaching monitoring setup."""
    print("=== Training and Coaching Setup ===")
    
    result = FunctionResult("Setting up training session monitoring") \
        .tap(
            uri="wss://training.company.com/coaching-stream",
            control_id="training_session_001",
            direction="speak",  # Monitor trainee's speech only
            status_url="https://api.company.com/training-events"
        ) \
        .set_metadata({
            "session_type": "sales_training",
            "trainee_id": "trainee_789",
            "trainer_id": "trainer_101",
            "skill_focus": "objection_handling"
        }) \
        .update_global_data({
            "training_active": True,
            "coaching_mode": "live_feedback"
        }) \
        .say("This is a training call. Your performance will be monitored for coaching purposes.")
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def multi_tap_management():
    """Managing multiple tap sessions."""
    print("=== Multi-Tap Management ===")
    
    # Start multiple taps for different purposes
    start_multiple = FunctionResult("Initializing multi-stream monitoring") \
        .tap(
            uri="wss://compliance.company.com/stream",
            control_id="compliance_stream",
            direction="both"
        ) \
        .tap(
            uri="rtp://analytics.company.com:5006",
            control_id="analytics_stream", 
            direction="both",
            codec="PCMA"
        ) \
        .tap(
            uri="wss://quality.company.com/monitoring",
            control_id="quality_stream",
            direction="speak"
        ) \
        .update_global_data({
            "active_streams": ["compliance", "analytics", "quality"],
            "monitoring_level": "comprehensive"
        })
    
    print("Start multiple monitoring streams:")
    print(json.dumps(start_multiple.to_dict(), indent=2))
    print()
    
    # Stop specific streams
    stop_selective = FunctionResult("Reducing monitoring scope") \
        .stop_tap("analytics_stream") \
        .stop_tap("quality_stream") \
        .update_global_data({
            "active_streams": ["compliance"],
            "monitoring_level": "compliance_only"
        }) \
        .say("Monitoring has been reduced to compliance-only")
    
    print("Stop selective monitoring:")
    print(json.dumps(stop_selective.to_dict(), indent=2))
    print()


if __name__ == "__main__":
    print("Tap and Stop Tap Virtual Helper Examples\n")
    
    basic_websocket_tap_example()
    basic_rtp_tap_example()
    advanced_compliance_monitoring()
    customer_service_monitoring()
    real_time_analytics_tap()
    stop_tap_examples()
    call_center_workflow()
    security_incident_monitoring()
    training_and_coaching()
    multi_tap_management()
    
    print("COMPLETE: All tap examples completed")
    print("\nKey Features Demonstrated:")
    print("- WebSocket and RTP tap streaming")
    print("- Compliance and security monitoring")
    print("- Quality assurance and training")
    print("- Real-time analytics integration")
    print("- Multiple concurrent tap sessions")
    print("- Selective tap control and management")
    print("- Status callbacks and metadata tracking")
    print("- Complete workflow integration") 