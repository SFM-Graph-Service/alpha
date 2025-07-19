"""
unit tests for the SFM data model classes defined in core/sfm_models.py
"""

import unittest
import uuid
import time
from typing import Dict, Any, List, Tuple
from dataclasses import FrozenInstanceError

from models import (
    TimeSlice,
    SpatialUnit,
    Scenario,
    Node,
    Actor,
    Institution,
    Resource,
    Flow,
    Relationship,
    Policy,
    CeremonialBehavior,
    InstrumentalBehavior,
    PolicyInstrument,
    GovernanceStructure,
    ValueFlow,
)
from models.sfm_enums import (
    ValueCategory,
    InstitutionLayer,
    ResourceType,
    FlowNature,
    RelationshipKind,
    PolicyInstrumentType,
)
from graph.graph import SFMGraph

# Test Constants
TEST_TIMEOUT = 5.0  # seconds for performance tests
FLOAT_PRECISION = 7  # decimal places for float comparisons
PROBABILITY_MIN = 0.0
PROBABILITY_MAX = 1.0


class TestDataFactory:
    """Factory class for creating consistent test data across test classes."""
    
    @staticmethod
    def create_test_actor(label: str = "Test Actor", **kwargs: Any) -> Actor:
        """Create a standardized test Actor."""
        defaults: Dict[str, Any] = {
            "description": f"Test actor: {label}",
            "legal_form": "Test Entity",
            "sector": "Test Sector",
            "power_resources": {"economic": 0.5, "political": 0.3},
            "decision_making_capacity": 0.7,
            "institutional_affiliations": [],
            "cognitive_frameworks": [],
            "behavioral_patterns": [],
        }
        defaults.update(kwargs)
        return Actor(label=label, **defaults)
    
    @staticmethod
    def create_test_institution(label: str = "Test Institution", **kwargs: Any) -> Institution:
        """Create a standardized test Institution."""
        defaults: Dict[str, Any] = {
            "description": f"Test institution: {label}",
            "layer": InstitutionLayer.FORMAL_RULE,
            "formal_rules": ["Test rule 1", "Test rule 2"],
            "enforcement_mechanisms": ["Test enforcement"],
            "informal_norms": [],
            "path_dependencies": [],
        }
        defaults.update(kwargs)
        return Institution(label=label, **defaults)
    
    @staticmethod
    def create_test_resource(label: str = "Test Resource", **kwargs: Any) -> Resource:
        """Create a standardized test Resource."""
        defaults: Dict[str, Any] = {
            "description": f"Test resource: {label}",
            "rtype": ResourceType.NATURAL,
            "unit": "units",
        }
        defaults.update(kwargs)
        return Resource(label=label, **defaults)
    
    @staticmethod
    def create_test_relationship(source_id: uuid.UUID, target_id: uuid.UUID, **kwargs: Any) -> Relationship:
        """Create a standardized test Relationship."""
        defaults: Dict[str, Any] = {
            "kind": RelationshipKind.GOVERNS,
            "weight": 0.5,
            "certainty": 0.8,
            "meta": {},
            "time": None,
            "space": None,
            "scenario": None,
        }
        defaults.update(kwargs)
        return Relationship(source_id=source_id, target_id=target_id, **defaults)


class EnumTestCase(unittest.TestCase):
    """Enhanced test suite for enumeration types with comprehensive validation."""

    def test_value_category_enum_completeness(self):
        """Test that ValueCategory enum contains core expected values."""
        # Test core SFM categories are present
        core_categories = {
            "ECONOMIC", "SOCIAL", "ENVIRONMENTAL", "CULTURAL", 
            "INSTITUTIONAL", "TECHNOLOGICAL"
        }
        actual_categories = {item.name for item in ValueCategory}
        
        missing_core = core_categories - actual_categories
        self.assertEqual(
            len(missing_core), 0,
            f"ValueCategory enum missing core categories: {missing_core}"
        )
        
        # Test that we have a reasonable number of categories
        self.assertGreaterEqual(
            len(actual_categories), len(core_categories),
            "ValueCategory should have at least the core SFM categories"
        )

    def test_institution_layer_enum_hierarchy(self):
        """Test InstitutionLayer enum contains Hayden's core institutional layers."""
        # Test core Hayden layers are present
        core_layers = {"FORMAL_RULE", "ORGANIZATION", "INFORMAL_NORM"}
        actual_layers = {layer.name for layer in InstitutionLayer}
        
        missing_core = core_layers - actual_layers
        self.assertEqual(
            len(missing_core), 0,
            f"InstitutionLayer missing Hayden's core layers: {missing_core}"
        )
        
        # Test that we have the core framework
        self.assertGreaterEqual(
            len(actual_layers), len(core_layers),
            "InstitutionLayer should include Hayden's three-layer framework"
        )

    def test_resource_type_enum_coverage(self):
        """Test ResourceType enum covers core resource categories."""
        # Test core resource types are present
        core_types = {"NATURAL", "PRODUCED", "HUMAN", "INFORMATION"}
        actual_types = {rtype.name for rtype in ResourceType}
        
        missing_core = core_types - actual_types
        self.assertEqual(
            len(missing_core), 0,
            f"ResourceType missing core resource types: {missing_core}"
        )
        
        # Test coverage is comprehensive
        self.assertGreaterEqual(
            len(actual_types), len(core_types),
            "ResourceType should cover core resource categories and more"
        )

    def test_flow_nature_enum_completeness(self):
        """Test FlowNature enum contains core flow directions."""
        # Test core flow natures are present
        core_natures = {"INPUT", "OUTPUT", "TRANSFER"}
        actual_natures = {nature.name for nature in FlowNature}
        
        missing_core = core_natures - actual_natures
        self.assertEqual(
            len(missing_core), 0,
            f"FlowNature missing core flow directions: {missing_core}"
        )
        
        # Test basic flow directions are covered
        self.assertGreaterEqual(
            len(actual_natures), len(core_natures),
            "FlowNature should represent core flow directions and more"
        )

    def test_relationship_kind_sfm_coverage(self):
        """Test RelationshipKind enum covers SFM relationship types."""
        # Core SFM relationships
        core_relationships = {
            "GOVERNS", "USES", "PRODUCES", "EXCHANGES_WITH", 
            "LOCATED_IN", "OCCURS_DURING"
        }
        
        # Extended SFM relationships
        extended_relationships = {
            "ENABLES", "INHIBITS", "PRECEDES", "REINFORCES", 
            "UNDERMINES", "AFFECTS", "INFLUENCES", "PARTICIPATES_IN",
            "COLLABORATES_WITH", "COMPETES_WITH", "REGULATES",
            "MONITORS", "IMPLEMENTS", "ENACTS", "MAINTAINS"
        }
        
        expected_relationships = core_relationships | extended_relationships
        actual_relationships = {kind.name for kind in RelationshipKind}
        
        missing_relationships = expected_relationships - actual_relationships
        self.assertEqual(
            len(missing_relationships), 0,
            f"Missing expected relationship kinds: {missing_relationships}"
        )

    def test_enum_string_representations(self):
        """Test that enums have meaningful string representations."""
        test_cases: List[Tuple[Any, str]] = [
            (ValueCategory.ECONOMIC, "ECONOMIC"),
            (InstitutionLayer.FORMAL_RULE, "FORMAL_RULE"),
            (ResourceType.NATURAL, "NATURAL"),
            (FlowNature.INPUT, "INPUT"),
            (RelationshipKind.GOVERNS, "GOVERNS"),
        ]
        
        for enum_value, expected_str in test_cases:
            with self.subTest(enum_value=enum_value):
                self.assertEqual(
                    str(enum_value), f"{enum_value.__class__.__name__}.{expected_str}",
                    f"Enum {enum_value} should have meaningful string representation"
                )

    def test_enum_iteration_consistency(self):
        """Test that enum iteration is consistent and complete."""
        from enum import Enum
        enums_to_test: List[type[Enum]] = [
            ValueCategory, InstitutionLayer, ResourceType, FlowNature, RelationshipKind
        ]
        for enum_class in enums_to_test:
            with self.subTest(enum_class=enum_class):
                # Test that iteration is consistent
                items_list1 = list(enum_class.__members__.values())
                items_list2 = list(enum_class.__members__.values())
                self.assertEqual(
                    items_list1, items_list2,
                    f"Enum {enum_class.__name__} iteration should be consistent"
                )
                # Test that all items are accessible by name
                for item in enum_class:
                    self.assertTrue(
                        hasattr(enum_class, item.name),
                        f"Enum {enum_class.__name__} should have attribute {item.name}"
                    )


