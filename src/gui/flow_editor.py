"""
Visual Flow Editor - Node-based routine editor with drag-and-drop interface.
Provides an intuitive visual way to create and edit bot routines.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Optional, Tuple, Any
import json
from src.routine.routine_schema import (
    RoutineFlow, RoutineNode, PointNode, LabelNode, 
    JumpNode, SettingNode, NodePosition, RoutineMetadata
)
from src.common import config


class FlowNode:
    """Visual representation of a routine node on the canvas."""
    
    # Node dimensions and styling
    WIDTH = 180
    HEIGHT = 80
    MINI_HEIGHT = 40
    HEADER_HEIGHT = 25
    PORT_RADIUS = 6
    
    # Colors
    COLORS = {
        'point': '#4CAF50',
        'label': '#2196F3',
        'jump': '#FF9800',
        'setting': '#9C27B0',
        'default': '#607D8B'
    }
    
    def __init__(self, canvas: tk.Canvas, node_data: RoutineNode, x: float, y: float):
        self.canvas = canvas
        self.node_data = node_data
        self.x = x
        self.y = y
        
        # Canvas items
        self.rect = None
        self.header_rect = None
        self.title_text = None
        self.content_text = None
        self.input_port = None
        self.output_port = None
        
        # Connection lines
        self.connections = []  # Lines connecting to other nodes
        
        self.draw()
    
    def draw(self):
        """Draw the node on the canvas."""
        color = self.COLORS.get(self.node_data.type, self.COLORS['default'])
        
        # Determine height based on content
        height = self.HEIGHT
        if isinstance(self.node_data, LabelNode) or isinstance(self.node_data, JumpNode):
            height = self.MINI_HEIGHT
        
        # Main rectangle
        self.rect = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.WIDTH, self.y + height,
            fill='white',
            outline=color,
            width=2,
            tags=('node', f'node_{self.node_data.id}')
        )
        
        # Header
        self.header_rect = self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.WIDTH, self.y + self.HEADER_HEIGHT,
            fill=color,
            outline='',
            tags=('node', f'node_{self.node_data.id}', 'header')
        )
        
        # Title
        title = self._get_title()
        self.title_text = self.canvas.create_text(
            self.x + self.WIDTH / 2, self.y + self.HEADER_HEIGHT / 2,
            text=title,
            fill='white',
            font=('Arial', 10, 'bold'),
            tags=('node', f'node_{self.node_data.id}', 'text')
        )
        
        # Content
        if height > self.MINI_HEIGHT:
            content = self._get_content()
            self.content_text = self.canvas.create_text(
                self.x + 10, self.y + self.HEADER_HEIGHT + 10,
                text=content,
                fill='#333',
                font=('Arial', 9),
                anchor='nw',
                width=self.WIDTH - 20,
                tags=('node', f'node_{self.node_data.id}', 'text')
            )
        
        # Input port (top)
        self.input_port = self.canvas.create_oval(
            self.x + self.WIDTH / 2 - self.PORT_RADIUS,
            self.y - self.PORT_RADIUS,
            self.x + self.WIDTH / 2 + self.PORT_RADIUS,
            self.y + self.PORT_RADIUS,
            fill=color,
            outline='white',
            width=2,
            tags=('port', 'input_port', f'node_{self.node_data.id}')
        )
        
        # Output port (bottom)
        self.output_port = self.canvas.create_oval(
            self.x + self.WIDTH / 2 - self.PORT_RADIUS,
            self.y + height - self.PORT_RADIUS,
            self.x + self.WIDTH / 2 + self.PORT_RADIUS,
            self.y + height + self.PORT_RADIUS,
            fill=color,
            outline='white',
            width=2,
            tags=('port', 'output_port', f'node_{self.node_data.id}')
        )
    
    def _get_title(self) -> str:
        """Get the display title for this node."""
        if isinstance(self.node_data, PointNode):
            x = self.node_data.game_position.get('x', 0)
            y = self.node_data.game_position.get('y', 0)
            return f"Point ({x}, {y})"
        elif isinstance(self.node_data, LabelNode):
            return f"Label: {self.node_data.label}"
        elif isinstance(self.node_data, JumpNode):
            return f"Jump → {self.node_data.target_label}"
        elif isinstance(self.node_data, SettingNode):
            return f"Setting"
        return self.node_data.type.title()
    
    def _get_content(self) -> str:
        """Get the content text for this node."""
        if isinstance(self.node_data, PointNode):
            lines = []
            if self.node_data.frequency != 1:
                lines.append(f"Freq: {self.node_data.frequency}")
            if self.node_data.adjust:
                lines.append("Adjust: Yes")
            if self.node_data.commands:
                lines.append(f"Commands: {len(self.node_data.commands)}")
            return '\n'.join(lines) if lines else "No commands"
        elif isinstance(self.node_data, SettingNode):
            return f"{self.node_data.setting_key} = {self.node_data.setting_value}"
        return ""
    
    def move(self, dx: float, dy: float):
        """Move the node by delta x and y."""
        self.x += dx
        self.y += dy
        self.canvas.move(f'node_{self.node_data.id}', dx, dy)
        self.node_data.editor_position.x = self.x
        self.node_data.editor_position.y = self.y
    
    def get_output_port_pos(self) -> Tuple[float, float]:
        """Get the position of the output port."""
        coords = self.canvas.coords(self.output_port)
        return ((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2)
    
    def get_input_port_pos(self) -> Tuple[float, float]:
        """Get the position of the input port."""
        coords = self.canvas.coords(self.input_port)
        return ((coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2)
    
    def highlight(self, color: str = '#FFD700'):
        """Highlight the node."""
        self.canvas.itemconfig(self.rect, outline=color, width=3)
    
    def unhighlight(self):
        """Remove highlight."""
        color = self.COLORS.get(self.node_data.type, self.COLORS['default'])
        self.canvas.itemconfig(self.rect, outline=color, width=2)
    
    def delete(self):
        """Remove the node from canvas."""
        self.canvas.delete(f'node_{self.node_data.id}')


class FlowEditorCanvas(tk.Frame):
    """Interactive canvas for visual flow editing."""
    
    def __init__(self, parent, routine_flow: Optional[RoutineFlow] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.routine_flow = routine_flow or self._create_empty_routine()
        self.flow_nodes: Dict[str, FlowNode] = {}
        self.connections: List[int] = []  # Canvas line IDs
        
        # Interaction state
        self.selected_node: Optional[FlowNode] = None
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.connecting = False
        self.connection_start_node: Optional[FlowNode] = None
        self.temp_connection_line = None
        
        self._create_widgets()
        self._setup_bindings()
        self._load_routine()
    
    def _create_empty_routine(self) -> RoutineFlow:
        """Create an empty routine flow."""
        metadata = RoutineMetadata(name="New Routine")
        return RoutineFlow(metadata=metadata, nodes=[], start_node="")
    
    def _create_widgets(self):
        """Create the canvas and controls."""
        # Toolbar
        toolbar = tk.Frame(self, bg='#f0f0f0', height=40)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Button(toolbar, text='+ Point', command=self._add_point_node, 
                 bg='#4CAF50', fg='white', padx=10).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text='+ Label', command=self._add_label_node,
                 bg='#2196F3', fg='white', padx=10).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text='+ Jump', command=self._add_jump_node,
                 bg='#FF9800', fg='white', padx=10).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Label(toolbar, text='|', bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text='Delete', command=self._delete_selected,
                 bg='#f44336', fg='white', padx=10).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text='Clear', command=self._clear_canvas,
                 bg='#9E9E9E', fg='white', padx=10).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Label(toolbar, text='|', bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        tk.Button(toolbar, text='Save JSON', command=self._save_json,
                 bg='#607D8B', fg='white', padx=10).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text='Load JSON', command=self._load_json,
                 bg='#607D8B', fg='white', padx=10).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Canvas with scrollbars
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            bg='#fafafa',
            scrollregion=(0, 0, 2000, 2000),
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)
        
        # Grid background
        self._draw_grid()
        
        # Status bar
        self.status_bar = tk.Label(self, text='Ready', bg='#e0e0e0', anchor='w')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _draw_grid(self, spacing=50):
        """Draw a grid background."""
        width = 2000
        height = 2000
        
        # Vertical lines
        for x in range(0, width, spacing):
            self.canvas.create_line(x, 0, x, height, fill='#e0e0e0', tags='grid')
        
        # Horizontal lines
        for y in range(0, height, spacing):
            self.canvas.create_line(0, y, width, y, fill='#e0e0e0', tags='grid')
        
        self.canvas.tag_lower('grid')
    
    def _setup_bindings(self):
        """Setup mouse and keyboard bindings."""
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.canvas.bind('<B1-Motion>', self._on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_canvas_release)
        self.canvas.bind('<Double-Button-1>', self._on_canvas_double_click)
        
        self.bind('<Delete>', lambda e: self._delete_selected())
        self.bind('<Control-s>', lambda e: self._save_json())
    
    def _load_routine(self):
        """Load routine nodes onto canvas."""
        self.flow_nodes.clear()
        self.canvas.delete('node')
        self.canvas.delete('connection')
        
        for node in self.routine_flow.nodes:
            flow_node = FlowNode(
                self.canvas,
                node,
                node.editor_position.x,
                node.editor_position.y
            )
            self.flow_nodes[node.id] = flow_node
        
        self._redraw_connections()
    
    def _redraw_connections(self):
        """Redraw all connection lines."""
        self.canvas.delete('connection')
        self.connections.clear()
        
        for node_id, flow_node in self.flow_nodes.items():
            if flow_node.node_data.next:
                target_node = self.flow_nodes.get(flow_node.node_data.next)
                if target_node:
                    self._draw_connection(flow_node, target_node)
    
    def _draw_connection(self, from_node: FlowNode, to_node: FlowNode):
        """Draw a connection line between two nodes."""
        x1, y1 = from_node.get_output_port_pos()
        x2, y2 = to_node.get_input_port_pos()
        
        # Curved line for better visibility
        mid_y = (y1 + y2) / 2
        
        line = self.canvas.create_line(
            x1, y1,
            x1, mid_y,
            x2, mid_y,
            x2, y2,
            fill='#666',
            width=2,
            arrow=tk.LAST,
            smooth=True,
            tags='connection'
        )
        self.connections.append(line)
        self.canvas.tag_lower('connection')
        self.canvas.tag_lower('grid')
    
    def _on_canvas_click(self, event):
        """Handle canvas click."""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Check if clicked on a node
        items = self.canvas.find_overlapping(canvas_x-2, canvas_y-2, canvas_x+2, canvas_y+2)
        
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith('node_'):
                    node_id = tag.replace('node_', '')
                    self._select_node(node_id)
                    self.drag_start_x = canvas_x
                    self.drag_start_y = canvas_y
                    self.dragging = True
                    return
        
        # Clicked on empty space
        self._deselect_all()
    
    def _on_canvas_drag(self, event):
        """Handle canvas drag."""
        if self.dragging and self.selected_node:
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            
            dx = canvas_x - self.drag_start_x
            dy = canvas_y - self.drag_start_y
            
            self.selected_node.move(dx, dy)
            self._redraw_connections()
            
            self.drag_start_x = canvas_x
            self.drag_start_y = canvas_y
    
    def _on_canvas_release(self, event):
        """Handle mouse release."""
        self.dragging = False
    
    def _on_canvas_double_click(self, event):
        """Handle double-click for editing."""
        if self.selected_node:
            self._edit_node(self.selected_node)
    
    def _select_node(self, node_id: str):
        """Select a node."""
        self._deselect_all()
        
        if node_id in self.flow_nodes:
            self.selected_node = self.flow_nodes[node_id]
            self.selected_node.highlight()
            self.status_bar.config(text=f'Selected: {self.selected_node._get_title()}')
    
    def _deselect_all(self):
        """Deselect all nodes."""
        if self.selected_node:
            self.selected_node.unhighlight()
        self.selected_node = None
        self.status_bar.config(text='Ready')
    
    def _add_point_node(self):
        """Add a new point node."""
        node_id = f"node_{len(self.routine_flow.nodes)}"
        node = PointNode(
            id=node_id,
            type='point',
            editor_position=NodePosition(100, 100 + len(self.routine_flow.nodes) * 100),
            game_position={'x': 0, 'y': 0},
            commands=[]
        )
        self.routine_flow.add_node(node)
        
        flow_node = FlowNode(self.canvas, node, node.editor_position.x, node.editor_position.y)
        self.flow_nodes[node_id] = flow_node
        
        self.status_bar.config(text='Added Point node - Double-click to edit')
    
    def _add_label_node(self):
        """Add a new label node."""
        node_id = f"node_{len(self.routine_flow.nodes)}"
        node = LabelNode(
            id=node_id,
            type='label',
            editor_position=NodePosition(100, 100 + len(self.routine_flow.nodes) * 100),
            label=f"label_{len(self.routine_flow.nodes)}"
        )
        self.routine_flow.add_node(node)
        
        flow_node = FlowNode(self.canvas, node, node.editor_position.x, node.editor_position.y)
        self.flow_nodes[node_id] = flow_node
        
        self.status_bar.config(text='Added Label node')
    
    def _add_jump_node(self):
        """Add a new jump node."""
        node_id = f"node_{len(self.routine_flow.nodes)}"
        node = JumpNode(
            id=node_id,
            type='jump',
            editor_position=NodePosition(100, 100 + len(self.routine_flow.nodes) * 100),
            target_label=""
        )
        self.routine_flow.add_node(node)
        
        flow_node = FlowNode(self.canvas, node, node.editor_position.x, node.editor_position.y)
        self.flow_nodes[node_id] = flow_node
        
        self.status_bar.config(text='Added Jump node - Double-click to set target')
    
    def _delete_selected(self):
        """Delete the selected node."""
        if self.selected_node:
            node_id = self.selected_node.node_data.id
            self.selected_node.delete()
            del self.flow_nodes[node_id]
            self.routine_flow.remove_node(node_id)
            self.selected_node = None
            self._redraw_connections()
            self.status_bar.config(text='Node deleted')
    
    def _clear_canvas(self):
        """Clear all nodes."""
        if messagebox.askyesno("Clear Canvas", "Delete all nodes?"):
            self.canvas.delete('node')
            self.canvas.delete('connection')
            self.flow_nodes.clear()
            self.routine_flow.nodes.clear()
            self.status_bar.config(text='Canvas cleared')
    
    def _edit_node(self, flow_node: FlowNode):
        """Open edit dialog for a node."""
        # TODO: Implement proper edit dialog
        messagebox.showinfo("Edit Node", f"Edit dialog for {flow_node._get_title()}\n(Feature coming soon)")
    
    def _save_json(self):
        """Save routine to JSON file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')]
        )
        if filepath:
            try:
                self.routine_flow.save(filepath)
                messagebox.showinfo("Success", f"Saved to {filepath}")
                self.status_bar.config(text=f'Saved: {filepath}')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
    
    def _load_json(self):
        """Load routine from JSON file."""
        filepath = filedialog.askopenfilename(
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')]
        )
        if filepath:
            try:
                self.routine_flow = RoutineFlow.load(filepath)
                self._load_routine()
                messagebox.showinfo("Success", f"Loaded from {filepath}")
                self.status_bar.config(text=f'Loaded: {filepath}')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {e}")


# Standalone window for testing
class FlowEditorWindow(tk.Toplevel):
    """Standalone window for the flow editor."""
    
    def __init__(self, parent=None, routine_flow: Optional[RoutineFlow] = None):
        if parent:
            super().__init__(parent)
        else:
            # Create root window if no parent
            root = tk.Tk()
            root.withdraw()
            super().__init__(root)
        
        self.title("Visual Flow Editor")
        self.geometry("1200x800")
        
        self.editor = FlowEditorCanvas(self, routine_flow)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_close(self):
        """Handle window close."""
        if messagebox.askokcancel("Quit", "Close the editor?"):
            self.destroy()


if __name__ == '__main__':
    # Test the flow editor
    window = FlowEditorWindow()
    window.mainloop()
