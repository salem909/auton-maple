"""
Bidirectional converter between CSV and JSON routine formats.
Maintains backward compatibility with existing CSV routines.
"""

import csv
from datetime import datetime
from os.path import splitext, basename
from typing import List, Tuple
from src.routine.routine_schema import (
    RoutineFlow, RoutineMetadata, RoutineNode, PointNode, 
    LabelNode, JumpNode, SettingNode, CommandData, NodePosition
)


class RoutineConverter:
    """Convert between CSV and JSON routine formats."""
    
    @staticmethod
    def csv_to_json(csv_filepath: str, output_filepath: str = None) -> RoutineFlow:
        """
        Convert a CSV routine to JSON flow format.
        
        Args:
            csv_filepath: Path to the CSV file
            output_filepath: Optional path to save JSON file
            
        Returns:
            RoutineFlow object
        """
        routine_name = basename(splitext(csv_filepath)[0])
        metadata = RoutineMetadata(
            name=routine_name,
            description=f"Converted from {basename(csv_filepath)}",
            author="AutoMaple",
            version="1.0",
            created=datetime.now().isoformat(),
            modified=datetime.now().isoformat()
        )
        
        nodes: List[RoutineNode] = []
        node_counter = 0
        previous_node_id = None
        start_node_id = None
        current_point_node = None
        
        # Visual layout parameters
        x_position = 100
        y_position = 100
        x_spacing = 200
        
        with open(csv_filepath, 'r', newline='') as f:
            csv_reader = csv.reader(f, skipinitialspace=True)
            
            for row in csv_reader:
                if not row or not row[0].strip():
                    continue
                
                first_item = row[0].strip()
                
                # Check for indentation (commands under a point)
                if first_item.startswith('    ') or (row[0].startswith(' ') and not first_item):
                    # This is a command for the current point
                    if current_point_node and len(row) > 0:
                        command_name = row[0].strip().lower()
                        params = RoutineConverter._parse_params(row[1:])
                        
                        command = CommandData(
                            type=command_name,
                            params=params
                        )
                        current_point_node.commands.append(command)
                    continue
                
                # Parse the component type
                symbol = first_item.lower()
                params = RoutineConverter._parse_params(row[1:])
                
                node_id = f"node_{node_counter}"
                node_counter += 1
                
                # Create appropriate node type
                if symbol == '*' or symbol == 'point':
                    # Point node
                    x = float(params.get('x', 0))
                    y = float(params.get('y', 0))
                    frequency = int(params.get('frequency', 1))
                    skip = params.get('skip', 'False').lower() == 'true'
                    adjust = params.get('adjust', 'False').lower() == 'true'
                    
                    node = PointNode(
                        id=node_id,
                        type='point',
                        editor_position=NodePosition(x_position, y_position),
                        game_position={'x': x, 'y': y},
                        commands=[],
                        frequency=frequency,
                        skip=skip,
                        adjust=adjust
                    )
                    current_point_node = node
                    nodes.append(node)
                    
                elif symbol == '@' or symbol == 'label':
                    # Label node
                    label_name = params.get('label', f'label_{node_counter}')
                    
                    node = LabelNode(
                        id=node_id,
                        type='label',
                        editor_position=NodePosition(x_position, y_position),
                        label=label_name
                    )
                    current_point_node = None
                    nodes.append(node)
                    
                elif symbol == '>' or symbol == 'jump' or symbol == 'goto':
                    # Jump node
                    target = params.get('label', '')
                    frequency = int(params.get('frequency', 1))
                    skip = params.get('skip', 'False').lower() == 'true'
                    
                    node = JumpNode(
                        id=node_id,
                        type='jump',
                        editor_position=NodePosition(x_position, y_position),
                        target_label=target,
                        frequency=frequency,
                        skip=skip
                    )
                    current_point_node = None
                    nodes.append(node)
                    
                elif symbol == '$' or symbol == 'setting':
                    # Setting node
                    target = params.get('target', '')
                    value = params.get('value', '')
                    
                    node = SettingNode(
                        id=node_id,
                        type='setting',
                        editor_position=NodePosition(x_position, y_position),
                        setting_key=target,
                        setting_value=value
                    )
                    current_point_node = None
                    nodes.append(node)
                else:
                    # Unknown, skip
                    continue
                
                # Connect to previous node
                if previous_node_id is not None and len(nodes) > 1:
                    nodes[-2].next = node_id
                
                if start_node_id is None:
                    start_node_id = node_id
                
                previous_node_id = node_id
                x_position += x_spacing
        
        if not start_node_id and nodes:
            start_node_id = nodes[0].id
        
        routine = RoutineFlow(
            metadata=metadata,
            nodes=nodes,
            start_node=start_node_id or "node_0"
        )
        
        if output_filepath:
            routine.save(output_filepath)
        
        return routine
    
    @staticmethod
    def json_to_csv(json_filepath: str, output_filepath: str = None) -> str:
        """
        Convert a JSON routine to CSV format.
        
        Args:
            json_filepath: Path to the JSON file
            output_filepath: Optional path to save CSV file
            
        Returns:
            CSV content as string
        """
        routine = RoutineFlow.load(json_filepath)
        lines = []
        
        # Build execution order by following next pointers
        visited = set()
        current_id = routine.start_node
        ordered_nodes = []
        
        while current_id and current_id not in visited:
            node = routine.get_node(current_id)
            if not node:
                break
            visited.add(current_id)
            ordered_nodes.append(node)
            current_id = node.next
        
        # Add any unvisited nodes at the end
        for node in routine.nodes:
            if node.id not in visited:
                ordered_nodes.append(node)
        
        # Convert nodes to CSV format
        for node in ordered_nodes:
            if isinstance(node, PointNode):
                # Point line
                args = [
                    '*',
                    f'x={node.game_position["x"]}',
                    f'y={node.game_position["y"]}'
                ]
                if node.frequency != 1:
                    args.append(f'frequency={node.frequency}')
                if node.skip:
                    args.append('skip=True')
                if node.adjust:
                    args.append('adjust=True')
                
                lines.append(', '.join(args))
                
                # Commands
                for cmd in node.commands:
                    if cmd.params:
                        cmd_parts = [f'    {cmd.type}']
                        for key, value in cmd.params.items():
                            cmd_parts.append(f'{key}={value}')
                        lines.append(', '.join(cmd_parts))
                    else:
                        lines.append(f'    {cmd.type}')
                    
            elif isinstance(node, LabelNode):
                lines.append('')  # Empty line before label
                lines.append(f'@, label={node.label}')
                
            elif isinstance(node, JumpNode):
                args = ['>', f'label={node.target_label}']
                if node.frequency != 1:
                    args.append(f'frequency={node.frequency}')
                if node.skip:
                    args.append('skip=True')
                lines.append(', '.join(args))
                
            elif isinstance(node, SettingNode):
                lines.append(f'$, target={node.setting_key}, value={node.setting_value}')
        
        csv_content = '\n'.join(lines) + '\n'
        
        if output_filepath:
            with open(output_filepath, 'w') as f:
                f.write(csv_content)
        
        return csv_content
    
    @staticmethod
    def _parse_params(items: List[str]) -> dict:
        """Parse parameter list from CSV into dictionary."""
        params = {}
        for item in items:
            if '=' in item:
                key, value = item.split('=', 1)
                params[key.strip()] = value.strip()
        return params


# Example usage and testing
if __name__ == '__main__':
    # Example: Convert CSV to JSON
    converter = RoutineConverter()
    
    # Test conversion (would need actual CSV file)
    # routine = converter.csv_to_json('routines/example.csv', 'routines/example.json')
    # print(f"Converted to JSON with {len(routine.nodes)} nodes")
    
    # Test reverse conversion
    # csv_content = converter.json_to_csv('routines/example.json', 'routines/example_converted.csv')
    # print("Converted back to CSV")
    
    print("Routine converter ready!")