class DimensionalEntitiesTestCase(unittest.TestCase):
    """Test suite for dimensional entities (TimeSlice, SpatialUnit, Scenario)."""

    def test_time_slice_immutability(self):
        """Test that TimeSlice is immutable as required for dimensional consistency."""
        time_slice = TimeSlice(label="2025-Q1")
        
        with self.assertRaises(FrozenInstanceError, msg="TimeSlice should be immutable"):
            # Attempting to assign to a frozen dataclass attribute should raise FrozenInstanceError
            setattr(time_slice, "label", "2025-Q2")

    def test_time_slice_label_formats(self):
        """Test various TimeSlice label formats for different temporal granularities."""
        valid_formats = [
            "2025",          # Annual
            "2025-Q1",       # Quarterly  
            "2025-01",       # Monthly
            "2025-01-15",    # Daily
            "FY2025",        # Fiscal year
            "H1-2025",       # Half-year
        ]
        
        for label in valid_formats:
            with self.subTest(label=label):
                time_slice = TimeSlice(label=label)
                self.assertEqual(
                    time_slice.label, label,
                    f"TimeSlice should accept label format: {label}"
                )

    def test_spatial_unit_hierarchical_coding(self):
        """Test SpatialUnit supports hierarchical spatial coding."""
        test_cases = [
            ("US", "United States"),
            ("US-WA", "Washington State"),
            ("US-WA-SEATTLE", "Seattle Metropolitan Area"),
            ("EU", "European Union"),
            ("EU-DE-BER", "Berlin, Germany"),
        ]
        
        for code, name in test_cases:
            with self.subTest(code=code):
                spatial_unit = SpatialUnit(code=code, name=name)
                self.assertEqual(spatial_unit.code, code, "Code should be preserved")
                self.assertEqual(spatial_unit.name, name, "Name should be preserved")

    def test_spatial_unit_immutability(self):
        """Test that SpatialUnit is immutable for referential integrity."""
        spatial_unit = SpatialUnit(code="US-CA", name="California")
        # pylint: disable=assigning-non-slot, attribute-defined-outside-init
        with self.assertRaises(FrozenInstanceError, msg="SpatialUnit should be immutable"):
            # This assignment should fail because SpatialUnit is a frozen dataclass
            spatial_unit.code = "US-NY"  # type: ignore[attr-defined]
    def test_scenario_policy_variants(self):
        """Test Scenario supports various policy and counterfactual scenarios."""
        policy_scenarios = [
            "baseline",
            "carbon_tax_50",
            "renewable_mandate_30",
            "ubi_pilot",
            "no_regulation",
            "maximum_intervention",
        ]
        
        for scenario_label in policy_scenarios:
            with self.subTest(scenario=scenario_label):
                scenario = Scenario(label=scenario_label)
                self.assertEqual(
                    scenario.label, scenario_label,
                    f"Scenario should support policy variant: {scenario_label}"
                )

    def test_scenario_immutability(self):
        """Test that Scenario is immutable for scenario consistency."""
        scenario = Scenario(label="baseline")
        # pylint: disable=assigning-non-slot, attribute-defined-outside-init
        with self.assertRaises(FrozenInstanceError, msg="Scenario should be immutable"):
            scenario.label = "modified"  # type: ignore[attr-defined]


