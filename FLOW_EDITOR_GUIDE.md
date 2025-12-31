# Visual Flow Editor - User Guide

## 🎨 Overview

The **Visual Flow Editor** is a modern, node-based interface for creating and editing AutoMaple routines. Instead of manually editing CSV files, you can now visually design your farming routes with drag-and-drop nodes and visual connections.

## ✨ Key Features

- 🎯 **Visual Node Editor** - Drag-and-drop interface with canvas
- 🔗 **Connection Lines** - See the execution flow clearly
- 📦 **Multiple Node Types** - Points, Labels, Jumps, Settings
- 💾 **JSON Format** - Modern, structured data format
- 🔄 **Bidirectional Conversion** - CSV ↔ JSON compatibility
- ✅ **Backward Compatible** - Existing CSV routines still work

## 🚀 Getting Started

### Opening the Flow Editor

1. Load a command book first
2. Go to **File → Visual Flow Editor**
3. A new window will open with the node editor

### Creating Your First Routine

1. Click **"+ Point"** to add a movement point
2. Double-click the node to edit coordinates
3. Add more points and connect them
4. Click **"+ Jump"** to create loops
5. Save as JSON using **"Save JSON"** button

## 🎮 Node Types

### Point Node (Green)
Represents a location where the bot will move and execute commands.

**Properties:**
- `game_position` - In-game coordinates (x, y)
- `commands` - List of commands to execute
- `frequency` - Execute every N iterations (default: 1)
- `skip` - Skip first execution (default: false)
- `adjust` - Fine-tune position (default: false)

**Example:**
```json
{
  "id": "farm_spot_1",
  "type": "point",
  "game_position": {"x": 300, "y": 200},
  "commands": [
    {"type": "buff", "params": {}},
    {"type": "attack", "params": {"skill": "arrow_rain"}}
  ],
  "frequency": 1
}
```

### Label Node (Blue)
Creates a reference point for jump statements.

**Properties:**
- `label` - Name of the label

**Example:**
```json
{
  "id": "main_loop_label",
  "type": "label",
  "label": "main_loop"
}
```

### Jump Node (Orange)
Jumps to a specific label, creating loops or branches.

**Properties:**
- `target_label` - Which label to jump to
- `frequency` - Jump every N iterations
- `skip` - Skip first jump

**Example:**
```json
{
  "id": "loop_back",
  "type": "jump",
  "target_label": "main_loop",
  "frequency": 1
}
```

### Setting Node (Purple)
Changes a bot setting during runtime.

**Properties:**
- `setting_key` - Name of the setting
- `setting_value` - New value

## 🖱️ Controls

### Mouse Controls
- **Left Click** - Select a node
- **Click + Drag** - Move selected node
- **Double Click** - Edit node properties (coming soon)
- **Click Empty Space** - Deselect all

### Keyboard Shortcuts
- **Delete** - Delete selected node
- **Ctrl+S** - Save routine

### Toolbar Buttons
- **+ Point** - Add a new point node
- **+ Label** - Add a new label
- **+ Jump** - Add a new jump
- **Delete** - Delete selected node
- **Clear** - Clear entire canvas
- **Save JSON** - Save routine to JSON file
- **Load JSON** - Load routine from JSON file

## 📁 File Formats

### JSON Format (New)
Modern, structured format with full metadata:

```json
{
  "metadata": {
    "name": "Dragon Canyon Upper Path 2",
    "description": "Efficient farming route",
    "author": "AutoMaple",
    "version": "1.0",
    "map_name": "Dragon Canyon Upper Path 2"
  },
  "start_node": "start",
  "nodes": [...]
}
```

### CSV Format (Legacy)
Traditional format, still fully supported:

```csv
*, x=100, y=200
    buff
    attack
@, label=main_loop
>, label=main_loop, frequency=10
```

## 🔄 Converting Between Formats

### CSV to JSON
1. Go to **File → Convert CSV to JSON**
2. Select your CSV routine file
3. Choose where to save the JSON file
4. Done! You can now edit it in the Flow Editor

