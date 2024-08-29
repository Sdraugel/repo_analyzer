import os
import json
import matplotlib.pyplot as plt
import networkx as nx

class DiagramGenerator:
    def __init__(self, output_file_path):
        self.output_file_path = output_file_path
        self.diagram_output_path = os.path.join('analysis_files', 'qpid_system_diagram.png')
    
    def generate_diagram(self):
        # Load the JSON data from the output file
        with open(self.output_file_path, 'r') as file:
            data = json.load(file)
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Parse the JSON data and add nodes/edges to the graph
        for item in data.get('details', []):
            filename = item['filename']
            description = item['description']
            
            # Example logic to parse and create nodes/edges
            components = filename.split(os.sep)
            for i in range(len(components) - 1):
                G.add_edge(components[i], components[i + 1])
        
        # Generate the layout for the graph
        pos = nx.spring_layout(G)
        
        # Draw the graph
        plt.figure(figsize=(10, 8))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', font_size=10, font_weight='bold')
        
        # Save the diagram
        plt.savefig(self.diagram_output_path)
        plt.close()
        
        return self.diagram_output_path