class CoreNodeTestCase(unittest.TestCase):
    """Test suite for core Node class and basic node functionality."""

    def test_node_uuid_generation(self):
        """Test that each Node gets a unique UUID."""
        nodes = [Node(label=f"Node {i}") for i in range(100)]
        node_ids = [node.id for node in nodes]
        
        # Test uniqueness
        self.assertEqual(
            len(node_ids), len(set(node_ids)),
            "All node IDs should be unique"
        )
        
        # Test UUID format
        for node in nodes:
            self.assertIsInstance(
                node.id, uuid.UUID,
                "Node ID should be a valid UUID"
            )

    def test_node_iterator_protocol(self):
        """Test that Node implements iterator protocol for attribute access."""
        node = Node(
            label="Test Node",
            description="Test description",
            meta={"key1": "value1", "key2": "value2"}
        )
        
        # Test iterator returns all attributes (including enhanced fields)
        node_dict = dict(node)
        expected_keys = {
            "label", "description", "id", "meta",
            "version", "created_at", "modified_at", "certainty", 
            "data_quality", "previous_version_id"
        }
        
        self.assertEqual(
            set(node_dict.keys()), expected_keys,
            "Node iterator should return all attributes"
        )
        
        # Test values are correct
        self.assertEqual(node_dict["label"], "Test Node")
        self.assertEqual(node_dict["description"], "Test description")
        self.assertIsInstance(node_dict["id"], uuid.UUID)

    def test_node_metadata_flexibility(self):
        """Test that Node metadata supports flexible key-value storage."""
        meta_data = {
            "source": "survey_2025",
            "confidence": "high",
            "analyst": "team_alpha",
            "version": "1.2.3",
        }
        
        node = Node(label="Meta Test", meta=meta_data)
        
        for key, value in meta_data.items():
            with self.subTest(key=key):
                self.assertEqual(
                    node.meta[key], value,
                    f"Metadata key {key} should preserve value {value}"
                )

    def test_node_metadata_mutability(self):
        """Test that Node metadata can be modified after creation."""
        node = Node(label="Mutable Meta Test", meta={"initial": "value"})
        
        # Test adding new metadata
        node.meta["new_key"] = "new_value"
        self.assertEqual(node.meta["new_key"], "new_value")
        
        # Test modifying existing metadata
        node.meta["initial"] = "modified_value"
        self.assertEqual(node.meta["initial"], "modified_value")


class ActorTestCase(unittest.TestCase):
    """Focused test suite for Actor class and SFM actor functionality."""

    def setUp(self):
        """Set up test fixtures for Actor tests."""
        self.basic_actor = TestDataFactory.create_test_actor()
        self.government_actor = TestDataFactory.create_test_actor(
            label="EPA",
            legal_form="Government Agency",
            sector="Public Administration",
            power_resources={"political": 0.9, "legal": 0.8}
        )
        self.corporate_actor = TestDataFactory.create_test_actor(
            label="MegaCorp",
            legal_form="Corporation",
            sector="Energy",
            power_resources={"economic": 0.8, "political": 0.4}
        )

    def test_actor_inheritance(self):
        """Test that Actor properly inherits from Node."""
        self.assertIsInstance(self.basic_actor, Node, "Actor should inherit from Node")
        self.assertIsInstance(self.basic_actor, Actor, "Actor should be instance of Actor")

    def test_actor_power_resources_modeling(self):
        """Test Actor power resources reflect Hayden's power analysis."""
        # Test government actor power profile
        gov_power = self.government_actor.power_resources
        self.assertGreater(
            gov_power.get("political", 0), 0.5,
            "Government actors should have significant political power"
        )
        
        # Test corporate actor power profile  
        corp_power = self.corporate_actor.power_resources
        self.assertGreater(
            corp_power.get("economic", 0), 0.5,
            "Corporate actors should have significant economic power"
        )

    def test_actor_institutional_affiliations(self):
        """Test Actor institutional affiliations support network analysis."""
        institution_ids = [uuid.uuid4() for _ in range(3)]
        
        actor = TestDataFactory.create_test_actor(
            institutional_affiliations=institution_ids
        )
        
        self.assertEqual(
            len(actor.institutional_affiliations), 3,
            "Actor should maintain institutional affiliations"
        )
        
        for inst_id in institution_ids:
            self.assertIn(
                inst_id, actor.institutional_affiliations,
                f"Institutional affiliation {inst_id} should be preserved"
            )

    def test_actor_cognitive_behavioral_links(self):
        """Test Actor links to cognitive frameworks and behavioral patterns."""
        cognitive_ids = [uuid.uuid4() for _ in range(2)]
        behavioral_ids = [uuid.uuid4() for _ in range(3)]
        
        actor = TestDataFactory.create_test_actor(
            cognitive_frameworks=cognitive_ids,
            behavioral_patterns=behavioral_ids
        )
        
        self.assertEqual(len(actor.cognitive_frameworks), 2)
        self.assertEqual(len(actor.behavioral_patterns), 3)

    def test_actor_decision_making_capacity(self):
        """Test Actor decision-making capacity is properly bounded."""
        test_capacities = [0.0, 0.5, 1.0]
        
        for capacity in test_capacities:
            with self.subTest(capacity=capacity):
                actor = TestDataFactory.create_test_actor(
                    decision_making_capacity=capacity
                )
                self.assertEqual(
                    actor.decision_making_capacity, capacity,
                    f"Decision-making capacity {capacity} should be preserved"
                )

    def test_actor_default_values(self):
        """Test Actor default values are appropriate for SFM analysis."""
        minimal_actor = Actor(label="Minimal Actor")
        
        # Test default collections are empty but not None
        self.assertEqual(len(minimal_actor.power_resources), 0)
        self.assertEqual(len(minimal_actor.institutional_affiliations), 0)
        self.assertEqual(len(minimal_actor.cognitive_frameworks), 0)
        self.assertEqual(len(minimal_actor.behavioral_patterns), 0)
        
        # Test optional fields are None
        self.assertIsNone(minimal_actor.legal_form)
        self.assertIsNone(minimal_actor.sector)
        self.assertIsNone(minimal_actor.decision_making_capacity)