### JSON to CSV
The system automatically converts JSON to CSV when loading for execution, maintaining full compatibility.

## 💡 Best Practices

### Organizing Your Routine

1. **Start with Labels** - Define your main sections first
2. **Group Related Points** - Keep related farming spots together visually
3. **Use Descriptive IDs** - Name nodes clearly (e.g., "elite_spawn_point")
4. **Add Metadata** - Document your routine in the metadata section

### Visual Layout Tips

1. **Left-to-Right Flow** - Arrange nodes in execution order
2. **Use Grid Spacing** - Align nodes to the background grid
3. **Minimize Crossings** - Keep connection lines clear
4. **Color Coding** - Use node colors to identify types at a glance

### Performance Tips

1. **Use Frequency Wisely** - Don't buff every single iteration
2. **Strategic Adjustments** - Only enable `adjust` where precision matters
3. **Optimize Paths** - Let the A* algorithm find efficient routes
4. **Minimize Jumps** - Too many loops can reduce clarity

## 🐛 Troubleshooting

### "File → Visual Flow Editor" is Disabled
- Make sure you've loaded a command book first
- Check that AutoMaple is not currently running

### Node Won't Move
- Make sure the node is selected (highlighted in gold)
- Click and drag from the node body, not the ports

### Connections Not Showing
- Connections are created automatically based on the `next` property
- Use "Load JSON" to refresh connections after manual edits

### Routine Won't Execute
- Verify all jump targets exist
- Check that coordinates are within map bounds
- Ensure commands are in your loaded command book

## 🔧 Advanced Features

### Manual JSON Editing

You can edit JSON files directly for advanced control:

```json
{
  "id": "complex_point",
  "type": "point",
  "game_position": {"x": 500, "y": 200},
  "commands": [
    {
      "type": "attack",
      "params": {
        "skill": "combo_ability",
        "duration": 5,
        "repeat": 3
      }
    }
  ],
  "next": "next_point_id"
}
```

### Programmatic Generation

You can generate routines programmatically using Python:

```python
from src.routine.routine_schema import RoutineFlow, PointNode, NodePosition

routine = RoutineFlow(
    metadata=RoutineMetadata(name="Generated Routine"),
    nodes=[],
    start_node="node_0"
)

# Add nodes programmatically
for i, (x, y) in enumerate(farming_spots):
    node = PointNode(
        id=f"node_{i}",
        type="point",
        editor_position=NodePosition(i * 200, 100),
        game_position={"x": x, "y": y},
        commands=[CommandData(type="attack", params={})]
    )
    routine.add_node(node)

routine.save("generated_routine.json")
```

## 🎯 Example Routines

### Simple Linear Farm
```
Point A → Point B → Point C → Jump back to A
```

### Multi-Area Farm with Buff Checks
```
Buff Check → Area 1 (3 points) → Area 2 (2 points) → Loop
```

### Elite Boss Hunter
```
Farm Loop → Elite Detection → Boss Routine → Return to Farm
```

## 📚 API Reference

### RoutineFlow Class
Main container for a routine.

**Methods:**
- `save(filepath)` - Save to JSON file
- `load(filepath)` - Load from JSON file
- `add_node(node)` - Add a node
- `remove_node(node_id)` - Remove a node
- `get_node(node_id)` - Get node by ID

### RoutineConverter Class
Convert between formats.

**Methods:**
- `csv_to_json(csv_path, json_path)` - Convert CSV to JSON
- `json_to_csv(json_path, csv_path)` - Convert JSON to CSV

## 🤝 Contributing

Want to add new node types or features?

1. Add the node class in `routine_schema.py`
2. Update the converter in `routine_converter.py`
3. Add UI support in `flow_editor.py`
4. Update this documentation

## 📄 License

Same as AutoMaple - see main LICENSE file.

## 🆘 Support

- Check existing issues on GitHub
- Join the AutoMaple Discord community
- Review the main README.md for general help

---

**Happy Botting!** 🤖🍁
