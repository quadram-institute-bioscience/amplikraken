class TaxonNode:
    def __init__(self, node_id, rank=None, name=None):
        self.node_id = int(node_id)
        self.rank = rank
        self.name = name
        self.children = []

    #def __len__(self):
    #    return len(self.children)
    
    def __str__(self):
        return f"{self.node_id}:{self.rank}:{self.name} ({len(self.children)} children)"


class KrakenTree:
    def __init__(self, root_id=0):
        self.root = TaxonNode(root_id)
        self.nodes = {root_id: self.root}  # Keep track of nodes by their IDs

    
    def append_child(self, parent_id, child_id, child_rank=None, child_name=None):
        parent_node = self.nodes.get(int(parent_id))
        if parent_node:
            child_node = TaxonNode(child_id, child_rank, child_name)
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

    def get_all_children_ids(self, node_id):
        node = self.nodes.get(int(node_id))
        if node is None:
            raise ValueError(f"Node {node_id} not found")
        
        children_ids = []
        for child in node.children:
            children_ids.append(child.node_id)
            children_ids.extend(self.get_all_children_ids(child.node_id))
        
        return children_ids

    
    def get_node_by_name(self, name):
        for node_id, node in self.nodes.items():
            if node.name == name:
                return node_id
        return None

    def export_to_newick(self):
        def build_newick(node):
            if not node.children:
                return str(node.node_id)
            else:
                children_newick = [build_newick(child) for child in node.children]
                return f"({','.join(children_newick)}){node.node_id}"

        return build_newick(self.root) + ";"
    
    def find_last_common_ancestor(self, ids):
        if not ids:
            return None
        
        lineages = [self.get_lineage(node_id) for node_id in ids]
        common_ancestors = set(lineages[0])
        
        for lineage in lineages:
            common_ancestors.intersection_update(lineage)
        
        # Find the last common ancestor in the shared path
        last_common_ancestor = None
        for node_id in lineages[0]:
            if node_id in common_ancestors:
                last_common_ancestor = node_id
            else:
                break
        
        return last_common_ancestor



def parse_kraken_db(kraken_db_file):
    tree = None
    last_level = {}
    with open(kraken_db_file, 'r') as file:
        for line in file:
            line = line.strip()
            columns = line.split('\t')
            if len(columns) >= 5:
                #percentage = columns[0]
                taxid_str = columns[4]
                rank = columns[3]
                name = columns[5]
                level = int((len(name) - len(name.lstrip())) / 2)
                name = name.strip()
                if tree is None:
                    print("Initializing tree, root:" + taxid_str)
                    tree = KrakenTree(int(taxid_str))

                else:
                    #print("Appending child " + taxid_str + " to " + str(last_level[level - 1]), file=sys.stderr)
                    tree.append_child(last_level[level - 1], int(taxid_str), rank, name)

                last_level[level] = int(taxid_str)

    return tree


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 lineage.py <kraken_db_inspect_output> <taxid|name>")
        sys.exit(1)


    t = parse_kraken_db(sys.argv[1])
    #t.print_tree()

    try:
        # GOT TAXID?
        taxid = int(sys.argv[2])
        node = t.nodes.get(int(sys.argv[2]))
        print(node)
        for i in t.get_lineage(sys.argv[2]):
            print(i, t.nodes.get(i), sep="\t")
    except ValueError:
        # GOT NAME or FULL STRING?
        name = sys.argv[2]
        data = name.split(" ")
        taxa_ids = []
        if len(data) > 1 and ":" in data[0]:
            # "3:33 1673:1 3:10 1672:2 3:2 1672:2 3:32 1672:1 3:24 1672:4 3:6 45295:7 0:2 45295:5 0:2 45295:1 0:26 3:7 1672:5 1673:4 0:41 |:| 3:23 1673:1 3:84 1672:4 3:24 1672:1 3:32 1672:2 3:2 1672:2 3:10 1673:1 3:18 0:13"
            taxa = {}
            all_taxa_counts = {}
            for d in data:
                if ":" not in d:
                    raise ValueError(f"Invalid data: {d}")
                tax, quant = d.split(":")
                
                if tax in ["|", "A", "0"]:
                    continue
                print(f"{d}\t--- tax: {tax} quant: {quant}")
                taxa[tax] = int(quant) if tax not in taxa else taxa[tax] + int(quant)
                taxa_ids.append(int(tax))
            # Sort taxa len(t.nodes.get(int(tax))
             
            for tax, quant in taxa.items():
                node = t.nodes.get(int(tax))
                    
                print(f"{tax}\t{quant}X\t{node}\t{t.get_lineage(tax)}\t>>\t{t.get_all_children_ids(tax)[:5]+['& '+str(len(t.get_all_children_ids(tax)))] if len(t.get_all_children_ids(tax)) > 5 else t.get_all_children_ids(tax)}")

        else:
            node_id = t.get_node_by_name(name)
            print(node_id, t.nodes.get(node_id), sep="\t")
            for i in t.get_lineage(node_id):
                print(i, t.nodes.get(i), sep="\t")

        print(f"Last common ancestor {taxa_ids}:", t.find_last_common_ancestor(taxa_ids)    )
        print("All childen of last common ancestor 43927:", t.get_all_children_ids(43927))

    print(t.export_to_newick())