class InstitutionTestCase(unittest.TestCase):
    """Test suite for Institution class and Hayden's institutional framework."""

    def setUp(self):
        """Set up test fixtures for Institution tests."""
        self.formal_rule = TestDataFactory.create_test_institution(
            label="Environmental Protection Act",
            layer=InstitutionLayer.FORMAL_RULE,
            formal_rules=["Emissions standards", "Permit requirements"],
            enforcement_mechanisms=["Fines", "License revocation"]
        )
        
        self.organization = TestDataFactory.create_test_institution(
            label="EPA Regional Office",
            layer=InstitutionLayer.ORGANIZATION,
            formal_rules=["Internal procedures", "Reporting protocols"]
        )
        
        self.informal_norm = TestDataFactory.create_test_institution(
            label="Environmental Stewardship",
            layer=InstitutionLayer.INFORMAL_NORM,
            informal_norms=["Precautionary principle", "Stakeholder engagement"]
        )

    def test_institution_inheritance(self):
        """Test that Institution properly inherits from Node."""
        self.assertIsInstance(self.formal_rule, Node)
        self.assertIsInstance(self.formal_rule, Institution)

    def test_hayden_three_layer_framework(self):
        """Test Institution supports Hayden's three-layer institutional framework."""
        # Test layer assignment
        self.assertEqual(self.formal_rule.layer, InstitutionLayer.FORMAL_RULE)
        self.assertEqual(self.organization.layer, InstitutionLayer.ORGANIZATION)
        self.assertEqual(self.informal_norm.layer, InstitutionLayer.INFORMAL_NORM)
        
        # Test layer-appropriate content
        self.assertGreater(
            len(self.formal_rule.formal_rules), 0,
            "Formal rule institutions should have formal rules"
        )
        self.assertGreater(
            len(self.formal_rule.enforcement_mechanisms), 0,
            "Formal rule institutions should have enforcement mechanisms"
        )
        self.assertGreater(
            len(self.informal_norm.informal_norms), 0,
            "Informal norm institutions should have informal norms"
        )

    def test_institution_enforcement_mechanisms(self):
        """Test Institution enforcement mechanisms support compliance analysis."""
        enforcement_types = [
            "Legal penalties", "Economic sanctions", "Social pressure",
            "Reputation damage", "Exclusion from benefits"
        ]
        
        institution = TestDataFactory.create_test_institution(
            enforcement_mechanisms=enforcement_types
        )
        
        for mechanism in enforcement_types:
            self.assertIn(
                mechanism, institution.enforcement_mechanisms,
                f"Enforcement mechanism {mechanism} should be preserved"
            )

    def test_institution_change_resistance(self):
        """Test Institution change resistance modeling for path dependency analysis."""
        resistance_levels = [0.0, 0.3, 0.7, 1.0]
        
        for resistance in resistance_levels:
            with self.subTest(resistance=resistance):
                institution = TestDataFactory.create_test_institution(
                    change_resistance=resistance
                )
                self.assertEqual(
                    institution.change_resistance, resistance,
                    f"Change resistance {resistance} should be preserved"
                )

    def test_institution_path_dependencies(self):
        """Test Institution path dependencies support historical analysis."""
        dependency_ids = [uuid.uuid4() for _ in range(4)]
        
        institution = TestDataFactory.create_test_institution(
            path_dependencies=dependency_ids
        )
        
        self.assertEqual(len(institution.path_dependencies), 4)
        for dep_id in dependency_ids:
            self.assertIn(dep_id, institution.path_dependencies)

    def test_institution_legitimacy_basis(self):
        """Test Institution legitimacy basis supports Weber's authority types."""
        legitimacy_types = [
            "traditional", "charismatic", "legal-rational",
            "expert", "democratic", "custom"
        ]
        
        for legitimacy_type in legitimacy_types:
            with self.subTest(legitimacy_type=legitimacy_type):
                institution = TestDataFactory.create_test_institution(
                    legitimacy_basis=legitimacy_type
                )
                self.assertEqual(
                    institution.legitimacy_basis, legitimacy_type,
                    f"Legitimacy basis {legitimacy_type} should be preserved"
                )


class PolicyTestCase(unittest.TestCase):
    """Test suite for Policy class as specialized Institution."""

    def test_policy_inheritance_from_institution(self):
        """Test that Policy properly inherits from Institution."""
        policy = Policy(
            label="Carbon Tax Policy",
            authority="Federal Government",
            layer=InstitutionLayer.FORMAL_RULE
        )
        
        self.assertIsInstance(policy, Institution, "Policy should inherit from Institution")
        self.assertIsInstance(policy, Policy, "Policy should be instance of Policy")

    def test_policy_authority_specification(self):
        """Test Policy authority field supports governance analysis."""
        authorities = [
            "Federal Government", "State Government", "Local Authority",
            "International Organization", "Regulatory Agency"
        ]
        
        for authority in authorities:
            with self.subTest(authority=authority):
                policy = Policy(label=f"Test Policy", authority=authority)
                self.assertEqual(
                    policy.authority, authority,
                    f"Policy authority {authority} should be preserved"
                )

    def test_policy_enforcement_strength(self):
        """Test Policy enforcement strength supports effectiveness analysis."""
        enforcement_levels = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for level in enforcement_levels:
            with self.subTest(enforcement_level=level):
                policy = Policy(
                    label="Test Policy",
                    authority="Test Authority",
                    enforcement=level
                )
                self.assertEqual(
                    policy.enforcement, level,
                    f"Enforcement level {level} should be preserved"
                )

    def test_policy_target_sectors(self):
        """Test Policy target sectors support sectoral analysis."""
        target_sectors = ["Energy", "Transportation", "Manufacturing", "Agriculture"]
        
        policy = Policy(
            label="Multi-Sector Policy",
            authority="Government",
            target_sectors=target_sectors
        )
        
        self.assertEqual(len(policy.target_sectors), 4)
        for sector in target_sectors:
            self.assertIn(
                sector, policy.target_sectors,
                f"Target sector {sector} should be preserved"
            )


