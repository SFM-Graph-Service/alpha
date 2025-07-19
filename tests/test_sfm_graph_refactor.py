"""
Test cases for the refactored SFMGraph.add_node() method.
"""
import unittest
from graph.graph import SFMGraph
from models.core_nodes import Actor, Institution, Resource, Process, Flow, ValueFlow, Policy, GovernanceStructure
from models.specialized_nodes import BeliefSystem, TechnologySystem, Indicator, FeedbackLoop, SystemProperty, AnalyticalContext, PolicyInstrument
from models.behavioral_nodes import ValueSystem, CeremonialBehavior, InstrumentalBehavior, ChangeProcess, CognitiveFramework, BehavioralPattern
from models.sfm_enums import ResourceType, InstitutionLayer, FlowNature


class TestSFMGraphRefactor(unittest.TestCase):
    """Test cases for refactored SFMGraph.add_node() method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = SFMGraph()
    
    def test_add_core_nodes(self):
        """Test adding core node types."""
        # Test Actor
        actor = Actor(label="Test Actor")
        result = self.graph.add_node(actor)
        self.assertEqual(result, actor)
        self.assertIn(actor.id, self.graph.actors)
        
        # Test Institution
        institution = Institution(label="Test Institution", layer=InstitutionLayer.FORMAL_RULE)
        result = self.graph.add_node(institution)
        self.assertEqual(result, institution)
        self.assertIn(institution.id, self.graph.institutions)
        
        # Test Resource
        resource = Resource(label="Test Resource", rtype=ResourceType.NATURAL)
        result = self.graph.add_node(resource)
        self.assertEqual(result, resource)
        self.assertIn(resource.id, self.graph.resources)
        
        # Test Process
        process = Process(label="Test Process")
        result = self.graph.add_node(process)
        self.assertEqual(result, process)
        self.assertIn(process.id, self.graph.processes)
        
        # Test Flow
        flow = Flow(label="Test Flow", nature=FlowNature.TRANSFER)
        result = self.graph.add_node(flow)
        self.assertEqual(result, flow)
        self.assertIn(flow.id, self.graph.flows)
    
    def test_add_specialized_nodes(self):
        """Test adding specialized node types."""
        # Test BeliefSystem
        belief = BeliefSystem(label="Test Belief")
        result = self.graph.add_node(belief)
        self.assertEqual(result, belief)
        self.assertIn(belief.id, self.graph.belief_systems)
        
        # Test TechnologySystem
        tech = TechnologySystem(label="Test Technology")
        result = self.graph.add_node(tech)
        self.assertEqual(result, tech)
        self.assertIn(tech.id, self.graph.technology_systems)
        
        # Test Indicator
        indicator = Indicator(label="Test Indicator")
        result = self.graph.add_node(indicator)
        self.assertEqual(result, indicator)
        self.assertIn(indicator.id, self.graph.indicators)
    
    def test_add_behavioral_nodes(self):
        """Test adding behavioral node types."""
        # Test ValueSystem
        value_system = ValueSystem(label="Test Value System")
        result = self.graph.add_node(value_system)
        self.assertEqual(result, value_system)
        self.assertIn(value_system.id, self.graph.value_systems)
        
        # Test CeremonialBehavior
        ceremonial = CeremonialBehavior(label="Test Ceremonial")
        result = self.graph.add_node(ceremonial)
        self.assertEqual(result, ceremonial)
        self.assertIn(ceremonial.id, self.graph.ceremonial_behaviors)
    
    def test_inheritance_handling(self):
        """Test that inheritance is handled correctly."""
        # ValueFlow should go to value_flows, not flows
        value_flow = ValueFlow(label="Test Value Flow")
        result = self.graph.add_node(value_flow)
        self.assertEqual(result, value_flow)
        self.assertIn(value_flow.id, self.graph.value_flows)
        self.assertNotIn(value_flow.id, self.graph.flows)
        
        # Policy should go to policies, not institutions
        policy = Policy(label="Test Policy")
        result = self.graph.add_node(policy)
        self.assertEqual(result, policy)
        self.assertIn(policy.id, self.graph.policies)
        self.assertNotIn(policy.id, self.graph.institutions)
        
        # GovernanceStructure should go to governance_structures
        governance = GovernanceStructure(label="Test Governance")
        result = self.graph.add_node(governance)
        self.assertEqual(result, governance)
        self.assertIn(governance.id, self.graph.governance_structures)
    
    def test_unsupported_node_type(self):
        """Test that unsupported node types raise TypeError."""
        from models.base_nodes import Node
        
        # Create a generic Node (not a specialized type)
        generic_node = Node(label="Generic Node")
        
        with self.assertRaises(TypeError) as context:
            self.graph.add_node(generic_node)
        
        self.assertIn("Unsupported node type", str(context.exception))
    
    def test_multiple_nodes_same_type(self):
        """Test adding multiple nodes of the same type."""
        actor1 = Actor(label="Actor 1")
        actor2 = Actor(label="Actor 2")
        
        self.graph.add_node(actor1)
        self.graph.add_node(actor2)
        
        self.assertEqual(len(self.graph.actors), 2)
        self.assertIn(actor1.id, self.graph.actors)
        self.assertIn(actor2.id, self.graph.actors)
    
    def test_iter_functionality(self):
        """Test that __iter__ works correctly with the registry."""
        actor = Actor(label="Test Actor")
        resource = Resource(label="Test Resource", rtype=ResourceType.NATURAL)
        belief = BeliefSystem(label="Test Belief")
        
        self.graph.add_node(actor)
        self.graph.add_node(resource)
        self.graph.add_node(belief)
        
        nodes = list(self.graph)
        self.assertEqual(len(nodes), 3)
        self.assertIn(actor, nodes)
        self.assertIn(resource, nodes)
        self.assertIn(belief, nodes)
    
    def test_len_functionality(self):
        """Test that __len__ works correctly with the registry."""
        self.assertEqual(len(self.graph), 0)
        
        actor = Actor(label="Test Actor")
        resource = Resource(label="Test Resource", rtype=ResourceType.NATURAL)
        
        self.graph.add_node(actor)
        self.assertEqual(len(self.graph), 1)
        
        self.graph.add_node(resource)
        self.assertEqual(len(self.graph), 2)
    
    def test_clear_functionality(self):
        """Test that clear() works correctly with the registry."""
        actor = Actor(label="Test Actor")
        resource = Resource(label="Test Resource", rtype=ResourceType.NATURAL)
        belief = BeliefSystem(label="Test Belief")
        
        self.graph.add_node(actor)
        self.graph.add_node(resource)
        self.graph.add_node(belief)
        
        self.assertEqual(len(self.graph), 3)
        
        self.graph.clear()
        
        self.assertEqual(len(self.graph), 0)
        self.assertEqual(len(self.graph.actors), 0)
        self.assertEqual(len(self.graph.resources), 0)
        self.assertEqual(len(self.graph.belief_systems), 0)


if __name__ == '__main__':
    unittest.main()