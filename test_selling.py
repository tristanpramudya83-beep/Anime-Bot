#!/usr/bin/env python3
"""
Test script to verify the selling functionality works correctly.
This simulates the selling process without needing to run the Discord bot.
"""

import json
import os
from pathlib import Path

def load_user_characters():
    """Load user characters from JSON file"""
    file_path = Path("user_data/user_characters.json")
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    return data if isinstance(data, dict) else {}
                return {}
        except (json.JSONDecodeError, Exception) as e:
            print(f"[ERROR] Error loading user characters: {e}")
            return {}
    return {}

def save_user_characters(characters_data):
    """Save user characters to JSON file"""
    file_path = Path("user_data/user_characters.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(characters_data, f, indent=2, ensure_ascii=False)

def test_selling_logic():
    """Test the selling logic with different scenarios"""
    print("🧪 Testing Selling Logic...")
    
    # Load current data
    all_characters = load_user_characters()
    user_id = "1307316629897482281"
    
    if user_id not in all_characters:
        print(f"❌ User {user_id} not found in data")
        return
    
    print(f"📊 Current characters for user {user_id}:")
    for char_name, char_data in all_characters[user_id].items():
        print(f"  - {char_name} ({char_data['tier']}): {char_data['count']} units")
    
    # Test Case 1: Sell 1 unit of a character that has 1 unit
    print("\n📝 Test Case 1: Selling 1 unit of 'Yui' (currently has 1 unit)")
    char_name = "Yui"
    quantity = 1
    
    if (user_id in all_characters and 
        char_name in all_characters[user_id] and 
        all_characters[user_id][char_name]['count'] >= quantity):
        
        original_count = all_characters[user_id][char_name]['count']
        print(f"  Original count: {original_count}")
        
        # Reduce count
        all_characters[user_id][char_name]['count'] -= quantity
        new_count = all_characters[user_id][char_name]['count']
        print(f"  New count after reduction: {new_count}")
        
        # Remove character if count reaches 0
        if new_count <= 0:
            del all_characters[user_id][char_name]
            print(f"  ✅ Character '{char_name}' removed from inventory (count reached 0)")
        else:
            print(f"  ✅ Character '{char_name}' count updated to {new_count}")
        
        # Save changes
        save_user_characters(all_characters)
        print(f"  💾 Changes saved successfully")
    else:
        print(f"  ❌ Cannot sell - insufficient quantity or character not found")
    
    # Test Case 2: Try to sell more than available
    print(f"\n📝 Test Case 2: Trying to sell 2 units of 'Erza' (currently has 1 unit)")
    char_name = "Erza"
    quantity = 2
    
    # Reload data after previous test
    all_characters = load_user_characters()
    
    if (user_id in all_characters and 
        char_name in all_characters[user_id] and 
        all_characters[user_id][char_name]['count'] >= quantity):
        print(f"  ❌ This should not happen - validation failed!")
    else:
        available = all_characters[user_id].get(char_name, {}).get('count', 0)
        print(f"  ✅ Correctly prevented sale - requested {quantity} but only {available} available")
    
    # Test Case 3: Sell partial quantity
    print(f"\n📝 Test Case 3: Adding test character with count 5 and selling 2")
    
    # Reload data
    all_characters = load_user_characters()
    
    # Add test character
    test_char = {
        "name": "Test Character",
        "anime": "Test Anime",
        "image": "test.jpg",
        "tier": "R",
        "count": 5
    }
    all_characters[user_id]["Test Character"] = test_char
    save_user_characters(all_characters)
    print(f"  Added test character with count 5")
    
    # Sell 2 units
    char_name = "Test Character"
    quantity = 2
    
    if (user_id in all_characters and 
        char_name in all_characters[user_id] and 
        all_characters[user_id][char_name]['count'] >= quantity):
        
        original_count = all_characters[user_id][char_name]['count']
        all_characters[user_id][char_name]['count'] -= quantity
        new_count = all_characters[user_id][char_name]['count']
        
        if new_count <= 0:
            del all_characters[user_id][char_name]
            print(f"  Character removed")
        else:
            print(f"  Count reduced from {original_count} to {new_count}")
        
        save_user_characters(all_characters)
        print(f"  ✅ Partial sale successful - remaining: {new_count}")
    
    print(f"\n📊 Final state:")
    final_data = load_user_characters()
    for char_name, char_data in final_data[user_id].items():
        print(f"  - {char_name} ({char_data['tier']}): {char_data['count']} units")

if __name__ == "__main__":
    test_selling_logic()