class FlowTestCase(unittest.TestCase):
    """Test suite for Flow class and value flow analysis."""

    def setUp(self):
        """Set up test fixtures for Flow tests."""
        from models.sfm_enums import FlowType
        self.material_flow = Flow(
            label="Steel Input",
            nature=FlowNature.INPUT,
            quantity=1000.0,
            unit="tonnes",
            flow_type=FlowType.MATERIAL
        )
        self.energy_flow = Flow(
            label="Electricity Consumption",
            nature=FlowNature.INPUT,
            quantity=500.0,
            unit="MWh",
            flow_type=FlowType.ENERGY
        )

    def test_flow_inheritance(self):
        """Test that Flow properly inherits from Node."""
        self.assertIsInstance(self.material_flow, Node)
        self.assertIsInstance(self.material_flow, Flow)

    def test_flow_nature_classification(self):
        """Test Flow nature supports input-output analysis."""
        natures = [FlowNature.INPUT, FlowNature.OUTPUT, FlowNature.TRANSFER]
        
        for nature in natures:
            with self.subTest(nature=nature):
                flow = Flow(label="Test Flow", nature=nature)
                self.assertEqual(
                    flow.nature, nature,
                    f"Flow nature {nature} should be preserved"
                )

    def test_flow_type_categories(self):
        """Test Flow type supports different flow categories."""
        from models.sfm_enums import FlowType
        flow_types = [
            FlowType.MATERIAL,
            FlowType.ENERGY,
            FlowType.INFORMATION,
            FlowType.FINANCIAL,
            FlowType.SOCIAL
        ]
        for flow_type in flow_types:
            with self.subTest(flow_type=flow_type):
                flow = Flow(label="Test Flow", flow_type=flow_type)
                self.assertEqual(
                    flow.flow_type, flow_type,
                    f"Flow type {flow_type} should be preserved"
                )

    def test_flow_transformation_coefficients(self):
        """Test Flow transformation coefficients support process analysis."""
        flow = Flow(
            label="Process Flow",
            transformation_coefficient=0.85,
            loss_factor=0.15
        )
        
        self.assertEqual(flow.transformation_coefficient, 0.85)
        self.assertEqual(flow.loss_factor, 0.15)
        
        # Test that transformation + loss ≈ 1.0 for mass balance
        total = (flow.transformation_coefficient or 0) + (flow.loss_factor or 0)
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_flow_hayden_value_components(self):
        """Test Flow ceremonial/instrumental value components per Hayden."""
        flow = Flow(
            label="Value Flow",
            ceremonial_component=0.3,
            instrumental_component=0.7
        )
        
        self.assertEqual(flow.ceremonial_component, 0.3)
        self.assertEqual(flow.instrumental_component, 0.7)
        
        # Test that components sum to 1.0 for value decomposition
        total = (flow.ceremonial_component or 0) + (flow.instrumental_component or 0)
        self.assertAlmostEqual(total, 1.0, places=2)


class RelationshipTestCase(unittest.TestCase):
    """Test suite for Relationship class and graph connectivity."""

    def setUp(self):
        """Set up test fixtures for Relationship tests."""
        self.actor_id = uuid.uuid4()
        self.institution_id = uuid.uuid4()
        self.relationship = TestDataFactory.create_test_relationship(
            self.actor_id, self.institution_id
        )

    def test_relationship_uuid_generation(self):
        """Test that Relationship gets unique UUID."""
        relationships = [
            TestDataFactory.create_test_relationship(
                uuid.uuid4(), uuid.uuid4()
            ) for _ in range(50)
        ]
        
        relationship_ids = [rel.id for rel in relationships]
        self.assertEqual(
            len(relationship_ids), len(set(relationship_ids)),
            "All relationship IDs should be unique"
        )

    def test_relationship_kind_semantics(self):
        """Test Relationship kinds support semantic graph analysis."""
        semantic_relationships = [
            (RelationshipKind.GOVERNS, "governance"),
            (RelationshipKind.USES, "resource_utilization"),
            (RelationshipKind.PRODUCES, "production"),
            (RelationshipKind.INFLUENCES, "influence_network"),
            (RelationshipKind.REGULATES, "regulatory_framework"),
        ]
        
        for kind, semantic_context in semantic_relationships:
            with self.subTest(kind=kind):
                rel = TestDataFactory.create_test_relationship(
                    self.actor_id, self.institution_id, kind=kind
                )
                self.assertEqual(
                    rel.kind, kind,
                    f"Relationship kind {kind} should support {semantic_context}"
                )

    def test_relationship_weight_and_certainty(self):
        """Test Relationship weight and certainty support uncertainty analysis."""
        test_cases = [
            (0.0, 0.5),  # No weight, medium certainty
            (0.5, 1.0),  # Medium weight, high certainty
            (1.0, 0.8),  # High weight, high certainty
        ]
        
        for weight, certainty in test_cases:
            with self.subTest(weight=weight, certainty=certainty):
                rel = TestDataFactory.create_test_relationship(
                    self.actor_id, self.institution_id,
                    weight=weight, certainty=certainty
                )
                self.assertEqual(rel.weight, weight)
                self.assertEqual(rel.certainty, certainty)

    def test_relationship_dimensional_context(self):
        """Test Relationship dimensional context (time, space, scenario)."""
        time_slice = TimeSlice(label="2025-Q1")
        spatial_unit = SpatialUnit(code="US-CA", name="California")
        scenario = Scenario(label="baseline")
        
        rel = Relationship(
            source_id=self.actor_id,
            target_id=self.institution_id,
            kind=RelationshipKind.GOVERNS,
            time=time_slice,
            space=spatial_unit,
            scenario=scenario
        )
        
        self.assertEqual(rel.time, time_slice)
        self.assertEqual(rel.space, spatial_unit)
        self.assertEqual(rel.scenario, scenario)

    def test_relationship_metadata_extensibility(self):
        """Test Relationship metadata supports extensible attributes."""
        metadata = {
            "data_source": "expert_survey_2025",
            "confidence_interval": "0.6-0.9",
            "validation_method": "triangulation",
        }
        
        rel = Relationship(
            source_id=self.actor_id,
            target_id=self.institution_id,
            kind=RelationshipKind.INFLUENCES,
            meta=metadata
        )
        
        for key, value in metadata.items():
            self.assertEqual(rel.meta[key], value)


