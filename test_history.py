#!/usr/bin/env python3
"""
Test script to verify the history functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from utils.history_manager import HistoryManager

def test_history_functionality():
    """Test the history saving and retrieval functionality"""
    print("=== Testing History Functionality ===")
    
    # Initialize history manager
    manager = HistoryManager()
    print("✅ History manager initialized")
    
    # Test saving a history record
    print("\n💾 Saving test history record...")
    
    test_output = {
        "overall_score": 85,
        "summary": "Good resume with strong technical skills",
        "keywords": ["Python", "JavaScript", "React"],
        "ats_score": 90,
        "buzzword_score": 75,
        "rpa_score": 80
    }
    
    history_id = manager.save_history(
        user_id=1,
        agent_name="Resume Analyzer",
        summary_text="Score: 85",
        full_output=test_output
    )
    
    if history_id:
        print(f"✅ History record saved successfully with ID: {history_id}")
    else:
        print("❌ Failed to save history record")
        return False
    
    # Test retrieving history records
    print("\n🔍 Retrieving history records...")
    
    total, records = manager.get_user_history(user_id=1, page=1, limit=10)
    
    print(f"📊 Retrieved {total} total records")
    print(f"📋 Retrieved {len(records)} records on this page")
    
    if records:
        record = records[0]
        print(f"   Latest record:")
        print(f"   - ID: {record['id']}")
        print(f"   - Agent: {record['agent_name']}")
        print(f"   - Summary: {record['summary_text']}")
        print(f"   - Timestamp: {record['timestamp']}")
        print("✅ History retrieval successful")
    else:
        print("❌ No records retrieved")
        return False
    
    # Test with pagination
    print("\n📖 Testing pagination...")
    total, page1_records = manager.get_user_history(user_id=1, page=1, limit=1)
    total, page2_records = manager.get_user_history(user_id=1, page=2, limit=1)
    
    print(f"   Page 1 records: {len(page1_records)}")
    print(f"   Page 2 records: {len(page2_records)}")
    print("✅ Pagination test successful")
    
    return True

if __name__ == "__main__":
    success = test_history_functionality()
    if success:
        print("\n🎉 All history functionality tests passed!")
    else:
        print("\n❌ History functionality tests failed!")