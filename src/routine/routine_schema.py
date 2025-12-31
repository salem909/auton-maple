"""
JSON-based routine format schema and validation.
Modern replacement for CSV-based routines with visual flow support.
"""

from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, field, asdict
import json


@dataclass
class NodePosition:
    """Visual position of a node in the flow editor."""
    x: float
    y: float


@dataclass
class CommandData:
    """Represents a command within a routine node."""
    type: str  # Command name from command book
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CommandData':
        return cls(
            type=data['type'],
            params=data.get('params', {})
        )


@dataclass
class RoutineNode:
    """Base class for routine flow nodes."""
    id: str
    type: Literal['point', 'label', 'jump', 'setting', 'condition']
    editor_position: NodePosition  # For visual editor
    next: Optional[str] = None  # ID of next node
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RoutineNode':
        pos_data = data['editor_position']
        data['editor_position'] = NodePosition(pos_data['x'], pos_data['y'])
        return cls(**data)


@dataclass
class PointNode(RoutineNode):
    """Node representing a point in the map with commands."""
    game_position: Dict[str, float] = field(default_factory=dict)  # {x, y} in-game coords
    commands: List[CommandData] = field(default_factory=list)
    frequency: int = 1
    skip: bool = False
    adjust: bool = False
    
    def __post_init__(self):
        self.type = 'point'
    
    def to_dict(self) -> Dict:
        result = super().to_dict()
        result['commands'] = [cmd.to_dict() for cmd in self.commands]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PointNode':
        pos_data = data['editor_position']
        data['editor_position'] = NodePosition(pos_data['x'], pos_data['y'])
        data['commands'] = [CommandData.from_dict(cmd) for cmd in data.get('commands', [])]
        return cls(**data)


@dataclass
class LabelNode(RoutineNode):
    """Node representing a label for jumps."""
    label: str = ""
    
    def __post_init__(self):
        self.type = 'label'
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LabelNode':
        pos_data = data['editor_position']
        data['editor_position'] = NodePosition(pos_data['x'], pos_data['y'])
        return cls(**data)


@dataclass
class JumpNode(RoutineNode):
    """Node representing a jump to a label."""
    target_label: str = ""
    frequency: int = 1
    skip: bool = False
    
    def __post_init__(self):
        self.type = 'jump'
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'JumpNode':
        pos_data = data['editor_position']
        data['editor_position'] = NodePosition(pos_data['x'], pos_data['y'])
        return cls(**data)


@dataclass
class SettingNode(RoutineNode):
    """Node representing a setting change."""
    setting_key: str = ""
    setting_value: Any = None
    
    def __post_init__(self):
        self.type = 'setting'
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SettingNode':
        pos_data = data['editor_position']
        data['editor_position'] = NodePosition(pos_data['x'], pos_data['y'])
        return cls(**data)


@dataclass
class RoutineMetadata:
    """Metadata about the routine."""
    name: str = "Untitled Routine"
    description: str = ""
    author: str = ""
    version: str = "1.0"
    map_name: str = ""
    created: str = ""
    modified: str = ""


@dataclass
class RoutineFlow:
    """Complete routine in flow-based format."""
    metadata: RoutineMetadata
    nodes: List[RoutineNode]
    start_node: str  # ID of the starting node
    
    def to_dict(self) -> Dict:
        return {
            'metadata': asdict(self.metadata),
            'nodes': [node.to_dict() for node in self.nodes],
            'start_node': self.start_node
        }
    
    def to_json(self, indent=2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, filepath: str):
        """Save to JSON file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RoutineFlow':
        """Load from dictionary."""
        metadata = RoutineMetadata(**data['metadata'])
        nodes = []
        
        for node_data in data['nodes']:
            node_type = node_data['type']
            if node_type == 'point':
                nodes.append(PointNode.from_dict(node_data))
            elif node_type == 'label':
                nodes.append(LabelNode.from_dict(node_data))
            elif node_type == 'jump':
                nodes.append(JumpNode.from_dict(node_data))
            elif node_type == 'setting':
                nodes.append(SettingNode.from_dict(node_data))
            else:
                nodes.append(RoutineNode.from_dict(node_data))
        
        return cls(
            metadata=metadata,
            nodes=nodes,
            start_node=data['start_node']
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RoutineFlow':
        """Load from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def load(cls, filepath: str) -> 'RoutineFlow':
        """Load from JSON file."""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())
    
    def get_node(self, node_id: str) -> Optional[RoutineNode]:
        """Get node by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def add_node(self, node: RoutineNode):
        """Add a new node to the routine."""
        self.nodes.append(node)
    
    def remove_node(self, node_id: str):
        """Remove a node by ID."""
        self.nodes = [n for n in self.nodes if n.id != node_id]
        # Clean up references
        for node in self.nodes:
            if node.next == node_id:
                node.next = None
    
    def connect_nodes(self, from_id: str, to_id: str):
        """Connect two nodes."""
        from_node = self.get_node(from_id)
        if from_node:
            from_node.next = to_id


# Example routine structure
EXAMPLE_ROUTINE = {
    "metadata": {
        "name": "Dragon Canyon Upper Path 2",
        "description": "Efficient farming route for Dragon Canyon",
        "author": "AutoMaple",
        "version": "1.0",
        "map_name": "Dragon Canyon Upper Path 2",
        "created": "2025-12-31",
        "modified": "2025-12-31"
    },
    "start_node": "start",
    "nodes": [
        {
            "id": "start",
            "type": "point",
            "editor_position": {"x": 100, "y": 100},
            "game_position": {"x": 100, "y": 200},
            "commands": [
                {"type": "buff", "params": {"skill": "wind_booster"}},
                {"type": "attack", "params": {"skill": "arrow_rain"}}
            ],
            "frequency": 1,
            "skip": False,
            "adjust": False,
            "next": "checkpoint_1"
        },
        {
            "id": "checkpoint_1",
            "type": "point",
            "editor_position": {"x": 300, "y": 100},
            "game_position": {"x": 300, "y": 200},
            "commands": [
                {"type": "attack", "params": {"skill": "arrow_platter"}}
            ],
            "frequency": 1,
            "skip": False,
            "adjust": False,
            "next": "checkpoint_2"
        },
        {
            "id": "checkpoint_2",
            "type": "point",
            "editor_position": {"x": 500, "y": 100},
            "game_position": {"x": 500, "y": 150},
            "commands": [
                {"type": "buff", "params": {}},
                {"type": "attack", "params": {"skill": "arrow_stream"}}
            ],
            "frequency": 1,
            "skip": False,
            "adjust": True,
            "next": "loop_back"
        },
        {
            "id": "loop_back",
            "type": "jump",
            "editor_position": {"x": 500, "y": 300},
            "target_label": "main_loop",
            "frequency": 1,
            "skip": False,
            "next": None
        },
        {
            "id": "main_loop",
            "type": "label",
            "editor_position": {"x": 100, "y": 300},
            "label": "main_loop",
            "next": "start"
        }
    ]
}