class SFMGraphTestCase(unittest.TestCase):
    """Test suite for SFMGraph class and graph operations."""

    def setUp(self):
        """Set up clean SFMGraph for each test."""
        self.graph = SFMGraph()
        self.graph.name = "Test SFM Graph"
        
        # Create test nodes
        self.test_actor = TestDataFactory.create_test_actor()
        self.test_institution = TestDataFactory.create_test_institution()
        self.test_resource = TestDataFactory.create_test_resource()

    def tearDown(self):
        """Clean up after each test."""
        self.graph.clear()

    def test_graph_initialization(self):
        """Test SFMGraph initializes with proper structure."""
        self.assertIsInstance(self.graph.id, uuid.UUID)
        self.assertEqual(self.graph.name, "Test SFM Graph")
        
        # Test all collections exist and are empty
        expected_collections = [
            'actors', 'institutions', 'resources', 'processes', 'flows',
            'relationships', 'belief_systems', 'technology_systems',
            'indicators', 'policies', 'feedback_loops', 'system_properties'
        ]
        
        for collection_name in expected_collections:
            with self.subTest(collection=collection_name):
                collection = getattr(self.graph, collection_name)
                self.assertIsInstance(collection, dict)
                self.assertEqual(len(collection), 0)

    def test_graph_add_node_type_routing(self):
        """Test SFMGraph routes nodes to correct collections by type."""
        # Test basic node types
        self.graph.add_node(self.test_actor)
        self.graph.add_node(self.test_institution) 
        self.graph.add_node(self.test_resource)
        
        self.assertEqual(len(self.graph.actors), 1)
        self.assertEqual(len(self.graph.institutions), 1)
        self.assertEqual(len(self.graph.resources), 1)
        
        self.assertIn(self.test_actor.id, self.graph.actors)
        self.assertIn(self.test_institution.id, self.graph.institutions)
        self.assertIn(self.test_resource.id, self.graph.resources)

    def test_graph_inheritance_handling(self):
        """Test SFMGraph correctly handles inheritance hierarchies."""
        # Test Policy (inherits from Institution) goes to policies, not institutions
        policy = Policy(label="Test Policy", authority="Government")
        self.graph.add_node(policy)
        
        self.assertEqual(len(self.graph.policies), 1)
        self.assertEqual(len(self.graph.institutions), 0)
        self.assertIn(policy.id, self.graph.policies)
        
        # Test ValueFlow (inherits from Flow) goes to value_flows, not flows
        value_flow = ValueFlow(label="Test Value Flow")
        self.graph.add_node(value_flow)
        
        self.assertEqual(len(self.graph.value_flows), 1)
        self.assertEqual(len(self.graph.flows), 0)
        self.assertIn(value_flow.id, self.graph.value_flows)

    def test_graph_relationship_management(self):
        """Test SFMGraph relationship management functionality."""
        # Add nodes first
        self.graph.add_node(self.test_actor)
        self.graph.add_node(self.test_institution)
        
        # Create and add relationship
        relationship = TestDataFactory.create_test_relationship(
            self.test_actor.id, self.test_institution.id
        )
        self.graph.add_relationship(relationship)
        
        self.assertEqual(len(self.graph.relationships), 1)
        self.assertIn(relationship.id, self.graph.relationships)

    def test_graph_iteration_protocol(self):
        """Test SFMGraph iteration returns all nodes."""
        from typing import List
        nodes: List[Node] = [self.test_actor, self.test_institution, self.test_resource]
        for node in nodes:
            self.graph.add_node(node)
        # Test iteration returns all nodes
        iterated_nodes: List[Node] = list(self.graph)
        self.assertEqual(len(iterated_nodes), 3)
        # Test all nodes are included
        iterated_ids = {node.id for node in iterated_nodes}
        expected_ids = {node.id for node in nodes}
        self.assertEqual(iterated_ids, expected_ids)

    def test_graph_length_calculation(self):
        """Test SFMGraph length calculation includes all node types."""
        from typing import List
        # Start with empty graph
        self.assertEqual(len(self.graph), 0)
        # Add different node types
        nodes_to_add: List[Node] = [
            self.test_actor,
            self.test_institution,
            self.test_resource,
            Policy(label="Test Policy", authority="Gov"),
            ValueFlow(label="Test Value Flow"),
        ]
        for i, node in enumerate(nodes_to_add, 1):
            self.graph.add_node(node)
            self.assertEqual(len(self.graph), i)

    def test_graph_clear_functionality(self):
        """Test SFMGraph clear removes all nodes and relationships."""
        # Add nodes and relationships
        self.graph.add_node(self.test_actor)
        self.graph.add_node(self.test_institution)
        
        relationship = TestDataFactory.create_test_relationship(
            self.test_actor.id, self.test_institution.id
        )
        self.graph.add_relationship(relationship)
        
        # Verify content exists
        self.assertGreater(len(self.graph), 0)
        self.assertGreater(len(self.graph.relationships), 0)
        
        # Clear and verify empty
        self.graph.clear()
        self.assertEqual(len(self.graph), 0)
        self.assertEqual(len(self.graph.relationships), 0)


