#!/usr/bin/env python3
"""
Quick test script to verify the Visual Flow Editor implementation.
Run this to test basic functionality without launching the full GUI.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_schema():
    """Test routine schema and data structures."""
    print("Testing routine schema...")
    
    from src.routine.routine_schema import (
        RoutineFlow, RoutineMetadata, PointNode, 
        LabelNode, JumpNode, NodePosition, CommandData
    )
    
    # Create a simple routine
    metadata = RoutineMetadata(
        name="Test Routine",
        description="Testing the schema",
        version="1.0"
    )
    
    routine = RoutineFlow(
        metadata=metadata,
        nodes=[],
        start_node="point1"
    )
    
    # Add a point node
    point = PointNode(
        id="point1",
        type="point",
        editor_position=NodePosition(100, 100),
        game_position={"x": 300, "y": 200},
        commands=[
            CommandData(type="attack", params={"skill": "fireball"})
        ],
        next="label1"
    )
    routine.add_node(point)
    
    # Add a label
    label = LabelNode(
        id="label1",
        type="label",
        editor_position=NodePosition(300, 100),
        label="loop_start",
        next="jump1"
    )
    routine.add_node(label)
    
    # Add a jump
    jump = JumpNode(
        id="jump1",
        type="jump",
        editor_position=NodePosition(500, 100),
        target_label="loop_start"
    )
    routine.add_node(jump)
    
    # Test serialization
    json_str = routine.to_json()
    print(f"✓ Created routine with {len(routine.nodes)} nodes")
    
    # Test deserialization
    loaded = RoutineFlow.from_json(json_str)
    assert len(loaded.nodes) == 3
    assert loaded.metadata.name == "Test Routine"
    print("✓ Serialization/deserialization works")
    
    # Test node retrieval
    node = loaded.get_node("point1")
    assert node is not None
    assert isinstance(node, PointNode)
    print("✓ Node retrieval works")
    
    print("✅ Schema tests passed!\n")
    return True


def test_converter():
    """Test CSV to JSON conversion."""
    print("Testing format converter...")
    
    import tempfile
    from src.routine.routine_converter import RoutineConverter
    
    # Create a test CSV
    csv_content = """*, x=100, y=200
    attack
*, x=300, y=200, frequency=2
    buff
@, label=main_loop
>, label=main_loop
"""
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_path = f.name
    
    try:
        # Convert to JSON
        routine = RoutineConverter.csv_to_json(csv_path)
        print(f"✓ Converted CSV to routine with {len(routine.nodes)} nodes")
        
        # Check nodes
        assert len(routine.nodes) >= 2  # At least 2 points
        assert any(isinstance(n, type(routine.nodes[0])) for n in routine.nodes)
        print("✓ CSV parsing works")
        
        # Convert back to CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name
        
        routine.save(json_path)
        csv_back = RoutineConverter.json_to_csv(json_path)
        
        # Verify basic CSV structure
        assert '*' in csv_back  # Has points
        assert '@' in csv_back  # Has labels
        assert '>' in csv_back  # Has jumps
        print("✓ JSON to CSV conversion works")
        
        # Cleanup
        os.unlink(csv_path)
        os.unlink(json_path)
        
    except Exception as e:
        print(f"❌ Converter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ Converter tests passed!\n")
    return True


def test_example_file():
    """Test loading the example routine."""
    print("Testing example routine file...")
    
    from src.routine.routine_schema import RoutineFlow
    
    try:
        routine = RoutineFlow.load('example_routine.json')
        print(f"✓ Loaded example routine: {routine.metadata.name}")
        print(f"  - Nodes: {len(routine.nodes)}")
        print(f"  - Start node: {routine.start_node}")
        
        # Verify structure
        assert len(routine.nodes) > 0
        assert routine.start_node == "start_point"
        
        # Check node types
        node_types = [n.type for n in routine.nodes]
        assert 'point' in node_types
        assert 'label' in node_types
        assert 'jump' in node_types
        
        print("✅ Example file tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Example file test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test basic integration scenarios."""
    print("Testing integration scenarios...")
    
    from src.routine.routine_schema import RoutineFlow, RoutineMetadata, PointNode, NodePosition, CommandData
    import tempfile
    
    try:
        # Create a routine programmatically
        routine = RoutineFlow(
            metadata=RoutineMetadata(name="Integration Test"),
            nodes=[],
            start_node="node_0"
        )
        
        # Add multiple points
        for i in range(3):
            point = PointNode(
                id=f"node_{i}",
                type="point",
                editor_position=NodePosition(100 + i * 200, 100),
                game_position={"x": 100 + i * 200, "y": 200},
                commands=[CommandData(type="attack", params={})],
                next=f"node_{i+1}" if i < 2 else None
            )
            routine.add_node(point)
        
        # Save and reload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name
        
        routine.save(json_path)
        loaded = RoutineFlow.load(json_path)
        
        assert len(loaded.nodes) == 3
        assert loaded.nodes[0].next == "node_1"
        print("✓ Save/load cycle works")
        
        # Test node removal
        loaded.remove_node("node_1")
        assert len(loaded.nodes) == 2
        print("✓ Node removal works")
        
        # Cleanup
        os.unlink(json_path)
        
        print("✅ Integration tests passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Visual Flow Editor - Test Suite")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Schema", test_schema()))
    results.append(("Converter", test_converter()))
    results.append(("Example File", test_example_file()))
    results.append(("Integration", test_integration()))
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n{passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The implementation is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
