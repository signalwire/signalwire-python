#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Example: Using join_room and sip_refer virtual helpers

This example shows how to use the new virtual helpers to:
1. Join RELAY rooms for multi-party communication
2. Use SIP REFER for call transfers in SIP environments
3. Chain room and SIP operations with other actions
"""

import json
from signalwire.core.function_result import FunctionResult


def basic_room_join_example():
    """Simple room joining with default settings."""
    print("=== Basic Room Join Example ===")
    
    result = FunctionResult("Joining the support team room") \
        .join_room("support_team_room") \
        .say("Welcome to the support team collaboration room")
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def conference_room_example():
    """Conference room setup with metadata tracking."""
    print("=== Conference Room Example ===")
    
    result = FunctionResult("Setting up daily standup meeting") \
        .join_room("daily_standup_room") \
        .set_metadata({
            "meeting_type": "daily_standup",
            "participant_id": "user_123",
            "role": "scrum_master",
            "join_time": "2024-01-01T09:00:00Z"
        }) \
        .update_global_data({
            "meeting_active": True,
            "room_name": "daily_standup_room"
        }) \
        .say("You have joined the daily standup meeting. Please wait for other participants")
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def basic_sip_refer_example():
    """Simple SIP REFER for call transfer."""
    print("=== Basic SIP REFER Example ===")
    
    result = FunctionResult("Transferring your call to support") \
        .say("Please hold while I transfer you to our support specialist") \
        .sip_refer("sip:support@company.com")
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def advanced_sip_refer_example():
    """Advanced SIP REFER with full URI and metadata."""
    print("=== Advanced SIP REFER Example ===")
    
    result = FunctionResult("Transferring to technical support") \
        .set_metadata({
            "transfer_type": "technical_support",
            "priority": "high",
            "original_caller": "+15551234567"
        }) \
        .say("I'm connecting you to our senior technical specialist") \
        .sip_refer("sip:tech-specialist@pbx.company.com:5060") \
        .update_global_data({
            "transfer_completed": True,
            "transfer_destination": "tech-specialist@pbx.company.com"
        })
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def customer_service_workflow():
    """Complete customer service workflow with room and SIP operations."""
    print("=== Customer Service Workflow ===")
    
    # Step 1: Join customer service room
    join_service_room = FunctionResult("Connecting to customer service") \
        .join_room("customer_service_room") \
        .set_metadata({
            "service_type": "billing_inquiry",
            "customer_tier": "premium",
            "queue_position": 1
        }) \
        .say("You have been connected to our customer service team")
    
    print("Join service room:")
    print(json.dumps(join_service_room.to_dict(), indent=2))
    print()
    
    # Step 2: Escalate to manager via SIP transfer
    escalate_to_manager = FunctionResult("Escalating to manager") \
        .say("Let me connect you with a manager who can better assist you") \
        .sip_refer("sip:manager@customer-service.company.com") \
        .update_global_data({
            "escalated": True,
            "escalation_reason": "customer_request"
        })
    
    print("Escalate to manager:")
    print(json.dumps(escalate_to_manager.to_dict(), indent=2))
    print()


def multi_party_conference_example():
    """Multi-party conference with external participants."""
    print("=== Multi-Party Conference Example ===")
    
    # Host joins conference room
    host_joins = FunctionResult("Setting up conference call") \
        .join_room("project_kickoff_meeting") \
        .set_metadata({
            "role": "meeting_host",
            "meeting_id": "proj_kick_001",
            "recording": True
        }) \
        .say("Welcome to the project kickoff meeting. We're waiting for other participants")
    
    print("Host joins conference:")
    print(json.dumps(host_joins.to_dict(), indent=2))
    print()
    
    # Add external participant via SIP
    add_external = FunctionResult("Adding external consultant") \
        .say("Now connecting our external consultant") \
        .sip_refer("sip:consultant@partner-company.com") \
        .update_global_data({
            "external_participants": ["consultant@partner-company.com"],
            "meeting_status": "all_participants_connected"
        })
    
    print("Add external participant:")
    print(json.dumps(add_external.to_dict(), indent=2))
    print()


def emergency_escalation_example():
    """Emergency escalation with priority handling."""
    print("=== Emergency Escalation Example ===")
    
    result = FunctionResult("Emergency escalation in progress") \
        .set_metadata({
            "alert_level": "critical",
            "incident_id": "INC-2024-001",
            "escalation_time": "2024-01-01T14:30:00Z"
        }) \
        .join_room("emergency_response_room") \
        .say("Emergency escalation activated. Connecting to response team") \
        .sip_refer("sip:emergency-manager@company.com:5060") \
        .update_global_data({
            "emergency_active": True,
            "response_team_notified": True
        })
    
    print(json.dumps(result.to_dict(), indent=2))
    print()


def sales_team_handoff_example():
    """Sales team handoff from lead qualification to closing."""
    print("=== Sales Team Handoff Example ===")
    
    # Qualify lead in sales room
    qualify_lead = FunctionResult("Connecting to sales qualification team") \
        .join_room("sales_qualification_room") \
        .set_metadata({
            "lead_score": 85,
            "product_interest": "enterprise_plan",
            "budget_qualified": True
        }) \
        .say("Thank you for your interest. Let me connect you with our sales team")
    
    print("Lead qualification:")
    print(json.dumps(qualify_lead.to_dict(), indent=2))
    print()
    
    # Transfer to senior sales via SIP
    transfer_to_senior = FunctionResult("Transferring to senior sales representative") \
        .say("Based on your requirements, I'm connecting you with our senior sales specialist") \
        .sip_refer("sip:senior-sales@company.com") \
        .update_global_data({
            "qualified_lead": True,
            "assigned_to": "senior-sales",
            "handoff_complete": True
        })
    
    print("Transfer to senior sales:")
    print(json.dumps(transfer_to_senior.to_dict(), indent=2))
    print()


def join_conference_examples():
    """Examples using join_conference virtual helper."""
    print("=== Join Conference Examples ===")
    
    # Simple conference join
    simple_conf = FunctionResult("Joining team conference") \
        .join_conference("daily_standup") \
        .say("Welcome to the daily standup conference")
    
    print("Simple conference join:")
    print(json.dumps(simple_conf.to_dict(), indent=2))
    print()
    
    # Advanced conference with recording and callbacks
    advanced_conf = FunctionResult("Setting up recorded conference call") \
        .join_conference(
            name="customer_training_session",
            muted=False,
            beep="onEnter", 
            record="record-from-start",
            max_participants=50,
            region="us-east",
            status_callback="https://api.company.com/conference-events",
            status_callback_event="start end join leave",
            recording_status_callback="https://api.company.com/recording-status"
        ) \
        .set_metadata({
            "session_type": "customer_training",
            "facilitator": "training_team",
            "max_duration": 3600
        })
    
    print("Advanced conference with recording:")
    print(json.dumps(advanced_conf.to_dict(), indent=2))
    print()


if __name__ == "__main__":
    print("Room and SIP Virtual Helper Examples\n")
    
    basic_room_join_example()
    conference_room_example()
    basic_sip_refer_example()
    advanced_sip_refer_example()
    customer_service_workflow()
    multi_party_conference_example()
    emergency_escalation_example()
    sales_team_handoff_example()
    join_conference_examples()
    
    print("COMPLETE: All room and SIP examples completed")
    print("\nKey Features Demonstrated:")
    print("- RELAY room joining for multi-party communication")
    print("- SIP REFER for call transfers in SIP environments")
    print("- Audio conferences with RELAY and CXML calls")
    print("- Conference recording and status callbacks")
    print("- Metadata tracking for participants and transfers")
    print("- Global data management for workflow state")
    print("- Method chaining with other actions")
    print("- Complete workflows for customer service, sales, and emergency response")
    print("- Integration between room collaboration and SIP transfers") 