class SFMBusinessLogicTestCase(unittest.TestCase):
    """Test suite for SFM-specific business logic and domain rules."""

    def setUp(self):
        """Set up test fixtures for SFM business logic tests."""
        self.graph = SFMGraph()
        self.graph.name = "SFM Business Logic Test"

    def test_hayden_institutional_layers_integration(self):
        """Test integration of Hayden's three-layer institutional framework."""
        # Create institutions at each layer
        formal_rule = Institution(
            label="Environmental Protection Act",
            layer=InstitutionLayer.FORMAL_RULE,
            formal_rules=["Emissions standards", "Permit requirements"],
            enforcement_mechanisms=["Fines", "License revocation"]
        )
        
        organization = Institution(
            label="EPA Regional Office",
            layer=InstitutionLayer.ORGANIZATION,
            formal_rules=["Internal procedures", "Reporting protocols"]
        )
        
        informal_norm = Institution(
            label="Environmental Stewardship",
            layer=InstitutionLayer.INFORMAL_NORM,
            informal_norms=["Precautionary principle", "Stakeholder engagement"]
        )
        
        # Add to graph and verify layer-specific properties
        institutions = [formal_rule, organization, informal_norm]
        for institution in institutions:
            self.graph.add_node(institution)
        
        # Verify institutional layer characteristics
        self.assertGreater(len(formal_rule.formal_rules), 0)
        self.assertGreater(len(formal_rule.enforcement_mechanisms), 0)
        self.assertGreater(len(informal_norm.informal_norms), 0)
        
        # Verify layer assignment
        layer_mapping = {
            formal_rule.id: InstitutionLayer.FORMAL_RULE,
            organization.id: InstitutionLayer.ORGANIZATION,
            informal_norm.id: InstitutionLayer.INFORMAL_NORM
        }
        
        for institution in institutions:
            expected_layer = layer_mapping[institution.id]
            self.assertEqual(institution.layer, expected_layer)

    def test_ceremonial_instrumental_dichotomy(self):
        """Test Hayden's ceremonial vs instrumental behavior dichotomy."""
        # Create ceremonial behavior (status quo, resistant to change)
        ceremonial = CeremonialBehavior(
            label="Bureaucratic Red Tape",
            description="Rigid procedures that resist technological change",
            rigidity_level=0.9,
            tradition_strength=0.8,
            resistance_to_change=0.95
        )
        
        # Create instrumental behavior (problem-solving, adaptive)
        instrumental = InstrumentalBehavior(
            label="Adaptive Management",
            description="Flexible problem-solving approach",
            efficiency_measure=0.85,
            adaptability_score=0.9,
            innovation_potential=0.8
        )
        
        self.graph.add_node(ceremonial)
        self.graph.add_node(instrumental)
        
        # Test ceremonial characteristics
        self.assertIsNotNone(ceremonial.rigidity_level)
        self.assertGreater(float(ceremonial.rigidity_level or 0), 0.5)
        self.assertIsNotNone(ceremonial.resistance_to_change)
        self.assertGreater(float(ceremonial.resistance_to_change or 0), 0.5)
        
        # Test instrumental characteristics  
        self.assertIsNotNone(instrumental.efficiency_measure)
        self.assertGreater(float(instrumental.efficiency_measure or 0), 0.5)
        self.assertIsNotNone(instrumental.adaptability_score)
        self.assertGreater(float(instrumental.adaptability_score), 0.5) #type: ignore[none-comparison]
        self.assertGreater(instrumental.innovation_potential, 0.5) #type: ignore[none-comparison]

    def test_value_flow_distributional_analysis(self):
        """Test value flow tracking for distributional impact analysis."""
        # Create actors with different power profiles
        corporation = Actor(
            label="Energy Corporation",
            legal_form="Corporation",
            power_resources={"economic": 0.9, "political": 0.6}
        )
        
        community = Actor(
            label="Local Community", 
            legal_form="Community Organization",
            power_resources={"social": 0.7, "political": 0.3}
        )
        
        # Create value flow with distributional impacts
        value_flow = ValueFlow(
            label="Energy Project Benefits",
            nature=FlowNature.OUTPUT,
            quantity=1000000.0,
            unit="USD",
            value_created=1000000.0,
            value_captured=600000.0,
            beneficiary_actors=[corporation.id, community.id],
            distributional_impact={
                "corporation": 0.7,
                "community": 0.3,
            }
        )
        
        # Add to graph
        for actor in [corporation, community]:
            self.graph.add_node(actor)
        self.graph.add_node(value_flow)
        
        # Test distributional analysis
        total_distribution = sum(value_flow.distributional_impact.values())
        self.assertAlmostEqual(total_distribution, 1.0, places=2)
        
        # Test value accounting
        self.assertIsNotNone(value_flow.value_captured)
        self.assertIsNotNone(value_flow.value_created)
        self.assertLessEqual(value_flow.value_captured, value_flow.value_created) #type: ignore[comparison-overlap]

    def test_policy_instrument_effectiveness_framework(self):
        """Test policy instrument effectiveness measurement framework."""
        # Create different types of policy instruments
        instruments = [
            PolicyInstrument(
                label="Emissions Standards",
                instrument_type=PolicyInstrumentType.REGULATORY,  # Use enum instead of string
                target_behavior="emissions reduction",
                compliance_mechanism="mandatory_standards",
                effectiveness_measure=0.75
            ),
            PolicyInstrument(
                label="Carbon Tax",
                instrument_type=PolicyInstrumentType.ECONOMIC,  # Use enum instead of string",
                target_behavior="carbon pricing",
                compliance_mechanism="price_signals",
                effectiveness_measure=0.65
            ),
            PolicyInstrument(
                label="Green Certification",
                instrument_type=PolicyInstrumentType.VOLUNTARY,  # Use enum instead of string
                target_behavior="sustainable practices", 
                compliance_mechanism="reputation_incentives",
                effectiveness_measure=0.45
            ),
        ]
        
        for instrument in instruments:
            self.graph.add_node(instrument)
        
        # Test instrument type validity (use enum values)
        valid_types = {
            PolicyInstrumentType.REGULATORY,
            PolicyInstrumentType.ECONOMIC,
            PolicyInstrumentType.VOLUNTARY,
            PolicyInstrumentType.INFORMATION,
        }
        for instrument in instruments:
            self.assertIn(instrument.instrument_type, valid_types)
        
        # Test effectiveness bounds
        for instrument in instruments:
            effectiveness = instrument.effectiveness_measure
            self.assertGreaterEqual(effectiveness, 0.0) #type: ignore[none-comparison]
            self.assertLessEqual(effectiveness, 1.0) #type: ignore[none-comparison]

    def test_governance_structure_power_analysis(self):
        """Test governance structure power distribution analysis."""
        governance = GovernanceStructure(
            label="Federal Environmental Governance",
            layer=InstitutionLayer.ORGANIZATION,
            power_distribution={
                "executive": 0.5,
                "legislative": 0.3,
                "judicial": 0.2
            },
            accountability_mechanisms=[
                "congressional_oversight",
                "judicial_review",
                "public_reporting"
            ]
        )
        
        self.graph.add_node(governance)
        
        # Test power distribution sums to 1.0
        total_power = sum(governance.power_distribution.values())
        self.assertAlmostEqual(total_power, 1.0, places=1)
        
        # Test accountability mechanisms exist
        self.assertGreater(len(governance.accountability_mechanisms), 0)

    def test_integrated_sfm_scenario_modeling(self):
        """Test integrated SFM scenario with multiple interacting components."""
        # Create actors
        government = Actor(
            label="Federal Government",
            power_resources={"political": 0.9, "legal": 1.0}
        )
        
        industry = Actor(
            label="Industrial Association",
            power_resources={"economic": 0.8, "political": 0.6}
        )
        
        # Create policy and instruments
        carbon_policy = Policy(
            label="Carbon Pricing Act",
            authority="Federal Government",
            layer=InstitutionLayer.FORMAL_RULE,
            enforcement=0.8
        )
        
        carbon_tax = PolicyInstrument(
            label="Carbon Tax",
            instrument_type=PolicyInstrumentType.ECONOMIC,
            effectiveness_measure=0.7
        )
        
        # Create behavioral responses
        adaptation = InstrumentalBehavior(
            label="Technology Investment",
            efficiency_measure=0.6,
            innovation_potential=0.7
        )
        
        resistance = CeremonialBehavior(
            label="Regulatory Resistance",
            rigidity_level=0.8,
            resistance_to_change=0.9
        )
        
        # Create value flows
        compliance_costs = ValueFlow(
            label="Compliance Costs",
            nature=FlowNature.OUTPUT,
            value_created=-500000.0,  # Cost
            distributional_impact={"industry": 1.0}
        )
        
        # Add all components
        from typing import List
        components: List[Node] = [
            government, industry, carbon_policy, carbon_tax,
            adaptation, resistance, compliance_costs
        ]
        for component in components:
            self.graph.add_node(component)
        
        # Create relationships
        relationships = [
            Relationship(government.id, carbon_policy.id, RelationshipKind.ENACTS),
            Relationship(carbon_policy.id, carbon_tax.id, RelationshipKind.IMPLEMENTS),
            Relationship(carbon_tax.id, industry.id, RelationshipKind.AFFECTS),
            Relationship(industry.id, adaptation.id, RelationshipKind.INFLUENCES),
            Relationship(industry.id, resistance.id, RelationshipKind.INFLUENCES),
        ]
        
        for rel in relationships:
            self.graph.add_relationship(rel)
        
        # Verify integrated scenario
        self.assertEqual(len(self.graph), len(components))
        self.assertEqual(len(self.graph.relationships), len(relationships))
        
        # Verify component categorization
        self.assertEqual(len(self.graph.actors), 2)
        self.assertEqual(len(self.graph.policies), 1)
        self.assertEqual(len(self.graph.policy_instruments), 1)
        self.assertEqual(len(self.graph.instrumental_behaviors), 1)
        self.assertEqual(len(self.graph.ceremonial_behaviors), 1)
        self.assertEqual(len(self.graph.value_flows), 1)


