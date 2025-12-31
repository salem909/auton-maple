# 🚀 Quick Start - Visual Flow Editor

## What's New?

Your AutoMaple routine system just got a major upgrade! Instead of manually editing CSV files, you can now create routines visually with a drag-and-drop node editor.

## 📦 What Was Added

✅ **Visual Flow Editor** - Node-based routine editor with drag-and-drop  
✅ **JSON Format** - Modern, structured routine format  
✅ **Format Converter** - Convert CSV ↔ JSON seamlessly  
✅ **Full Compatibility** - All existing CSV routines still work  
✅ **Menu Integration** - New menu options in File menu  

## 🎯 Quick Usage

### Option 1: Visual Editor (Recommended for New Routines)

1. **Launch AutoMaple** and load a command book
2. Go to **File → Visual Flow Editor**
3. Use toolbar to add nodes:
   - Click **"+ Point"** for movement locations
   - Click **"+ Label"** for loop markers
   - Click **"+ Jump"** to create loops
4. Drag nodes to arrange them visually
5. Click **"Save JSON"** when done
6. Load the JSON file normally via **File → Load Routine**

### Option 2: Convert Existing CSV

1. Go to **File → Convert CSV to JSON**
2. Select your CSV routine
3. Save as JSON
4. Now you can edit it in the Visual Flow Editor!

### Option 3: Keep Using CSV

Your existing CSV routines work exactly as before - no changes needed! The new system is completely optional.

## 🎨 Visual Editor Features

### Node Types (Color Coded)
- 🟢 **Green** - Point nodes (movement & commands)
- 🔵 **Blue** - Label nodes (loop targets)
- 🟠 **Orange** - Jump nodes (create loops)
- 🟣 **Purple** - Setting nodes (change bot settings)

### Controls
- **Left Click** - Select node
- **Click + Drag** - Move node
- **Double Click** - Edit (coming soon)
- **Delete Key** - Remove selected node
- **Ctrl+S** - Quick save

## 📚 Documentation

Detailed guides available:
- **FLOW_EDITOR_GUIDE.md** - Complete user manual
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **example_routine.json** - Example JSON file

## ✅ Verification

Run the test suite to verify everything works:
```bash
python test_flow_editor.py
```

All tests should pass with: `🎉 All tests passed!`

## 🎓 Example Workflow

### Creating a Simple Farm Route

1. **Open Flow Editor** (File → Visual Flow Editor)
2. **Add first point**: Click "+ Point"
3. **Edit coordinates**: Double-click node (or edit JSON)
4. **Add more points**: Keep clicking "+ Point"
5. **Create loop**: 
   - Add a Label node at the start
   - Add a Jump node at the end
   - Set jump target to your label
6. **Save**: Click "Save JSON"
7. **Test**: Load the routine and run!

### Visual Layout Example
```
[Start Point] → [Farm Spot 1] → [Farm Spot 2] → [Jump]
     ↑                                              ↓
     └──────────── [Main Loop Label] ←─────────────┘
```

## 🔧 Troubleshooting

### Flow Editor Menu Item Disabled
- Load a command book first
- Make sure AutoMaple is not running

### Can't See Nodes After Loading
- Check the JSON file is valid
- Try scrolling the canvas
- Verify nodes have valid editor_position coordinates

### Routine Won't Execute
- JSON routines are automatically converted to CSV for execution
- Check game coordinates are correct
- Verify commands exist in your command book

## 💡 Tips

1. **Start Simple** - Create a basic 2-3 point route first
2. **Use Grid** - Align nodes to the background grid for organization
3. **Descriptive Names** - Use clear node IDs like "elite_spawn_point"
4. **Save Often** - Use Ctrl+S to save frequently
5. **Version Control** - JSON files work great with Git

## 🎯 Benefits Over CSV

| Feature | CSV | JSON + Flow Editor |
|---------|-----|-------------------|
| Visual editing | ❌ | ✅ |
| See execution flow | ❌ | ✅ |
| Drag & drop | ❌ | ✅ |
| Metadata support | ❌ | ✅ |
| Easy to share | ⚠️ | ✅ |
| Git-friendly | ⚠️ | ✅ |
| Syntax errors | Common | Rare |
| Learning curve | Steep | Gentle |

## 🌟 Next Steps

1. **Try the editor** - Open the Flow Editor and experiment
2. **Convert a routine** - Take an existing CSV and convert it
3. **Create new routine** - Build something from scratch
4. **Share with community** - JSON files are easier to share

## 📞 Need Help?

- Check **FLOW_EDITOR_GUIDE.md** for detailed documentation
- Review **example_routine.json** for format reference
- Ask in the AutoMaple community/Discord

---

**Happy Botting with Visual Routines!** 🤖✨
