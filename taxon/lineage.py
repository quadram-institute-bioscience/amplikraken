class Node:
    def __init__(self, node_id, rank=None, name=None):
        self.node_id = int(node_id)
        self.rank = rank
        self.name = name
        self.children = []

    def __str__(self):
        return f"Node {self.node_id}:{self.rank}:{self.name} with {len(self.children)} children"


class Tree:
    def __init__(self, root_id=0):
        self.root = Node(root_id)
        self.nodes = {root_id: self.root}  # Keep track of nodes by their IDs

    def append_child(self, parent_id, child_id):
        parent_node = self.nodes.get(int(parent_id))
        if parent_node:
            child_node = Node(child_id)
            parent_node.children.append(child_node)
            self.nodes[child_id] = child_node
            return True
        return False

    def print_tree(self, node=None, indent=0):
        if not node:
            node = self.root
        print(' ' * indent + str(node.node_id))
        for child in node.children:
            self.print_tree(child, indent + 2)

    def get_lineage(self, node_id):
        node = self.nodes.get(int(node_id))
        if node is None:
            raise ValueError(f"Node {node_id} not found")

        if node:
            lineage = []
            current_node = node
            while current_node.node_id != self.root.node_id:
                lineage.append(current_node.node_id)
                parent_id = None
                for key, value in self.nodes.items():
                    if current_node in value.children:
                        parent_id = key
                        break
                current_node = self.nodes[parent_id]
            lineage.append(0)  # Add root node ID to the lineage
            lineage.reverse()  # Reverse the lineage to get the path from root to node
            return lineage
        return None



def parse_kraken_db(kraken_db_file, taxid):
     
    tree = None
    last_level = {}
    with open(kraken_db_file, 'r') as file:
        for line in file:
            line = line.strip()
            columns = line.split('\t')
            if len(columns) >= 5:
                percentage = columns[0]
                taxid_str = columns[4]
                rank = columns[3]
                name = columns[5]
                level = int((len(name) - len(name.lstrip())) / 2)
                if tree is None:
                    print("Initializing tree" + taxid_str)
                    tree = Tree(int(taxid_str))
                    
                else:
                    print("Appending child" + taxid_str + " to " + str(last_level[level - 1]))
                    tree.append_child(last_level[level - 1], int(taxid_str))
                
                
                last_level[level] = int(taxid_str)

                # Leves is number of leading spaces of name, divided by 2
                #print(f"{level}\ttaxid: {taxid_str}, rank: {rank}, percentage: {percentage}: name: {name}, ")
    return tree
if __name__=="__main__":
    import sys
    t = parse_kraken_db(sys.argv[1], sys.argv[2])
    t.print_tree()

    node = t.nodes.get(int(sys.argv[2]))
    print(node)
    print(t.get_lineage(sys.argv[2]))