class PerformanceTestCase(unittest.TestCase):
    """Test suite for performance and scalability testing."""

    def test_large_graph_performance(self):
        """Test performance with realistic SFM graph sizes."""
        graph = SFMGraph()
        
        start_time = time.time()
        
        # Create large numbers of nodes
        actors = [TestDataFactory.create_test_actor(f"Actor_{i}") for i in range(100)]
        institutions = [TestDataFactory.create_test_institution(f"Institution_{i}") for i in range(50)]
        resources = [TestDataFactory.create_test_resource(f"Resource_{i}") for i in range(200)]
        
        # Add all nodes
        all_nodes = actors + institutions + resources
        for node in all_nodes:
            graph.add_node(node)
        
        # Test iteration performance
        iteration_start = time.time()
        node_count = sum(1 for _node in graph)  # type: ignore[attr-defined]
        iteration_time = time.time() - iteration_start
        
        total_time = time.time() - start_time
        
        # Performance assertions
        self.assertEqual(node_count, len(all_nodes))
        self.assertLess(total_time, TEST_TIMEOUT, "Large graph operations should complete quickly")
        self.assertLess(iteration_time, 1.0, "Graph iteration should be fast")

    def test_relationship_network_performance(self):
        """Test performance with dense relationship networks."""
        graph = SFMGraph()
        
        # Create nodes
        actors = [TestDataFactory.create_test_actor(f"Actor_{i}") for i in range(20)]
        for actor in actors:
            graph.add_node(actor)
        
        # Create dense relationship network
        start_time = time.time()
        relationship_count = 0
        
        for i, source_actor in enumerate(actors):
            for target_actor in actors[i+1:]:
                rel = TestDataFactory.create_test_relationship(
                    source_actor.id, target_actor.id,
                    kind=RelationshipKind.COLLABORATES_WITH
                )
                graph.add_relationship(rel)
                relationship_count += 1
        
        total_time = time.time() - start_time
        
        # Performance assertions
        expected_relationships = len(actors) * (len(actors) - 1) // 2
        self.assertEqual(len(graph.relationships), expected_relationships)
        self.assertLess(total_time, TEST_TIMEOUT, "Relationship creation should be efficient")

    def test_memory_efficiency(self):
        """Test memory efficiency with many similar nodes."""
        graph = SFMGraph()
        
        # Create many nodes with similar structure
        from typing import List
        nodes: List[Actor] = []
        for i in range(1000):
            node = TestDataFactory.create_test_actor(
                f"Actor_{i}",
                power_resources={},  # Empty dict
                institutional_affiliations=[],  # Empty list
                cognitive_frameworks=[],  # Empty list
                behavioral_patterns=[]  # Empty list
            )
            nodes.append(node)
            graph.add_node(node)
        # Test that empty collections are independent
        nodes[0].institutional_affiliations.append(uuid.uuid4())
        nodes[0].power_resources["test"] = 0.5
        # Other nodes should remain unaffected
        self.assertEqual(len(nodes[1].institutional_affiliations), 0)
        self.assertEqual(len(nodes[1].power_resources), 0)


if __name__ == '__main__':
    # Configure test runner
    unittest.main(
        verbosity=2,
        buffer=True,  # Capture stdout/stderr
        failfast=False,  # Continue after first failure
        warnings='ignore'  # Suppress deprecation warnings
    )
