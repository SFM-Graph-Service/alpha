"""
Unit tests for the SFM data model classes defined in core/sfm_models.py
"""
import unittest
import uuid
from datetime import datetime
from typing import Type, List
from enum import Enum
from models import (
    TimeSlice,
    SpatialUnit,
    Scenario,
    Node,
    Actor,
    Institution,
    Resource,
    Process,
    Flow,
    Relationship,
    BeliefSystem,
    Policy,
    TechnologySystem,
    Indicator,
    AnalyticalContext,
    SystemProperty,
    ValueSystem,
    CeremonialBehavior,
    InstrumentalBehavior,
    PolicyInstrument,
    GovernanceStructure,
    ValueFlow,
    ChangeProcess,
    CognitiveFramework,
    BehavioralPattern,
    TemporalDynamics,
    ValidationRule,
    ModelMetadata,
)
from models.sfm_enums import (
    LegitimacySource,
    TechnologyReadinessLevel,
    ValueCategory,
    InstitutionLayer,
    ResourceType,
    FlowNature,
    RelationshipKind,
    TemporalFunctionType,
    ValidationRuleType,
    FlowType,
    PolicyInstrumentType,
    ChangeType,
    BehaviorPatternType,
    FeedbackPolarity,
    FeedbackType,
    SystemPropertyType,
)
from graph.graph import SFMGraph, NetworkMetrics
from typing import Type
from enum import Enum

class TestEnums(unittest.TestCase):
    """Test suite for the enumeration types in sfm_models.py"""

    def test_value_category_enum(self):
        """Test ValueCategory enum values."""
        self.assertTrue(hasattr(ValueCategory, "ECONOMIC"))
        self.assertTrue(hasattr(ValueCategory, "SOCIAL"))
        self.assertTrue(hasattr(ValueCategory, "ENVIRONMENTAL"))
        self.assertTrue(hasattr(ValueCategory, "CULTURAL"))
        self.assertTrue(hasattr(ValueCategory, "INSTITUTIONAL"))
        self.assertTrue(hasattr(ValueCategory, "TECHNOLOGICAL"))

    def test_institution_layer_enum(self):
        """Test InstitutionLayer enum values."""
        self.assertTrue(hasattr(InstitutionLayer, "FORMAL_RULE"))
        self.assertTrue(hasattr(InstitutionLayer, "ORGANIZATION"))
        self.assertTrue(hasattr(InstitutionLayer, "INFORMAL_NORM"))

    def test_resource_type_enum(self):
        """Test ResourceType enum values."""
        self.assertTrue(hasattr(ResourceType, "NATURAL"))
        self.assertTrue(hasattr(ResourceType, "PRODUCED"))
        self.assertTrue(hasattr(ResourceType, "HUMAN"))
        self.assertTrue(hasattr(ResourceType, "INFORMATION"))

    def test_flow_nature_enum(self):
        """Test FlowNature enum values."""
        self.assertTrue(hasattr(FlowNature, "INPUT"))
        self.assertTrue(hasattr(FlowNature, "OUTPUT"))
        self.assertTrue(hasattr(FlowNature, "TRANSFER"))

    def test_relationship_kind_enum(self):
        """Test RelationshipKind enum values."""
        self.assertTrue(hasattr(RelationshipKind, "GOVERNS"))
        self.assertTrue(hasattr(RelationshipKind, "USES"))
        self.assertTrue(hasattr(RelationshipKind, "PRODUCES"))
        self.assertTrue(hasattr(RelationshipKind, "EXCHANGES_WITH"))
        self.assertTrue(hasattr(RelationshipKind, "LOCATED_IN"))
        self.assertTrue(hasattr(RelationshipKind, "OCCURS_DURING"))
        # New relationship kinds
        self.assertTrue(hasattr(RelationshipKind, "ENABLES"))
        self.assertTrue(hasattr(RelationshipKind, "INHIBITS"))
        self.assertTrue(hasattr(RelationshipKind, "PRECEDES"))
        self.assertTrue(hasattr(RelationshipKind, "REINFORCES"))
        self.assertTrue(hasattr(RelationshipKind, "UNDERMINES"))
        self.assertTrue(hasattr(RelationshipKind, "AFFECTS"))

    def test_all_value_categories(self):
        """Test all ValueCategory enum values exist."""
        expected_categories = [
            "ECONOMIC",
            "SOCIAL",
            "ENVIRONMENTAL",
            "CULTURAL",
            "INSTITUTIONAL",
            "TECHNOLOGICAL",
            "POLITICAL",
            "EDUCATIONAL",
            "HEALTH",
            "SECURITY",
            "INFRASTRUCTURE",
            "LEGAL",
            "ETHICAL",
            "AESTHETIC",
            "RECREATIONAL",
            "SPIRITUAL",
            "DEMOGRAPHIC",
            "SPATIAL",
            "TEMPORAL",
            "INFORMATIONAL",
            "PSYCHOLOGICAL",
            "COMMUNITY",
            "RESOURCE",
            "PERFORMANCE",
            "QUALITY",
            "ACCESSIBILITY",
            "RESILIENCE",
            "INNOVATION",
            "EQUITY",
            "TRANSPARENCY",
            "PARTICIPATION",
            "SUSTAINABILITY",
            "DIVERSITY",
            "COOPERATION",
            "COMPETITIVENESS",
            "MOBILITY",
            "COMMUNICATION",
            "ADAPTATION",
            "INTEGRATION",
            "AUTONOMY",
            "STABILITY",
            "EFFICIENCY",
            "EFFECTIVENESS",
            "ACCOUNTABILITY",
            "LEGITIMACY",
            "CAPACITY",
            "CONNECTIVITY",
            "FLEXIBILITY",
            "SCALABILITY",
            "INTEROPERABILITY",
        ]

        for category_name in expected_categories:
            self.assertTrue(
                hasattr(ValueCategory, category_name),
                f"Missing ValueCategory.{category_name}",
            )

    def test_all_relationship_kinds(self):
        """Test all RelationshipKind enum values exist."""
        # Test a representative sample of new relationship kinds
        new_relationships = [
            "FUNDS",
            "PAYS",
            "OWNS",
            "COMPETES_WITH",
            "SUPPLIES",
            "INFORMS",
            "ADVISES",
            "EDUCATES",
            "SERVES",
            "COLLABORATES_WITH",
            "CONTAINS",
            "CONNECTS",
            "TRANSPORTS",
            "FOLLOWS",
            "TRIGGERS",
            "PROCESSES",
            "MAINTAINS",
            "OPERATES",
            "CONSERVES",
            "DEVELOPS",
        ]

        for rel_name in new_relationships:
            self.assertTrue(
                hasattr(RelationshipKind, rel_name),
                f"Missing RelationshipKind.{rel_name}",
            )

    def test_all_relationship_kinds_comprehensive(self):
        """Test all 100+ RelationshipKind enum values exist."""
        # Get all enum members
        all_members = list(RelationshipKind)

        # Should have 100+ members based on the implementation
        self.assertGreater(len(all_members), 100)

        # Test specific critical ones
        critical_relationships = [
            "GOVERNS",
            "USES",
            "PRODUCES",
            "EXCHANGES_WITH",
            "FUNDS",
            "PAYS",
            "OWNS",
            "COMPETES_WITH",
            "SUPPLIES",
            "INFORMS",
            "ADVISES",
            "EDUCATES",
            "SERVES",
            "COLLABORATES_WITH",
            # ... add more based on actual implementation
        ]

        for rel_name in critical_relationships:
            self.assertTrue(
                hasattr(RelationshipKind, rel_name),
                f"Missing critical RelationshipKind.{rel_name}",
            )

    def test_all_enum_values_unique(self):
        """Test all enums have unique values."""
        enum_classes: List[Type[Enum]] = [
            ValueCategory,
            RelationshipKind,
            InstitutionLayer,
            ResourceType,
            FlowNature,
            FlowType,
            PolicyInstrumentType,
            ChangeType,
            BehaviorPatternType,
            FeedbackPolarity,
            FeedbackType,
            TemporalFunctionType,
            ValidationRuleType,
            SystemPropertyType,
        ]
        
        for enum_class in enum_classes:
            values = [member.value for member in enum_class]
            self.assertEqual(
                len(values),
                len(set(values)),
                f"{enum_class.__name__} has duplicate values",
            )

    def test_enum_string_representations(self):
        """Test that enum values have proper string representations."""
        # Test RelationshipKind string representations
        self.assertEqual(str(RelationshipKind.GOVERNS), "RelationshipKind.GOVERNS")
        self.assertIn("RelationshipKind.USES", repr(RelationshipKind.USES))

        # Test ValueCategory string representations
        self.assertEqual(str(ValueCategory.ECONOMIC), "ValueCategory.ECONOMIC")
        self.assertIn("ValueCategory.SOCIAL", repr(ValueCategory.SOCIAL))

        # Test other enums
        self.assertEqual(str(InstitutionLayer.FORMAL_RULE), "InstitutionLayer.FORMAL_RULE")
        self.assertEqual(str(ResourceType.NATURAL), "ResourceType.NATURAL")
        self.assertEqual(str(FlowNature.INPUT), "FlowNature.INPUT")

    def test_enum_iteration(self):
        """Test that enums can be properly iterated."""
        # Test that we can iterate over all enum values
        relationship_kinds = list(RelationshipKind)
        self.assertGreater(len(relationship_kinds), 10)  # Should have many values

        value_categories = list(ValueCategory)
        self.assertGreater(len(value_categories), 20)  # Should have many categories

        # Test that all members are of correct type
        for kind in relationship_kinds:
            self.assertIsInstance(kind, RelationshipKind)

        for category in value_categories:
            self.assertIsInstance(category, ValueCategory)

    def test_enum_membership_testing(self):
        """Test enum membership testing."""
        # Test RelationshipKind membership
        self.assertIn(RelationshipKind.GOVERNS, RelationshipKind)
        self.assertIn(RelationshipKind.USES, RelationshipKind)
        self.assertIn(RelationshipKind.PRODUCES, RelationshipKind)

        # Test ValueCategory membership
        self.assertIn(ValueCategory.ECONOMIC, ValueCategory)
        self.assertIn(ValueCategory.SOCIAL, ValueCategory)
        self.assertIn(ValueCategory.ENVIRONMENTAL, ValueCategory)

        # Test other enums
        self.assertIn(InstitutionLayer.FORMAL_RULE, InstitutionLayer)
        self.assertIn(ResourceType.NATURAL, ResourceType)
        self.assertIn(FlowNature.TRANSFER, FlowNature)

    def test_enum_comparison_operations(self):
        """Test enum comparison and equality operations."""
        # Test equality
        self.assertEqual(RelationshipKind.GOVERNS, RelationshipKind.GOVERNS)
        self.assertNotEqual(RelationshipKind.GOVERNS, RelationshipKind.USES)

        # Test that different enum types are not equal
        self.assertNotEqual(ResourceType.NATURAL, FlowNature.INPUT)

        # Test identity
        self.assertIs(RelationshipKind.GOVERNS, RelationshipKind.GOVERNS)

    def test_enum_error_conditions(self):
        """Test enum error conditions and invalid access."""
        # Test that accessing non-existent enum members raises AttributeError
        with self.assertRaises(AttributeError):
            _ = getattr(RelationshipKind, 'NONEXISTENT_RELATIONSHIP')

        with self.assertRaises(AttributeError):
            _ = getattr(ValueCategory, 'NONEXISTENT_CATEGORY')

    def test_specific_relationship_kinds_exist(self):
        """Test that specific important relationship kinds exist."""
        critical_relationships = [
            "GOVERNS", "USES", "PRODUCES", "EXCHANGES_WITH", "LOCATED_IN",
            "OCCURS_DURING", "ENABLES", "INHIBITS", "PRECEDES", "REINFORCES",
            "UNDERMINES", "AFFECTS", "INFLUENCES", "DEPENDS_ON", "SUPPORTS",
            "FUNDS", "PAYS", "OWNS", "COMPETES_WITH", "SUPPLIES", "INFORMS",
            "ADVISES", "EDUCATES", "SERVES", "COLLABORATES_WITH", "CONTAINS",
            "CONNECTS", "TRANSPORTS", "FOLLOWS", "TRIGGERS", "PROCESSES",
            "MAINTAINS", "OPERATES", "CONSERVES", "DEVELOPS"
        ]

        for rel_name in critical_relationships:
            self.assertTrue(
                hasattr(RelationshipKind, rel_name),
                f"Missing critical RelationshipKind.{rel_name}"
            )
            # Test that we can actually access the value
            rel_value = getattr(RelationshipKind, rel_name)
            self.assertIsInstance(rel_value, RelationshipKind)

    def test_value_category_completeness(self):
        """Test that ValueCategory enum covers all expected domains."""
        expected_core_categories = [
            "ECONOMIC", "SOCIAL", "ENVIRONMENTAL", "CULTURAL", "INSTITUTIONAL",
            "TECHNOLOGICAL", "POLITICAL", "EDUCATIONAL", "HEALTH", "SECURITY"
        ]

        for category_name in expected_core_categories:
            self.assertTrue(
                hasattr(ValueCategory, category_name),
                f"Missing core ValueCategory.{category_name}"
            )
            # Test that we can access the value
            category_value = getattr(ValueCategory, category_name)
            self.assertIsInstance(category_value, ValueCategory)

    def test_institution_layer_completeness(self):
        """Test InstitutionLayer enum completeness."""
        expected_layers = ["FORMAL_RULE", "ORGANIZATION", "INFORMAL_NORM"]

        for layer_name in expected_layers:
            self.assertTrue(
                hasattr(InstitutionLayer, layer_name),
                f"Missing InstitutionLayer.{layer_name}"
            )

        # Test that we have at least these three core layers (Hayden's framework)
        all_layers = list(InstitutionLayer)
        self.assertGreaterEqual(len(all_layers), 3)

    def test_resource_type_validity(self):
        """Test ResourceType enum validity and completeness."""
        expected_types = ["NATURAL", "PRODUCED", "HUMAN", "INFORMATION"]

        for type_name in expected_types:
            self.assertTrue(
                hasattr(ResourceType, type_name),
                f"Missing ResourceType.{type_name}"
            )

        # Test that all resource types are accessible
        for resource_type in ResourceType:
            self.assertIsInstance(resource_type, ResourceType)

    def test_flow_nature_validity(self):
        """Test FlowNature enum validity."""
        expected_natures = ["INPUT", "OUTPUT", "TRANSFER"]

        for nature_name in expected_natures:
            self.assertTrue(
                hasattr(FlowNature, nature_name),
                f"Missing FlowNature.{nature_name}"
            )

        # Test enum values make sense for SFM context
        all_natures = list(FlowNature)
        self.assertGreaterEqual(len(all_natures), 3)  # At least the core three

    def test_enum_documentation_completeness(self):
        """Test that enum classes have proper documentation."""
        enum_classes: List[Type[Enum]] = [
            ValueCategory, RelationshipKind, InstitutionLayer, ResourceType, FlowNature,
            FlowType, PolicyInstrumentType, ChangeType, BehaviorPatternType,
            FeedbackPolarity, FeedbackType, TemporalFunctionType, ValidationRuleType,
            SystemPropertyType
        ]

        for enum_class in enum_classes:
            # Each enum class should have a docstring or be well-documented through usage
            self.assertIsNotNone(enum_class.__name__)
            self.assertTrue(len(list(enum_class)) > 0, f"{enum_class.__name__} should have members")

    def test_flow_type_enum_completeness(self):
        """Test FlowType enum contains expected flow types."""
        expected_types = ["MATERIAL", "ENERGY", "INFORMATION", "FINANCIAL", "SOCIAL"]

        for flow_type in expected_types:
            self.assertTrue(
                hasattr(FlowType, flow_type),
                f"Missing FlowType.{flow_type}"
            )

        # Test all enum values are accessible
        all_types = list(FlowType)
        self.assertEqual(len(all_types), 5)

    def test_policy_instrument_type_enum_completeness(self):
        """Test PolicyInstrumentType enum contains expected instrument types."""
        expected_types = ["REGULATORY", "ECONOMIC", "VOLUNTARY", "INFORMATION"]

        for instrument_type in expected_types:
            self.assertTrue(
                hasattr(PolicyInstrumentType, instrument_type),
                f"Missing PolicyInstrumentType.{instrument_type}"
            )

        # Test all enum values are accessible
        all_types = list(PolicyInstrumentType)
        self.assertEqual(len(all_types), 4)

    def test_change_type_enum_completeness(self):
        """Test ChangeType enum contains expected change types."""
        expected_types = ["EVOLUTIONARY", "REVOLUTIONARY", "CYCLICAL", "INCREMENTAL"]

        for change_type in expected_types:
            self.assertTrue(
                hasattr(ChangeType, change_type),
                f"Missing ChangeType.{change_type}"
            )

        # Test all enum values are accessible
        all_types = list(ChangeType)
        self.assertEqual(len(all_types), 4)

    def test_behavior_pattern_type_enum_completeness(self):
        """Test BehaviorPatternType enum contains expected pattern types."""
        expected_types = ["HABITUAL", "STRATEGIC", "ADAPTIVE", "RESISTANT"]

        for pattern_type in expected_types:
            self.assertTrue(
                hasattr(BehaviorPatternType, pattern_type),
                f"Missing BehaviorPatternType.{pattern_type}"
            )

        # Test all enum values are accessible
        all_types = list(BehaviorPatternType)
        self.assertEqual(len(all_types), 4)

    def test_feedback_polarity_enum_completeness(self):
        """Test FeedbackPolarity enum contains expected polarity types."""
        expected_types = ["REINFORCING", "BALANCING"]

        for polarity_type in expected_types:
            self.assertTrue(
                hasattr(FeedbackPolarity, polarity_type),
                f"Missing FeedbackPolarity.{polarity_type}"
            )

        # Test all enum values are accessible
        all_types = list(FeedbackPolarity)
        self.assertEqual(len(all_types), 2)

    def test_feedback_type_enum_completeness(self):
        """Test FeedbackType enum contains expected feedback types."""
        expected_types = ["POSITIVE", "NEGATIVE", "NEUTRAL"]

        for feedback_type in expected_types:
            self.assertTrue(
                hasattr(FeedbackType, feedback_type),
                f"Missing FeedbackType.{feedback_type}"
            )

        # Test all enum values are accessible
        all_types = list(FeedbackType)
        self.assertEqual(len(all_types), 3)

    def test_temporal_function_type_enum_completeness(self):
        """Test TemporalFunctionType enum contains expected function types."""
        expected_types = ["LINEAR", "EXPONENTIAL", "LOGISTIC", "CYCLICAL", "STEP", "RANDOM"]

        for function_type in expected_types:
            self.assertTrue(
                hasattr(TemporalFunctionType, function_type),
                f"Missing TemporalFunctionType.{function_type}"
            )

        # Test all enum values are accessible
        all_types = list(TemporalFunctionType)
        self.assertEqual(len(all_types), 6)

    def test_validation_rule_type_enum_completeness(self):
        """Test ValidationRuleType enum contains expected rule types."""
        expected_types = ["RANGE", "SUM", "REQUIRED", "UNIQUE", "FORMAT", "RELATIONSHIP"]

        for rule_type in expected_types:
            self.assertTrue(
                hasattr(ValidationRuleType, rule_type),
                f"Missing ValidationRuleType.{rule_type}"
            )

        # Test all enum values are accessible
        all_types = list(ValidationRuleType)
        self.assertEqual(len(all_types), 6)

    def test_system_property_type_enum_completeness(self):
        """Test SystemPropertyType enum contains expected property types."""
        expected_types = ["STRUCTURAL", "DYNAMIC", "PERFORMANCE", "RESILIENCE", "EQUITY", "SUSTAINABILITY"]

        for property_type in expected_types:
            self.assertTrue(
                hasattr(SystemPropertyType, property_type),
                f"Missing SystemPropertyType.{property_type}"
            )

        # Test all enum values are accessible
        all_types = list(SystemPropertyType)
        self.assertEqual(len(all_types), 6)

    def test_all_new_enum_values_unique(self):
        """Test all new enums have unique values."""
        enum_classes: List[Type[Enum]] = [
            FlowType,
            PolicyInstrumentType,
            ChangeType,
            BehaviorPatternType,
            FeedbackPolarity,
            FeedbackType,
            TemporalFunctionType,
            ValidationRuleType,
            SystemPropertyType,
        ]
        for enum_class in enum_classes:
            values = [member.value for member in enum_class]
            self.assertEqual(
                len(values),
                len(set(values)),
                f"{enum_class.__name__} has duplicate values",
            )


class TestDimensionalEntities(unittest.TestCase):
    """Test suite for dimensional meta entities in sfm_models.py"""

    def test_time_slice(self):
        """Test TimeSlice initialization and properties."""
        time_slice = TimeSlice(label="FY2025")
        self.assertEqual(time_slice.label, "FY2025")

        # Test immutability (frozen)
        with self.assertRaises(AttributeError):
            time_slice.label = "Q1-2026"  # type: ignore , this is a frozen dataclass and should raise an error

    def test_spatial_unit(self):
        """Test SpatialUnit initialization and properties."""
        spatial_unit = SpatialUnit(code="US-WA-SEATTLE", name="Seattle, Washington")
        self.assertEqual(spatial_unit.code, "US-WA-SEATTLE")
        self.assertEqual(spatial_unit.name, "Seattle, Washington")

        # Test immutability (frozen)
        with self.assertRaises(AttributeError):
            spatial_unit.code = "US-OR-PORTLAND"  # type: ignore , this is a frozen dataclass and should raise an error

    def test_scenario(self):
        """Test Scenario initialization and properties."""
        scenario = Scenario(label="Carbon Tax 2026")
        self.assertEqual(scenario.label, "Carbon Tax 2026")

        # Test immutability (frozen)
        with self.assertRaises(AttributeError):
            scenario.label = "Baseline"  # type: ignore , this is a frozen dataclass and should raise an error


class TestNodeClasses(unittest.TestCase):
    """Test suite for node classes in sfm_models.py"""

    def test_node_init(self):
        """Test base Node class initialization."""
        # Default initialization with just label
        node = Node(label="Test Node")
        self.assertEqual(node.label, "Test Node")
        self.assertIsNone(node.description)
        self.assertIsInstance(node.id, uuid.UUID)
        self.assertEqual(node.meta, {})

        # Full initialization
        test_id = uuid.uuid4()
        node = Node(
            label="Test Node",
            description="A test node",
            id=test_id,
            meta={"key1": "value1", "key2": "value2"},
        )
        self.assertEqual(node.label, "Test Node")
        self.assertEqual(node.description, "A test node")
        self.assertEqual(node.id, test_id)
        self.assertEqual(node.meta, {"key1": "value1", "key2": "value2"})

    def test_actor_init(self):
        """Test Actor class initialization and inheritance."""
        # Test inheritance
        actor = Actor(label="Test Actor")
        self.assertIsInstance(actor, Node)

        # Test Actor-specific properties
        actor = Actor(
            label="EPA",
            description="Environmental Protection Agency",
            legal_form="Government Agency",
            sector="Public Administration",
        )
        self.assertEqual(actor.label, "EPA")
        self.assertEqual(actor.description, "Environmental Protection Agency")
        self.assertEqual(actor.legal_form, "Government Agency")
        self.assertEqual(actor.sector, "Public Administration")

    def test_institution_init(self):
        """Test Institution class initialization and inheritance."""
        # Test inheritance
        institution = Institution(
            label="Test Institution", layer=InstitutionLayer.FORMAL_RULE
        )
        self.assertIsInstance(institution, Node)

        # Test default layer
        self.assertEqual(institution.layer, InstitutionLayer.FORMAL_RULE)

        # Test Institution-specific properties
        institution = Institution(
            label="Carbon Tax",
            description="Tax on carbon emissions",
            layer=InstitutionLayer.FORMAL_RULE,
        )
        self.assertEqual(institution.label, "Carbon Tax")
        self.assertEqual(institution.description, "Tax on carbon emissions")
        self.assertEqual(institution.layer, InstitutionLayer.FORMAL_RULE)

    def test_institution_init_defaults(self):
        """Test Institution class default values."""
        institution = Institution(label="Test Institution")
        # The actual default should be None, not FORMAL_RULE
        self.assertIsNone(institution.layer)

        # Test with explicit value
        institution_with_layer = Institution(
            label="Test Institution", layer=InstitutionLayer.FORMAL_RULE
        )
        self.assertEqual(institution_with_layer.layer, InstitutionLayer.FORMAL_RULE)

    def test_resource_init(self):
        """Test Resource class initialization and inheritance."""
        # Test inheritance
        resource = Resource(label="Test Resource")
        self.assertIsInstance(resource, Node)

        # Test default type
        self.assertEqual(resource.rtype, ResourceType.NATURAL)

        # Test Resource-specific properties
        resource = Resource(
            label="Coal",
            description="Fossil fuel resource",
            rtype=ResourceType.NATURAL,
            unit="tonnes",
        )
        self.assertEqual(resource.label, "Coal")
        self.assertEqual(resource.description, "Fossil fuel resource")
        self.assertEqual(resource.rtype, ResourceType.NATURAL)
        self.assertEqual(resource.unit, "tonnes")

    def test_process_init(self):
        """Test Process class initialization and inheritance."""
        # Test inheritance
        process = Process(label="Test Process")
        self.assertIsInstance(process, Node)

        # Test Process-specific properties
        process = Process(
            label="Steel Production",
            description="Production of steel from iron ore",
            technology="Blast Furnace",
            responsible_actor_id="steel_mill_1",
        )
        self.assertEqual(process.label, "Steel Production")
        self.assertEqual(process.description, "Production of steel from iron ore")
        self.assertEqual(process.technology, "Blast Furnace")
        self.assertEqual(process.responsible_actor_id, "steel_mill_1")

    def test_flow_init(self):
        """Test Flow class initialization and inheritance."""
        # Test inheritance
        flow = Flow(label="Test Flow")
        self.assertIsInstance(flow, Node)

        # Test default nature
        self.assertEqual(flow.nature, FlowNature.TRANSFER)

        # Test Flow-specific properties
        time_slice = TimeSlice(label="2025")
        spatial_unit = SpatialUnit(code="US", name="United States")
        scenario = Scenario(label="Baseline")

        flow = Flow(
            label="CO2 Emissions",
            description="Carbon dioxide emissions from coal power plant",
            nature=FlowNature.OUTPUT,
            quantity=1000000.0,
            unit="tonnes",
            time=time_slice,
            space=spatial_unit,
            scenario=scenario,
        )
        self.assertEqual(flow.label, "CO2 Emissions")
        self.assertEqual(
            flow.description, "Carbon dioxide emissions from coal power plant"
        )
        self.assertEqual(flow.nature, FlowNature.OUTPUT)
        self.assertEqual(flow.quantity, 1000000.0)
        self.assertEqual(flow.unit, "tonnes")
        self.assertEqual(flow.time, time_slice)
        self.assertEqual(flow.space, spatial_unit)
        self.assertEqual(flow.scenario, scenario)

    # New class tests
    def test_belief_system_init(self):
        """Test BeliefSystem class initialization and inheritance."""
        # Test inheritance
        belief = BeliefSystem(label="Test Belief System")
        self.assertIsInstance(belief, Node)

        # Test BeliefSystem-specific properties
        belief = BeliefSystem(
            label="Economic Growth Paradigm",
            description="Belief system centered on continuous economic growth",
            strength=0.8,
            domain="Economics",
        )
        self.assertEqual(belief.label, "Economic Growth Paradigm")
        self.assertEqual(
            belief.description, "Belief system centered on continuous economic growth"
        )
        self.assertEqual(belief.strength, 0.8)
        self.assertEqual(belief.domain, "Economics")

    def test_policy_init(self):
        """Test Policy class initialization and inheritance."""
        # Test inheritance
        policy = Policy(label="Test Policy")
        self.assertIsInstance(policy, Institution)  # Policy extends Institution

        # Test Policy-specific properties
        policy = Policy(
            label="Carbon Tax Policy",
            description="Tax on carbon emissions",
            authority="Environmental Protection Agency",
            enforcement=0.75,
            target_sectors=["Energy", "Transportation"],
            layer=InstitutionLayer.FORMAL_RULE,  # Redundant if Policy inherits from Institution
        )
        self.assertEqual(policy.label, "Carbon Tax Policy")
        self.assertEqual(policy.description, "Tax on carbon emissions")
        self.assertEqual(policy.authority, "Environmental Protection Agency")
        self.assertEqual(policy.enforcement, 0.75)
        self.assertEqual(policy.target_sectors, ["Energy", "Transportation"])
        self.assertEqual(
            policy.layer, InstitutionLayer.FORMAL_RULE
        )  # Inherited from Institution

    def test_technology_system_init(self):
        """Test TechnologySystem class initialization and inheritance."""
        # Test inheritance
        tech = TechnologySystem(label="Test Technology System")
        self.assertIsInstance(tech, Node)

        # Test TechnologySystem-specific properties
        tech = TechnologySystem(
            label="Renewable Energy Grid",
            description="System of interconnected renewable energy sources",
            maturity=TechnologyReadinessLevel.BASIC_PRINCIPLES,
            compatibility={"fossil_fuel_grid": 0.3, "battery_storage": 0.9},
        )
        self.assertEqual(tech.label, "Renewable Energy Grid")
        self.assertEqual(
            tech.description, "System of interconnected renewable energy sources"
        )
        self.assertEqual(tech.maturity, TechnologyReadinessLevel.BASIC_PRINCIPLES)
        self.assertEqual(
            tech.compatibility, {"fossil_fuel_grid": 0.3, "battery_storage": 0.9}
        )

    def test_indicator_init(self):
        """Test Indicator class initialization and inheritance."""
        # Test inheritance
        indicator = Indicator(
            label="Test Indicator",
            value_category=ValueCategory.ECONOMIC,
            measurement_unit="$",
        )
        self.assertIsInstance(indicator, Node)

        # Test Indicator-specific properties
        indicator = Indicator(
            label="GDP Growth",
            description="Annual gross domestic product growth",
            value_category=ValueCategory.ECONOMIC,
            measurement_unit="%",
            current_value=2.5,
            target_value=3.0,
            threshold_values={"recession": 0.0, "boom": 4.0},
        )
        self.assertEqual(indicator.label, "GDP Growth")
        self.assertEqual(indicator.description, "Annual gross domestic product growth")
        self.assertEqual(indicator.value_category, ValueCategory.ECONOMIC)
        self.assertEqual(indicator.measurement_unit, "%")
        self.assertEqual(indicator.current_value, 2.5)
        self.assertEqual(indicator.target_value, 3.0)
        self.assertEqual(indicator.threshold_values, {"recession": 0.0, "boom": 4.0})

    def test_value_system_init(self):
        """Test ValueSystem class initialization and inheritance."""
        # Test inheritance
        value_system = ValueSystem(label="Democratic Values")
        self.assertIsInstance(value_system, Node)

        # Test ValueSystem-specific properties
        parent_ids = [uuid.uuid4() for _ in range(2)]
        value_system = ValueSystem(
            label="Environmental Justice",
            description="Core values around environmental equity",
            parent_values=parent_ids,
            priority_weight=0.8,
            cultural_domain="environmental_policy",
            legitimacy_source=LegitimacySource.LEGAL_RATIONAL
        )
        self.assertEqual(value_system.label, "Environmental Justice")
        self.assertEqual(value_system.description, "Core values around environmental equity")
        self.assertEqual(value_system.parent_values, parent_ids)
        self.assertEqual(value_system.priority_weight, 0.8)
        self.assertEqual(value_system.cultural_domain, "environmental_policy")
        self.assertEqual(value_system.legitimacy_source, LegitimacySource.LEGAL_RATIONAL)

    def test_ceremonial_behavior_init(self):
        """Test CeremonialBehavior class initialization and inheritance."""
        # Test inheritance
        ceremonial = CeremonialBehavior(label="Traditional Practices")
        self.assertIsInstance(ceremonial, Node)

        # Test CeremonialBehavior-specific properties
        ceremonial = CeremonialBehavior(
            label="Bureaucratic Procedures",
            description="Rigid bureaucratic processes that resist change",
            rigidity_level=0.9,
            tradition_strength=0.7,
            resistance_to_change=0.8
        )
        self.assertEqual(ceremonial.label, "Bureaucratic Procedures")
        self.assertEqual(ceremonial.description, "Rigid bureaucratic processes that resist change")
        self.assertEqual(ceremonial.rigidity_level, 0.9)
        self.assertEqual(ceremonial.tradition_strength, 0.7)
        self.assertEqual(ceremonial.resistance_to_change, 0.8)

    def test_instrumental_behavior_init(self):
        """Test InstrumentalBehavior class initialization and inheritance."""
        # Test inheritance
        instrumental = InstrumentalBehavior(label="Problem Solving")
        self.assertIsInstance(instrumental, Node)

        # Test InstrumentalBehavior-specific properties
        instrumental = InstrumentalBehavior(
            label="Adaptive Management",
            description="Flexible problem-solving approaches",
            efficiency_measure=0.85,
            adaptability_score=0.9,
            innovation_potential=0.8
        )
        self.assertEqual(instrumental.label, "Adaptive Management")
        self.assertEqual(instrumental.description, "Flexible problem-solving approaches")
        self.assertEqual(instrumental.efficiency_measure, 0.85)
        self.assertEqual(instrumental.adaptability_score, 0.9)
        self.assertEqual(instrumental.innovation_potential, 0.8)

    def test_policy_instrument_init(self):
        """Test PolicyInstrument class initialization and inheritance."""
        # Test inheritance
        instrument = PolicyInstrument(label="Carbon Tax")
        self.assertIsInstance(instrument, Node)

        # Test PolicyInstrument-specific properties
        instrument = PolicyInstrument(
            label="Emissions Trading System",
            description="Market-based carbon reduction mechanism",
            instrument_type=PolicyInstrumentType.ECONOMIC,
            target_behavior="emissions reduction",
            compliance_mechanism="market_penalties",
            effectiveness_measure=0.75
        )
        self.assertEqual(instrument.label, "Emissions Trading System")
        self.assertEqual(instrument.description, "Market-based carbon reduction mechanism")
        self.assertEqual(instrument.instrument_type, PolicyInstrumentType.ECONOMIC)
        self.assertEqual(instrument.target_behavior, "emissions reduction")
        self.assertEqual(instrument.compliance_mechanism, "market_penalties")
        self.assertEqual(instrument.effectiveness_measure, 0.75)

    def test_governance_structure_init(self):
        """Test GovernanceStructure class initialization and inheritance."""
        # Test inheritance from Institution
        governance = GovernanceStructure(label="Federal Agency")
        self.assertIsInstance(governance, Institution)
        self.assertIsInstance(governance, Node)

        # Test GovernanceStructure-specific properties
        power_dist = {"executive": 0.6, "legislative": 0.3, "judicial": 0.1}
        accountability = ["oversight_committees", "audit_requirements", "public_reporting"]

        governance = GovernanceStructure(
            label="Environmental Protection Governance",
            description="Multi-level environmental governance structure",
            decision_making_process="consensus_based",
            power_distribution=power_dist,
            accountability_mechanisms=accountability,
            layer=InstitutionLayer.ORGANIZATION
        )
        self.assertEqual(governance.label, "Environmental Protection Governance")
        self.assertEqual(governance.description, "Multi-level environmental governance structure")
        self.assertEqual(governance.decision_making_process, "consensus_based")
        self.assertEqual(governance.power_distribution, power_dist)
        self.assertEqual(governance.accountability_mechanisms, accountability)
        self.assertEqual(governance.layer, InstitutionLayer.ORGANIZATION)

    def test_value_flow_init(self):
        """Test ValueFlow class initialization and inheritance."""
        # Test inheritance from Flow
        value_flow = ValueFlow(label="Economic Benefits")
        self.assertIsInstance(value_flow, Flow)
        self.assertIsInstance(value_flow, Node)

        # Test ValueFlow-specific properties
        beneficiaries = [uuid.uuid4() for _ in range(3)]
        impact = {"low_income": 0.3, "middle_income": 0.5, "high_income": 0.2}

        value_flow = ValueFlow(
            label="Green Jobs Creation",
            description="Value flow from renewable energy investments",
            nature=FlowNature.OUTPUT,
            quantity=1000.0,
            unit="jobs",
            value_created=500000.0,
            value_captured=300000.0,
            beneficiary_actors=beneficiaries,
            distributional_impact=impact
        )
        self.assertEqual(value_flow.label, "Green Jobs Creation")
        self.assertEqual(value_flow.description, "Value flow from renewable energy investments")
        self.assertEqual(value_flow.nature, FlowNature.OUTPUT)
        self.assertEqual(value_flow.quantity, 1000.0)
        self.assertEqual(value_flow.unit, "jobs")
        self.assertEqual(value_flow.value_created, 500000.0)
        self.assertEqual(value_flow.value_captured, 300000.0)
        self.assertEqual(value_flow.beneficiary_actors, beneficiaries)
        self.assertEqual(value_flow.distributional_impact, impact)

    def test_change_process_init(self):
        """Test ChangeProcess class initialization and inheritance."""
        # Test inheritance
        change = ChangeProcess(label="Energy Transition")
        self.assertIsInstance(change, Node)

        # Test ChangeProcess-specific properties
        agents = [uuid.uuid4() for _ in range(2)]
        resistance = [uuid.uuid4() for _ in range(3)]
        trajectory = [TimeSlice(label="2025"), TimeSlice(label="2030")]

        change = ChangeProcess(
            label="Renewable Energy Transition",
            description="Transition from fossil fuels to renewables",
            change_type=ChangeType.EVOLUTIONARY,
            change_agents=agents,
            resistance_factors=resistance,
            change_trajectory=trajectory,
            success_probability=0.7
        )
        self.assertEqual(change.label, "Renewable Energy Transition")
        self.assertEqual(change.description, "Transition from fossil fuels to renewables")
        self.assertEqual(change.change_type, ChangeType.EVOLUTIONARY)
        self.assertEqual(change.change_agents, agents)
        self.assertEqual(change.resistance_factors, resistance)
        self.assertEqual(change.change_trajectory, trajectory)
        self.assertEqual(change.success_probability, 0.7)

    def test_cognitive_framework_init(self):
        """Test CognitiveFramework class initialization and inheritance."""
        # Test inheritance
        framework = CognitiveFramework(label="Market Fundamentalism")
        self.assertIsInstance(framework, Node)

        # Test CognitiveFramework-specific properties
        framing = {"market": "efficient", "government": "inefficient"}
        biases = ["confirmation_bias", "availability_heuristic"]
        filters = ["economic_data", "market_signals"]

        framework = CognitiveFramework(
            label="Neoliberal Framework",
            description="Market-oriented cognitive framework",
            framing_effects=framing,
            cognitive_biases=biases,
            information_filters=filters,
            learning_capacity=0.6
        )
        self.assertEqual(framework.label, "Neoliberal Framework")
        self.assertEqual(framework.description, "Market-oriented cognitive framework")
        self.assertEqual(framework.framing_effects, framing)
        self.assertEqual(framework.cognitive_biases, biases)
        self.assertEqual(framework.information_filters, filters)
        self.assertEqual(framework.learning_capacity, 0.6)

    def test_behavioral_pattern_init(self):
        """Test BehavioralPattern class initialization and inheritance."""
        # Test inheritance
        pattern = BehavioralPattern(label="Short-term Thinking")
        self.assertIsInstance(pattern, Node)

        # Test BehavioralPattern-specific properties
        context_deps = ["economic_pressure", "political_cycles"]

        pattern = BehavioralPattern(
            label="Quarterly Reporting Focus",
            description="Pattern of focusing on short-term quarterly results",
            pattern_type=BehaviorPatternType.HABITUAL,
            frequency=4.0,  # per year
            predictability=0.8,
            context_dependency=context_deps
        )
        self.assertEqual(pattern.label, "Quarterly Reporting Focus")
        self.assertEqual(pattern.description, "Pattern of focusing on short-term quarterly results")
        self.assertEqual(pattern.pattern_type, BehaviorPatternType.HABITUAL)
        self.assertEqual(pattern.frequency, 4.0)
        self.assertEqual(pattern.predictability, 0.8)
        self.assertEqual(pattern.context_dependency, context_deps)

    def test_actor_extended_fields(self):
        """Test Actor class extended SFM fields."""
        actor = Actor(
            label="Environmental NGO",
            description="Non-governmental environmental organization",
            legal_form="Non-profit",
            sector="Environmental Advocacy",
            power_resources={"political": 0.6, "economic": 0.3, "social": 0.8},
            decision_making_capacity=0.7,
            institutional_affiliations=[uuid.uuid4(), uuid.uuid4()],
            cognitive_frameworks=[uuid.uuid4()],
            behavioral_patterns=[uuid.uuid4(), uuid.uuid4()]
        )

        self.assertEqual(actor.power_resources, {"political": 0.6, "economic": 0.3, "social": 0.8})
        self.assertEqual(actor.decision_making_capacity, 0.7)
        self.assertEqual(len(actor.institutional_affiliations), 2)
        self.assertEqual(len(actor.cognitive_frameworks), 1)
        self.assertEqual(len(actor.behavioral_patterns), 2)

    def test_institution_extended_fields(self):
        """Test Institution class extended SFM fields."""
        institution = Institution(
            label="Environmental Protection Law",
            description="Legal framework for environmental protection",
            layer=InstitutionLayer.FORMAL_RULE,
            formal_rules=["Clean Air Act", "Water Protection Standards"],
            informal_norms=["Environmental stewardship", "Precautionary principle"],
            enforcement_mechanisms=["Fines", "Permits", "Inspections"],
            legitimacy_basis="legal-rational",
            change_resistance=0.8,
            path_dependencies=[uuid.uuid4()]
        )

        self.assertEqual(institution.formal_rules, ["Clean Air Act", "Water Protection Standards"])
        self.assertEqual(institution.informal_norms, ["Environmental stewardship", "Precautionary principle"])
        self.assertEqual(institution.enforcement_mechanisms, ["Fines", "Permits", "Inspections"])
        self.assertEqual(institution.legitimacy_basis, "legal-rational")
        self.assertEqual(institution.change_resistance, 0.8)
        self.assertEqual(len(institution.path_dependencies), 1)

    def test_flow_extended_fields(self):
        """Test Flow class extended SFM fields."""
        flow = Flow(
            label="Carbon Emissions Flow",
            description="CO2 emissions from industrial process",
            nature=FlowNature.OUTPUT,
            quantity=50000.0,
            unit="tonnes CO2",
            flow_type=FlowType.MATERIAL,
            source_process_id=uuid.uuid4(),
            target_process_id=uuid.uuid4(),
            transformation_coefficient=0.95,
            loss_factor=0.05,
            ceremonial_component=0.2,
            instrumental_component=0.8
        )

        self.assertEqual(flow.flow_type, FlowType.MATERIAL)
        self.assertIsInstance(flow.source_process_id, uuid.UUID)
        self.assertIsInstance(flow.target_process_id, uuid.UUID)
        self.assertEqual(flow.transformation_coefficient, 0.95)
        self.assertEqual(flow.loss_factor, 0.05)
        self.assertEqual(flow.ceremonial_component, 0.2)
        self.assertEqual(flow.instrumental_component, 0.8)


class TestFieldValidation(unittest.TestCase):
    """Test field validation and constraints."""

    def test_indicator_required_fields(self):
        """Test that Indicator requires value_category and measurement_unit."""
        # This should work with required fields
        indicator = Indicator(
            label="GDP", value_category=ValueCategory.ECONOMIC, measurement_unit="USD"
        )
        self.assertEqual(indicator.value_category, ValueCategory.ECONOMIC)
        self.assertEqual(indicator.measurement_unit, "USD")

    def test_relationship_id_uniqueness(self):
        """Test that relationships get unique IDs."""
        rel1 = Relationship(
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind=RelationshipKind.GOVERNS,
        )
        rel2 = Relationship(
            source_id=uuid.uuid4(), target_id=uuid.uuid4(), kind=RelationshipKind.USES
        )

        self.assertNotEqual(rel1.id, rel2.id)

    def test_node_uuid_generation(self):
        """Test that nodes get unique UUIDs."""
        node1 = Node(label="Node 1")
        node2 = Node(label="Node 2")

        self.assertNotEqual(node1.id, node2.id)
        self.assertIsInstance(node1.id, uuid.UUID)
        self.assertIsInstance(node2.id, uuid.UUID)

    def test_frozen_dataclass_immutability(self):
        """Test that frozen dataclasses cannot be modified."""
        time_slice = TimeSlice(label="2025")
        spatial_unit = SpatialUnit(code="US", name="United States")
        scenario = Scenario(label="Baseline")
          # These should all raise AttributeError
        with self.assertRaises(AttributeError):
            time_slice.label = "2026"  # type: ignore

        with self.assertRaises(AttributeError):
            spatial_unit.code = "CA"  # type: ignore

        with self.assertRaises(AttributeError):
            scenario.label = "Alternative"  # type: ignore

    def test_default_field_values(self):
        """Test default values for various node types."""
        # Test Resource defaults
        resource = Resource(label="Test Resource")
        self.assertEqual(resource.rtype, ResourceType.NATURAL)
        self.assertIsNone(resource.unit)

        # Test Flow defaults
        flow = Flow(label="Test Flow")
        self.assertEqual(flow.nature, FlowNature.TRANSFER)
        self.assertIsNone(flow.quantity)

        # Test Actor defaults
        actor = Actor(label="Test Actor")
        self.assertEqual(actor.power_resources, {})
        self.assertEqual(actor.institutional_affiliations, [])

        # Test Institution defaults
        institution = Institution(label="Test Institution")
        self.assertIsNone(institution.layer)
        self.assertEqual(institution.formal_rules, [])

    def test_relationship_field_validation(self):
        """Test relationship field constraints and defaults."""
        rel = Relationship(
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind=RelationshipKind.GOVERNS
        )

        # Test defaults
        self.assertEqual(rel.weight, 0.0)
        self.assertEqual(rel.certainty, 1.0)
        self.assertIsNone(rel.variability)
        self.assertEqual(rel.meta, {})

        # Test with all fields
        rel_full = Relationship(
            source_id=uuid.uuid4(),
            target_id=uuid.uuid4(),
            kind=RelationshipKind.USES,
            weight=0.5,
            certainty=0.8,
            variability=0.1,
            meta={"source": "survey_data"}
        )
        self.assertEqual(rel_full.weight, 0.5)
        self.assertEqual(rel_full.certainty, 0.8)
        self.assertEqual(rel_full.variability, 0.1)
        self.assertEqual(rel_full.meta["source"], "survey_data")

    def test_numeric_field_constraints(self):
        """Test numeric field bounds and validation."""
        # Test probability fields should be between 0 and 1
        ceremonial = CeremonialBehavior(
            label="Test",
            rigidity_level=0.5,
            tradition_strength=0.0,
            resistance_to_change=1.0
        )
        self.assertIsNotNone(ceremonial.rigidity_level)
        self.assertGreaterEqual(ceremonial.rigidity_level or 0.0, 0.0)
        self.assertLessEqual(ceremonial.rigidity_level or 1.0, 1.0)

        # Test that invalid probability values are handled gracefully
        # (Note: dataclasses don't enforce constraints by default, but this tests current behavior)
        extreme_ceremonial = CeremonialBehavior(
            label="Extreme Test",
            rigidity_level=2.0,  # Above normal range
            tradition_strength=-0.5  # Below normal range
        )
        self.assertEqual(extreme_ceremonial.rigidity_level, 2.0)  # Current implementation allows this
        self.assertEqual(extreme_ceremonial.tradition_strength, -0.5)

    def test_collection_field_types(self):
        """Test that collection fields maintain proper types."""
        actor = Actor(
            label="Test Actor",
            institutional_affiliations=[uuid.uuid4(), uuid.uuid4()],
            cognitive_frameworks=[uuid.uuid4()],
            behavioral_patterns=[uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
        )

        # Verify all elements are UUIDs
        for affiliation in actor.institutional_affiliations:
            self.assertIsInstance(affiliation, uuid.UUID)
        for framework in actor.cognitive_frameworks:
            self.assertIsInstance(framework, uuid.UUID)
        for pattern in actor.behavioral_patterns:
            self.assertIsInstance(pattern, uuid.UUID)

    def test_meta_field_validation(self):
        """Test metadata field validation and behavior."""
        node = Node(
            label="Test Node",
            meta={"key1": "value1", "key2": "value2", "numeric": "123"}
        )

        # Meta should be string-to-string mapping
        for key, value in node.meta.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)

        # Test meta field modification
        node.meta["new_key"] = "new_value"
        self.assertEqual(node.meta["new_key"], "new_value")

    def test_string_field_validation(self):
        """Test string field handling including empty strings."""
        # Test empty string handling
        node = Node(label="")
        self.assertEqual(node.label, "")

        # Test very long strings
        long_label = "A" * 1000
        node_long = Node(label=long_label)
        self.assertEqual(node_long.label, long_label)
        self.assertEqual(len(node_long.label), 1000)

    def test_optional_field_behavior(self):
        """Test behavior of optional fields across different node types."""
        # Test that optional fields can be None
        flow = Flow(
            label="Test Flow",
            quantity=None,
            unit=None,
            time=None,
            space=None,
            scenario=None
        )
        self.assertIsNone(flow.quantity)
        self.assertIsNone(flow.unit)
        self.assertIsNone(flow.time)
        self.assertIsNone(flow.space)
        self.assertIsNone(flow.scenario)

        # Test setting optional fields to valid values
        time_slice = TimeSlice(label="2025")
        flow.time = time_slice
        self.assertEqual(flow.time, time_slice)

    def test_enum_field_validation(self):
        """Test enum field validation and assignment."""
        # Test valid enum assignments
        resource = Resource(label="Test", rtype=ResourceType.HUMAN)
        self.assertEqual(resource.rtype, ResourceType.HUMAN)

        flow = Flow(label="Test", nature=FlowNature.INPUT)
        self.assertEqual(flow.nature, FlowNature.INPUT)

        institution = Institution(label="Test", layer=InstitutionLayer.ORGANIZATION)
        self.assertEqual(institution.layer, InstitutionLayer.ORGANIZATION)

        # Test enum value validation by checking all valid enum values
        for resource_type in ResourceType:
            resource = Resource(label="Test", rtype=resource_type)
            self.assertIn(resource.rtype, list(ResourceType))

        # Only test compatible combinations of FlowNature and FlowType
        compatible_flow_types = {
            FlowNature.INPUT: FlowType.MATERIAL,
            FlowNature.OUTPUT: FlowType.MATERIAL,
            FlowNature.TRANSFER: FlowType.MATERIAL,
        }
        for flow_nature, flow_type in compatible_flow_types.items():
            flow = Flow(label="Test", nature=flow_nature, flow_type=flow_type)
            self.assertIn(flow.nature, list(FlowNature))

    def test_datetime_field_behavior(self):
        """Test datetime field handling in AnalyticalContext and SystemProperty."""
        context = AnalyticalContext(label="Test Context")
        self.assertIsInstance(context.created_at, datetime)
        self.assertIsNone(context.modified_at)

        # Test setting modified_at
        now = datetime.now()
        context.modified_at = now
        self.assertEqual(context.modified_at, now)

        # Test SystemProperty timestamp
        prop = SystemProperty(label="Test Property")
        self.assertIsInstance(prop.timestamp, datetime)

    def test_complex_field_defaults(self):
        """Test complex field default values don't share references."""
        actor1 = Actor(label="Actor 1")
        actor2 = Actor(label="Actor 2")

        # Verify default lists are independent
        actor1.institutional_affiliations.append(uuid.uuid4())
        self.assertEqual(len(actor1.institutional_affiliations), 1)
        self.assertEqual(len(actor2.institutional_affiliations), 0)
          # Verify default dicts are independent
        actor1.power_resources["political"] = 0.5
        self.assertEqual(len(actor1.power_resources), 1)
        self.assertEqual(len(actor2.power_resources), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_empty_collections(self):
        """Test behavior with empty collections."""
        graph = SFMGraph()

        # Test iteration over empty graph
        nodes = list(graph)
        self.assertEqual(len(nodes), 0)

    def test_circular_relationships(self):
        """Test adding circular relationships."""
        node1_id = uuid.uuid4()
        node2_id = uuid.uuid4()

        rel1 = Relationship(
            source_id=node1_id, target_id=node2_id, kind=RelationshipKind.INFLUENCES
        )
        rel2 = Relationship(
            source_id=node2_id, target_id=node1_id, kind=RelationshipKind.INFLUENCES
        )

        graph = SFMGraph()
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)  # Should not raise error

        self.assertEqual(len(graph.relationships), 2)

    def test_self_referencing_relationship(self):
        """Test relationship where source equals target."""
        node_id = uuid.uuid4()

        rel = Relationship(
            source_id=node_id, target_id=node_id, kind=RelationshipKind.MAINTAINS
        )

        # Should be allowed
        self.assertEqual(rel.source_id, rel.target_id)

    def test_large_collections(self):
        """Test performance with larger collections."""
        graph = SFMGraph()

        # Add many nodes
        actors = []
        for i in range(100):
            actor = Actor(label=f"Actor {i}")
            actors.append(actor)
            graph.add_node(actor)

        self.assertEqual(len(graph.actors), 100)

        # Test iteration performance
        count = 0
        for actor in graph.actors:
            count += 1
        self.assertEqual(count, 100)

    def test_large_graph_performance(self):
        """Test adding a large number of nodes and relationships to the graph."""
        graph = SFMGraph()
        nodes = [Actor(label=f"Actor {i}") for i in range(200)]
        for node in nodes:
            graph.add_node(node)
        self.assertEqual(len(graph.actors), 200)
        # Add relationships
        for i in range(199):
            rel = Relationship(
                source_id=nodes[i].id,
                target_id=nodes[i+1].id,
                kind=RelationshipKind.COLLABORATES_WITH
            )
            graph.add_relationship(rel)
        self.assertEqual(len(graph.relationships), 199)

    def test_boundary_values(self):
        """Test boundary values for numeric fields."""
        ceremonial = CeremonialBehavior(label="Test", rigidity_level=0.0, tradition_strength=1.0, resistance_to_change=1.0)
        self.assertEqual(ceremonial.rigidity_level, 0.0)
        self.assertEqual(ceremonial.tradition_strength, 1.0)
        self.assertEqual(ceremonial.resistance_to_change, 1.0)
        # Test negative and large values (should be accepted by current implementation)
        ceremonial2 = CeremonialBehavior(label="Test2", rigidity_level=-1.0, tradition_strength=100.0)
        self.assertEqual(ceremonial2.rigidity_level, -1.0)
        self.assertEqual(ceremonial2.tradition_strength, 100.0)

    def test_empty_and_none_values(self):
        """Test handling of empty and None values in fields."""
        node = Node(label="", description=None)
        self.assertEqual(node.label, "")
        self.assertIsNone(node.description)
        # Test empty meta
        self.assertEqual(node.meta, {})
        # Test None for optional fields in Flow
        flow = Flow(label="Test", quantity=None, unit=None, time=None, space=None, scenario=None)
        self.assertIsNone(flow.quantity)
        self.assertIsNone(flow.unit)
        self.assertIsNone(flow.time)
        self.assertIsNone(flow.space)
        self.assertIsNone(flow.scenario)

    def test_unicode_and_special_characters(self):
        """Test support for unicode and special characters in string fields."""
        special_label = "测试 – テスト – اختبار – тест – δοκιμή – 🚀"
        node = Node(label=special_label)
        self.assertEqual(node.label, special_label)
        # Test special characters in meta
        node.meta["emoji"] = "🌟"
        self.assertEqual(node.meta["emoji"], "🌟")

    def test_stress_testing_large_relationships(self):
        """Stress test with a large number of relationships."""
        graph = SFMGraph()
        nodes = [Actor(label=f"Actor {i}") for i in range(50)]
        for node in nodes:
            graph.add_node(node)
        # Add many relationships
        for i in range(50):
            for j in range(50):
                if i != j:
                    rel = Relationship(
                        source_id=nodes[i].id,
                        target_id=nodes[j].id,
                        kind=RelationshipKind.COMPETES_WITH
                    )
                    graph.add_relationship(rel)
        self.assertEqual(len(graph.relationships), 50*49)

    def test_deeply_nested_collections(self):
        """Test nodes with complex nested data structures."""
        # Test actor with complex nested structures
        complex_actor = Actor(
            label="Complex Actor",
            power_resources={
                "political": 0.8,
                "economic": 0.6,
                "social": 0.9,
                "technological": 0.4,
                "informational": 0.7
            },
            institutional_affiliations=[uuid.uuid4() for _ in range(10)],
            cognitive_frameworks=[uuid.uuid4() for _ in range(5)],
            behavioral_patterns=[uuid.uuid4() for _ in range(15)]
        )

        self.assertEqual(len(complex_actor.power_resources), 5)
        self.assertEqual(len(complex_actor.institutional_affiliations), 10)
        self.assertEqual(len(complex_actor.cognitive_frameworks), 5)
        self.assertEqual(len(complex_actor.behavioral_patterns), 15)


    def test_memory_efficiency_collections(self):
        """Test that empty collections don't consume excessive memory."""
        # Create many nodes with empty collections
        nodes = []
        for i in range(1000):
            node = Actor(
                label=f"Actor {i}",
                institutional_affiliations=[],
                cognitive_frameworks=[],
                behavioral_patterns=[],
                power_resources={}
            )
            nodes.append(node)

        # All nodes should have independent empty collections
        nodes[0].institutional_affiliations.append(uuid.uuid4())
        self.assertEqual(len(nodes[0].institutional_affiliations), 1)
        self.assertEqual(len(nodes[1].institutional_affiliations), 0)


class TestSFMGraphOperations(unittest.TestCase):
    """Test suite for graph operations in SFMGraph class."""

    def setUp(self):
        """Set up a basic graph with one actor, one institution, one resource, one process, one flow, and one relationship for testing."""
        self.graph = SFMGraph()

        # Add a single actor
        self.actor = Actor(label="Test Actor", sector="Public")
        self.graph.add_node(self.actor)

        # Add a single institution
        self.institution = Institution(
            label="Test Institution",
            description="A test institution",
            layer=InstitutionLayer.FORMAL_RULE,
        )
        self.graph.add_node(self.institution)

        # Add a single resource
        self.resource = Resource(label="Test Resource", rtype=ResourceType.NATURAL)
        self.graph.add_node(self.resource)

        # Add a single process
        self.process = Process(label="Test Process", technology="Solar Panel")
        self.graph.add_node(self.process)

        # Add a single flow
        self.flow = Flow(label="Test Flow", nature=FlowNature.INPUT, unit="kWh")
        self.graph.add_node(self.flow)

        # Add a relationship between actor and institution
        self.relationship = Relationship(
            source_id=self.actor.id,
            target_id=self.institution.id,
            kind=RelationshipKind.GOVERNS,
        )
        self.graph.add_relationship(self.relationship)

    def test_add_node(self):
        """Test adding nodes to the graph."""
        # New actor
        actor2 = Actor(label="Test Actor 2", sector="Private")
        self.graph.add_node(actor2)
        self.assertEqual(len(self.graph.actors), 2)
        self.assertIn(actor2.id, self.graph.actors)

        # New institution
        institution2 = Institution(
            label="Test Institution 2",
            description="Another test institution",
            layer=InstitutionLayer.INFORMAL_NORM,
        )
        self.graph.add_node(institution2)
        self.assertEqual(len(self.graph.institutions), 2)
        self.assertIn(institution2.id, self.graph.institutions)        # New resource
        resource = Resource(label="Test Resource", rtype=ResourceType.PRODUCED)
        self.graph.add_node(resource)
        self.assertEqual(len(self.graph.resources), 2)  # setUp already added 1
        self.assertIn(resource.id, self.graph.resources)

        # New process
        process = Process(label="Test Process", technology="Solar Panel")
        self.graph.add_node(process)
        self.assertEqual(len(self.graph.processes), 2)  # setUp already added 1
        self.assertIn(process.id, self.graph.processes)

        # New flow
        flow = Flow(label="Test Flow", nature=FlowNature.INPUT, unit="kWh")
        self.graph.add_node(flow)
        self.assertEqual(len(self.graph.flows), 2)  # setUp already added 1
        self.assertIn(flow.id, self.graph.flows)

    def test_add_relationship(self):
        """Test adding relationships to the graph."""
        # New relationship
        rel = Relationship(
            source_id=self.actor.id,
            target_id=self.institution.id,
            kind=RelationshipKind.USES,
            weight=0.8,
        )
        self.graph.add_relationship(rel)
        self.assertEqual(len(self.graph.relationships), 2)
        self.assertIn(rel.id, self.graph.relationships)

    def test_inheritance_handling_in_add_node(self):
        """Test that inheritance is properly handled in add_node method."""
        # ValueFlow inherits from Flow
        value_flow = ValueFlow(label="Test Value Flow")
        regular_flow = Flow(label="Test Regular Flow")

        self.graph.add_node(value_flow)
        self.graph.add_node(regular_flow)        # ValueFlow should go to value_flows collection
        self.assertEqual(len(self.graph.value_flows), 1)
        self.assertEqual(len(self.graph.flows), 2)  # 1 regular + 1 from setUp
        self.assertIn(value_flow.id, self.graph.value_flows)
        self.assertIn(regular_flow.id, self.graph.flows)

        # GovernanceStructure inherits from Institution
        governance = GovernanceStructure(label="Test Governance")
        regular_institution = Institution(label="Test Institution")

        self.graph.add_node(governance)
        self.graph.add_node(regular_institution)

        # GovernanceStructure should go to governance_structures collection
        self.assertEqual(len(self.graph.governance_structures), 1)
        self.assertEqual(len(self.graph.institutions), 2)  # 1 regular + 1 from setUp
        self.assertIn(governance.id, self.graph.governance_structures)
        self.assertIn(regular_institution.id, self.graph.institutions)

    def test_graph_find_operations(self):
        """Test finding nodes and relationships in the graph."""
        # Add some nodes
        self.graph.add_node(self.actor)
        self.graph.add_node(self.institution)
        self.graph.add_relationship(self.relationship)

        # Test finding nodes by type
        all_actors = list(self.graph.actors.values())
        self.assertEqual(len(all_actors), 1)
        self.assertEqual(all_actors[0], self.actor)
          # Test finding relationships by source/target
        found_rel = None
        for rel in self.graph.relationships.values():
            if rel.source_id == self.actor.id and rel.target_id == self.institution.id:
                found_rel = rel
                break

        self.assertIsNotNone(found_rel)
        if found_rel is not None:
            self.assertEqual(found_rel.kind, RelationshipKind.GOVERNS)

    def test_graph_statistics(self):
        """Test graph statistics and metrics."""
        # Graph starts with setUp nodes: 5 nodes and 1 relationship
        self.assertEqual(len(self.graph), 5)
        self.assertEqual(len(self.graph.relationships), 1)

        # Add more nodes of different types
        new_actor = Actor(label="New Actor", sector="Private")
        new_institution = Institution(label="New Institution", description="New", layer=InstitutionLayer.INFORMAL_NORM)
        self.graph.add_node(new_actor)
        self.graph.add_node(new_institution)
          # Test updated node counts
        self.assertEqual(len(self.graph), 7)
        self.assertEqual(len(self.graph.actors), 2)  # 1 new + 1 from setUp
        self.assertEqual(len(self.graph.institutions), 2)  # 1 new + 1 from setUp
        self.assertEqual(len(self.graph.resources), 1)  # From setUp
        self.assertEqual(len(self.graph.processes), 1)  # From setUp
        self.assertEqual(len(self.graph.flows), 1)  # From setUp

        # Add relationships
        rel1 = Relationship(
            source_id=self.actor.id,
            target_id=self.institution.id,
            kind=RelationshipKind.GOVERNS
        )
        rel2 = Relationship(
            source_id=self.institution.id,
            target_id=self.resource.id,
            kind=RelationshipKind.REGULATES
        )

        self.graph.add_relationship(rel1)
        self.graph.add_relationship(rel2)

        self.assertEqual(len(self.graph.relationships), 3)  # 2 new + 1 from setUp

    def test_graph_node_type_distribution(self):
        """Test getting distribution of node types in the graph."""
        # Add various node types
        nodes_to_add = [
            Actor(label="Actor 1"),
            Actor(label="Actor 2"),
            Institution(label="Institution 1"),
            Resource(label="Resource 1"),
            Resource(label="Resource 2"),
            Resource(label="Resource 3"),
            Process(label="Process 1"),
            Flow(label="Flow 1"),
            Flow(label="Flow 2"),
            ValueSystem(label="Values 1"),
            CeremonialBehavior(label="Ceremonial 1"),
        ]

        for node in nodes_to_add:
            self.graph.add_node(node)
          # Check distribution (including setUp nodes: 1 actor, 1 institution, 1 resource, 1 process, 1 flow)
        self.assertEqual(len(self.graph.actors), 3)  # 2 new + 1 from setUp
        self.assertEqual(len(self.graph.institutions), 2)  # 1 new + 1 from setUp
        self.assertEqual(len(self.graph.resources), 4)  # 3 new + 1 from setUp
        self.assertEqual(len(self.graph.processes), 2)  # 1 new + 1 from setUp
        self.assertEqual(len(self.graph.flows), 3)  # 2 new + 1 from setUp
        self.assertEqual(len(self.graph.value_systems), 1)
        self.assertEqual(len(self.graph.ceremonial_behaviors), 1)

        # Total should equal sum of parts
        total_expected = 3 + 2 + 4 + 2 + 3 + 1 + 1  # 16 total
        self.assertEqual(len(self.graph), total_expected)

    def test_graph_relationship_patterns(self):
        """Test common relationship patterns in SFM."""
        # Create a small SFM network
        epa = Actor(label="EPA", sector="Government")
        carbon_tax = Policy(label="Carbon Tax", authority="Federal")
        energy_sector = Actor(label="Energy Sector", sector="Private")
        emissions = Flow(label="CO2 Emissions", nature=FlowNature.OUTPUT)

        nodes = [epa, carbon_tax, energy_sector, emissions]
        for node in nodes:
            self.graph.add_node(node)
          # Create relationships
        relationships = [
            Relationship(epa.id, carbon_tax.id, RelationshipKind.ENACTS, weight=1.0),
            Relationship(carbon_tax.id, energy_sector.id, RelationshipKind.REGULATES, weight=0.8),
            Relationship(energy_sector.id, emissions.id, RelationshipKind.PRODUCES, weight=0.9),
            Relationship(epa.id, emissions.id, RelationshipKind.MONITORS, weight=0.7),
        ]

        for rel in relationships:
            self.graph.add_relationship(rel)
          # Test relationship patterns
        self.assertEqual(len(self.graph.relationships), 5)  # 4 new + 1 from setUp

        # Find all relationships involving EPA
        epa_relationships = [
            rel for rel in self.graph.relationships.values()
            if epa.id in (rel.source_id, rel.target_id)
        ]
        self.assertEqual(len(epa_relationships), 2)

    def test_graph_validation_rules(self):
        """Test SFM-specific validation rules."""
        # Test that Policy nodes go to policies collection, not institutions
        policy = Policy(label="Test Policy", authority="Government")
        self.graph.add_node(policy)

        self.assertEqual(len(self.graph.policies), 1)
        self.assertEqual(len(self.graph.institutions), 1)  # setUp added 1 institution
        self.assertIn(policy.id, self.graph.policies)

        # Test that ValueFlow goes to value_flows, not flows
        value_flow = ValueFlow(label="Test Value Flow", value_created=100.0)
        self.graph.add_node(value_flow)

        self.assertEqual(len(self.graph.value_flows), 1)
        self.assertEqual(len(self.graph.flows), 1)  # setUp added 1 flow
        self.assertIn(value_flow.id, self.graph.value_flows)

    def test_graph_serialization_preparation(self):
        """Test preparing graph data for serialization."""
        # Add various nodes and relationships
        self.graph.add_node(self.actor)
        self.graph.add_node(self.institution)
        self.graph.add_relationship(self.relationship)

        # Test that all nodes have serializable data
        for node in self.graph:
            node_dict = dict(node)
            self.assertIn("id", node_dict)
            self.assertIn("label", node_dict)
            self.assertIsInstance(node_dict["id"], uuid.UUID)
            self.assertIsInstance(node_dict["label"], str)

        # Test relationship data
        for rel in self.graph.relationships.values():
            self.assertIsInstance(rel.id, uuid.UUID)
            self.assertIsInstance(rel.source_id, uuid.UUID)
            self.assertIsInstance(rel.target_id, uuid.UUID)
            self.assertIsInstance(rel.kind, RelationshipKind)

    def test_graph_bulk_operations(self):
        """Test bulk operations on the graph."""
        # Test bulk node addition
        nodes = [
            Actor(label=f"Actor {i}") for i in range(10)
        ] + [
            Institution(label=f"Institution {i}") for i in range(5)
        ] + [
            Resource(label=f"Resource {i}") for i in range(15)
        ]

        # Add all nodes
        for node in nodes:
            self.graph.add_node(node)
        self.assertEqual(len(self.graph), 35)  # 30 new + 5 from setUp
        self.assertEqual(len(self.graph.actors), 11)  # 10 new + 1 from setUp
        self.assertEqual(len(self.graph.institutions), 6)  # 5 new + 1 from setUp
        self.assertEqual(len(self.graph.resources), 16)  # 15 new + 1 from setUp

        # Test bulk relationship creation
        relationships = []
        actor_ids = list(self.graph.actors.keys())
        institution_ids = list(self.graph.institutions.keys())

        # Create relationships between actors and institutions
        for actor_id in actor_ids[:5]:  # First 5 actors
            for institution_id in institution_ids[:3]:  # First 3 institutions
                rel = Relationship(
                    source_id=actor_id,
                    target_id=institution_id,
                    kind=RelationshipKind.PARTICIPATES_IN,
                    weight=0.5                )
                relationships.append(rel)
                self.graph.add_relationship(rel)

        expected_relationships = 5 * 3 + 1  # 5 actors × 3 institutions + 1 from setUp
        self.assertEqual(len(self.graph.relationships), expected_relationships)


class TestSFMBusinessLogic(unittest.TestCase):
    """Test SFM-specific business logic and domain rules."""

    def setUp(self):
        """Set up test fixtures for SFM business logic tests."""
        self.graph = SFMGraph()
        self.graph.name = "Business Logic Test Graph"

    def test_hayden_institutional_layers(self):
        """Test Hayden's three-layer institutional framework."""
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

        # Add to graph
        for institution in [formal_rule, organization, informal_norm]:
            self.graph.add_node(institution)

        # Verify institutional layers
        self.assertEqual(formal_rule.layer, InstitutionLayer.FORMAL_RULE)
        self.assertEqual(organization.layer, InstitutionLayer.ORGANIZATION)
        self.assertEqual(informal_norm.layer, InstitutionLayer.INFORMAL_NORM)

        # Test that formal rules exist where expected
        self.assertGreater(len(formal_rule.formal_rules), 0)
        self.assertGreater(len(formal_rule.enforcement_mechanisms), 0)
        self.assertGreater(len(informal_norm.informal_norms), 0)

    def test_ceremonial_vs_instrumental_dichotomy(self):
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

        # Test that ceremonial behavior shows resistance characteristics
        self.assertGreater(ceremonial.rigidity_level or 0, 0.5)
        self.assertGreater(ceremonial.resistance_to_change or 0, 0.5)

        # Test that instrumental behavior shows adaptive characteristics
        self.assertGreater(instrumental.efficiency_measure or 0, 0.5)
        self.assertGreater(instrumental.adaptability_score or 0, 0.5)

    def test_value_flow_tracking(self):
        """Test value creation, capture, and distribution tracking."""
        # Create actors with different power resources
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

        government = Actor(
            label="Regulatory Agency",
            legal_form="Government Agency",
            power_resources={"political": 0.8, "legal": 0.9}
        )

        # Create value flow showing distributional impacts
        value_flow = ValueFlow(
            label="Energy Project Benefits",
            nature=FlowNature.OUTPUT,
            quantity=1000000.0,  # $1M in benefits
            unit="USD",
            value_created=1000000.0,
            value_captured=600000.0,  # 60% captured
            beneficiary_actors=[corporation.id, community.id, government.id],
            distributional_impact={
                "corporation": 0.7,  # 70% to corporation
                "community": 0.2,    # 20% to community
                "government": 0.1    # 10% to government (taxes)
            }
        )

        # Add to graph
        for actor in [corporation, community, government]:
            self.graph.add_node(actor)
        self.graph.add_node(value_flow)

        # Test value distribution logic
        total_distribution = sum(value_flow.distributional_impact.values())
        self.assertAlmostEqual(total_distribution, 1.0, places=2)

        # Test that value captured <= value created
        self.assertLessEqual(value_flow.value_captured or 0, value_flow.value_created or 0)

    def test_policy_instrument_effectiveness(self):
        """Test policy instrument design and effectiveness measurement."""
        # Create different types of policy instruments
        regulatory_instrument = PolicyInstrument(
            label="Emissions Standards",
            instrument_type=PolicyInstrumentType.REGULATORY,
            target_behavior="emissions reduction",
            compliance_mechanism="mandatory_standards",
            effectiveness_measure=0.75
        )

        economic_instrument = PolicyInstrument(
            label="Carbon Tax",
            instrument_type=PolicyInstrumentType.ECONOMIC,
            target_behavior="carbon pricing",
            compliance_mechanism="price_signals",
            effectiveness_measure=0.65
        )

        voluntary_instrument = PolicyInstrument(
            label="Green Certification",
            instrument_type=PolicyInstrumentType.VOLUNTARY,
            target_behavior="sustainable practices",
            compliance_mechanism="reputation_incentives",
            effectiveness_measure=0.45
        )

        information_instrument = PolicyInstrument(
            label="Energy Labeling",
            instrument_type=PolicyInstrumentType.INFORMATION,
            target_behavior="informed_choices",
            compliance_mechanism="disclosure_requirements",
            effectiveness_measure=0.55
        )

        instruments = [regulatory_instrument, economic_instrument,
                      voluntary_instrument, information_instrument]

        for instrument in instruments:
            self.graph.add_node(instrument)

        # Test instrument type validation
        valid_types = [
            PolicyInstrumentType.REGULATORY,
            PolicyInstrumentType.ECONOMIC,
            PolicyInstrumentType.VOLUNTARY,
            PolicyInstrumentType.INFORMATION
        ]
        for instrument in instruments:
            self.assertIn(instrument.instrument_type, valid_types)

        # Test effectiveness measures are reasonable
        for instrument in instruments:
            effectiveness = instrument.effectiveness_measure or 0
            self.assertGreaterEqual(effectiveness, 0.0)
            self.assertLessEqual(effectiveness, 1.0)

    def test_governance_structure_analysis(self):
        """Test governance structure analysis and power distribution."""
        # Create multi-level governance structure
        federal_governance = GovernanceStructure(
            label="Federal Environmental Governance",
            layer=InstitutionLayer.ORGANIZATION,
            decision_making_process="hierarchical",
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

        state_governance = GovernanceStructure(
            label="State Environmental Agency",
            layer=InstitutionLayer.ORGANIZATION,
            decision_making_process="federated",
            power_distribution={
                "state_agency": 0.6,
                "federal_delegation": 0.4
            },
            accountability_mechanisms=[
                "state_legislature_oversight",
                "federal_compliance_monitoring"
            ]
        )

        local_governance = GovernanceStructure(
            label="Local Environmental Board",
            layer=InstitutionLayer.ORGANIZATION,
            decision_making_process="participatory",
            power_distribution={
                "elected_officials": 0.4,
                "citizen_representatives": 0.3,
                "technical_experts": 0.3
            },
            accountability_mechanisms=[
                "public_hearings",
                "transparency_requirements",
                "citizen_appeals"
            ]
        )

        governance_structures = [federal_governance, state_governance, local_governance]

        for structure in governance_structures:
            self.graph.add_node(structure)

        # Test power distribution sums to 1.0
        for structure in governance_structures:
            total_power = sum(structure.power_distribution.values())
            self.assertAlmostEqual(total_power, 1.0, places=1)

        # Test accountability mechanisms exist
        for structure in governance_structures:
            self.assertGreater(len(structure.accountability_mechanisms), 0)

    def test_change_process_modeling(self):
        """Test institutional and technological change process modeling."""
        # Create different types of change processes
        evolutionary_change = ChangeProcess(
            label="Gradual Renewable Energy Adoption",
            change_type=ChangeType.EVOLUTIONARY,
            change_agents=[uuid.uuid4(), uuid.uuid4()],  # Market forces, technology advocates
            resistance_factors=[uuid.uuid4()],  # Fossil fuel interests
            change_trajectory=[
                TimeSlice(label="2020"),
                TimeSlice(label="2025"),
                TimeSlice(label="2030")
            ],
            success_probability=0.75
        )

        revolutionary_change = ChangeProcess(
            label="Rapid Decarbonization Policy",
            change_type=ChangeType.REVOLUTIONARY,
            change_agents=[uuid.uuid4()],  # Climate activists
            resistance_factors=[uuid.uuid4(), uuid.uuid4()],  # Industry, status quo
            change_trajectory=[
                TimeSlice(label="2025"),
                TimeSlice(label="2027")
            ],
            success_probability=0.35
        )

        cyclical_change = ChangeProcess(
            label="Regulatory Cycle",
            change_type=ChangeType.CYCLICAL,
            change_agents=[uuid.uuid4()],  # Political cycles
            resistance_factors=[],
            change_trajectory=[
                TimeSlice(label="2024"),
                TimeSlice(label="2028"),
                TimeSlice(label="2032")
            ],
            success_probability=0.85
        )

        change_processes = [evolutionary_change, revolutionary_change, cyclical_change]

        for process in change_processes:
            self.graph.add_node(process)

        # Test change type validity
        valid_change_types = [ChangeType.EVOLUTIONARY, ChangeType.REVOLUTIONARY, ChangeType.CYCLICAL]
        for process in change_processes:
            self.assertIn(process.change_type, valid_change_types)

        # Test success probability bounds
        for process in change_processes:
            prob = process.success_probability or 0
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)

        # Test that revolutionary change typically has more resistance
        self.assertGreater(
            len(revolutionary_change.resistance_factors),
            len(evolutionary_change.resistance_factors)
        )

    def test_cognitive_framework_influence(self):
        """Test cognitive framework influence on decision-making."""
        # Create different cognitive frameworks
        market_fundamentalism = CognitiveFramework(
            label="Market Fundamentalism",
            description="Belief in market efficiency and minimal regulation",
            framing_effects={
                "regulation": "market_distortion",
                "government": "inefficient",
                "private_sector": "efficient"
            },
            cognitive_biases=["confirmation_bias", "availability_heuristic"],
            information_filters=["economic_data", "market_signals"],
            learning_capacity=0.3  # Low learning capacity due to rigid beliefs
        )

        ecological_worldview = CognitiveFramework(
            label="Ecological Worldview",
            description="Systems thinking approach to environmental issues",
            framing_effects={
                "environment": "interconnected_system",
                "economy": "subset_of_ecology",
                "sustainability": "essential"
            },
            cognitive_biases=["systems_thinking", "precautionary_principle"],
            information_filters=["scientific_data", "ecological_indicators"],
            learning_capacity=0.8  # High learning capacity
        )

        frameworks = [market_fundamentalism, ecological_worldview]

        for framework in frameworks:
            self.graph.add_node(framework)

        # Test that framing effects are properly structured
        for framework in frameworks:
            self.assertGreater(len(framework.framing_effects), 0)
            for key, value in framework.framing_effects.items():
                self.assertIsInstance(key, str)
                self.assertIsInstance(value, str)

        # Test learning capacity differences
        self.assertLess(
            market_fundamentalism.learning_capacity or 0,
            ecological_worldview.learning_capacity or 0
        )

    def test_behavioral_pattern_analysis(self):
        """Test behavioral pattern identification and analysis."""
        # Create different behavioral patterns
        short_term_thinking = BehavioralPattern(
            label="Quarterly Earnings Focus",
            pattern_type=BehaviorPatternType.HABITUAL,
            frequency=4.0,  # 4 times per year
            predictability=0.9,
            context_dependency=["financial_markets", "investor_pressure"]
        )

        adaptive_learning = BehavioralPattern(
            label="Continuous Improvement",
            pattern_type=BehaviorPatternType.ADAPTIVE,
            frequency=12.0,  # Monthly reviews
            predictability=0.6,
            context_dependency=["performance_feedback", "external_changes"]
        )

        resistance_pattern = BehavioralPattern(
            label="Change Resistance",
            pattern_type=BehaviorPatternType.RESISTANT,
            frequency=1.0,  # Constant resistance
            predictability=0.8,
            context_dependency=["organizational_culture", "job_security_fears"]
        )

        strategic_planning = BehavioralPattern(
            label="Long-term Strategic Planning",
            pattern_type=BehaviorPatternType.STRATEGIC,
            frequency=1.0,  # Annual planning
            predictability=0.7,
            context_dependency=["leadership_vision", "stakeholder_expectations"]
        )

        patterns = [short_term_thinking, adaptive_learning, resistance_pattern, strategic_planning]

        for pattern in patterns:
            self.graph.add_node(pattern)

        # Test pattern type validity
        valid_pattern_types = [
            BehaviorPatternType.HABITUAL,
            BehaviorPatternType.STRATEGIC,
            BehaviorPatternType.ADAPTIVE,
            BehaviorPatternType.RESISTANT
        ]
        for pattern in patterns:
            self.assertIn(pattern.pattern_type, valid_pattern_types)

        # Test that context dependencies exist
        for pattern in patterns:
            self.assertGreater(len(pattern.context_dependency), 0)

        # Test frequency and predictability bounds
        for pattern in patterns:
            self.assertGreater(pattern.frequency or 0, 0)
            self.assertGreaterEqual(pattern.predictability or 0, 0.0)
            self.assertLessEqual(pattern.predictability or 1, 1.0)

    def test_integrated_sfm_scenario(self):
        """Test an integrated SFM scenario with multiple interacting components."""
        # Create a complete SFM scenario: Carbon pricing policy implementation

        # Actors
        government = Actor(
            label="Federal Government",
            power_resources={"political": 0.9, "legal": 1.0}
        )

        industry = Actor(
            label="Industrial Association",
            power_resources={"economic": 0.8, "political": 0.6}
        )

        # Institutions
        carbon_pricing_law = Policy(
            label="Carbon Pricing Act",
            authority="Federal Government",
            layer=InstitutionLayer.FORMAL_RULE,
            enforcement=0.8
        )

        # Policy Instruments
        carbon_tax = PolicyInstrument(
            label="Carbon Tax",
            instrument_type=PolicyInstrumentType.ECONOMIC,
            effectiveness_measure=0.7
        )

        # Behavioral responses
        industry_adaptation = InstrumentalBehavior(
            label="Technology Investment",
            efficiency_measure=0.6,
            innovation_potential=0.7
        )

        industry_resistance = CeremonialBehavior(
            label="Regulatory Resistance",
            rigidity_level=0.8,
            resistance_to_change=0.9
        )

        # Value flows
        compliance_costs = ValueFlow(
            label="Compliance Costs",
            nature=FlowNature.OUTPUT,
            value_created=-500000.0,  # Negative value (cost)
            distributional_impact={"industry": 1.0}
        )

        # Change process
        policy_implementation = ChangeProcess(
            label="Carbon Policy Implementation",
            change_type=ChangeType.EVOLUTIONARY,
            success_probability=0.65
        )

        # Add all components to graph
        components = [
            government, industry, carbon_pricing_law, carbon_tax,
            industry_adaptation, industry_resistance, compliance_costs,
            policy_implementation
        ]
        for component in components:
            self.graph.add_node(component)

        # Create relationships
        relationships = [
            Relationship(government.id, carbon_pricing_law.id, RelationshipKind.ENACTS),
            Relationship(carbon_pricing_law.id, carbon_tax.id, RelationshipKind.IMPLEMENTS),
            Relationship(carbon_tax.id, industry.id, RelationshipKind.AFFECTS),
            Relationship(industry.id, industry_adaptation.id, RelationshipKind.INFLUENCES),
            Relationship(industry.id, industry_resistance.id, RelationshipKind.INFLUENCES),
            Relationship(carbon_tax.id, compliance_costs.id, RelationshipKind.PRODUCES),
        ]

        for rel in relationships:
            self.graph.add_relationship(rel)

        # Test integrated scenario
        self.assertEqual(len(self.graph), len(components))
        self.assertEqual(len(self.graph.relationships), len(relationships))

        # Test that all node types are properly categorized
        self.assertEqual(len(self.graph.actors), 2)
        self.assertEqual(len(self.graph.policies), 1)
        self.assertEqual(len(self.graph.policy_instruments), 1)
        self.assertEqual(len(self.graph.instrumental_behaviors), 1)
        self.assertEqual(len(self.graph.ceremonial_behaviors), 1)
        self.assertEqual(len(self.graph.value_flows), 1)
        self.assertEqual(len(self.graph.change_processes), 1)
          # Test that relationships form a coherent policy network
        policy_relationships = [
            rel for rel in self.graph.relationships.values()
            if rel.kind in [RelationshipKind.ENACTS, RelationshipKind.IMPLEMENTS,
                           RelationshipKind.AFFECTS, RelationshipKind.INFLUENCES]
        ]
        self.assertEqual(len(policy_relationships), 5)  # ENACTS, IMPLEMENTS, AFFECTS, INFLUENCES, INFLUENCES (PRODUCES not included)


class TestNewClasses(unittest.TestCase):
    """Test suite for new classes added to the SFM data model"""

    def setUp(self):
        """Set up test fixtures."""
        # Create time slices for temporal dynamics
        start_time = TimeSlice(label="start_period_2024_H1")
        end_time = TimeSlice(label="end_period_2024_H2")

        self.temporal_dynamics = TemporalDynamics(
            start_time=start_time,
            end_time=end_time,
            function_type=TemporalFunctionType.LINEAR,
            parameters={"rate": 0.5, "offset": 0.1}
        )

        self.validation_rule = ValidationRule(
            rule_type=ValidationRuleType.RANGE,
            target_field="data_quality",
            parameters={"min_value": 0.5, "max_value": 1.0},
            error_message="Data quality must be between 0.5 and 1.0"
        )

        self.model_metadata = ModelMetadata(
            version="1.0.0",
            authors=["test_user"],
            creation_date=datetime.now(),
            last_modified=datetime.now(),
            description="Testing SFM model",
            change_log=["Initial version"]
        )

        self.network_metrics = NetworkMetrics(label="Test Network Metrics")
        # Set additional fields if they exist
        if hasattr(self.network_metrics, 'centrality_measures'):
            self.network_metrics.centrality_measures = {
                "betweenness": 0.5,
                "closeness": 0.7,
                "degree": 3.0
            }
        if hasattr(self.network_metrics, 'clustering_coefficient'):
            self.network_metrics.clustering_coefficient = 0.4
        if hasattr(self.network_metrics, 'path_lengths'):
            self.network_metrics.path_lengths = {uuid.uuid4(): 2.5}
        if hasattr(self.network_metrics, 'community_assignment'):
            self.network_metrics.community_assignment = "cluster_1"

    def test_temporal_dynamics_creation(self):
        """Test creation of TemporalDynamics objects."""
        self.assertIsNotNone(self.temporal_dynamics.start_time)
        self.assertIsNotNone(self.temporal_dynamics.end_time)
        # function_type may be an Enum or str, so compare by value
        expected_type = getattr(self.temporal_dynamics.function_type, 'value', self.temporal_dynamics.function_type)
        self.assertEqual(expected_type, TemporalFunctionType.LINEAR.value)
        self.assertEqual(self.temporal_dynamics.parameters["rate"], 0.5)
        self.assertEqual(self.temporal_dynamics.parameters["offset"], 0.1)

    def test_temporal_dynamics_required_fields(self):
        """Test that TemporalDynamics requires certain fields."""
        # Test with minimal required fields
        start_time = TimeSlice(label="minimal_start")
        minimal = TemporalDynamics(start_time=start_time)
        self.assertEqual(minimal.start_time.label, "minimal_start")
        self.assertIsNone(minimal.end_time)
        # function_type may be an Enum or str, so compare by value
        expected_type = getattr(minimal.function_type, 'value', minimal.function_type)
        self.assertEqual(expected_type, TemporalFunctionType.LINEAR.value)

    def test_validation_rule_creation(self):
        """Test creation of ValidationRule objects."""
        self.assertEqual(self.validation_rule.rule_type, ValidationRuleType.RANGE)
        self.assertEqual(self.validation_rule.target_field, "data_quality")
        self.assertEqual(self.validation_rule.parameters["min_value"], 0.5)
        self.assertEqual(self.validation_rule.parameters["max_value"], 1.0)
        self.assertEqual(self.validation_rule.error_message, "Data quality must be between 0.5 and 1.0")

    def test_validation_rule_required_fields(self):
        """Test that ValidationRule requires certain fields."""
        # Test with minimal required fields
        minimal = ValidationRule(
            rule_type=ValidationRuleType.REQUIRED,
            target_field="label"
        )
        self.assertEqual(minimal.rule_type, ValidationRuleType.REQUIRED)
        self.assertEqual(minimal.target_field, "label")
        self.assertEqual(minimal.error_message, "")

    def test_model_metadata_creation(self):
        """Test creation of ModelMetadata objects."""
        self.assertEqual(self.model_metadata.version, "1.0.0")
        self.assertIn("test_user", self.model_metadata.authors)
        self.assertIsInstance(self.model_metadata.creation_date, datetime)
        self.assertIsInstance(self.model_metadata.last_modified, datetime)
        self.assertEqual(self.model_metadata.description, "Testing SFM model")
        self.assertIn("Initial version", self.model_metadata.change_log)

    def test_model_metadata_required_fields(self):
        """Test that ModelMetadata requires certain fields."""
        # Test with minimal required fields
        minimal = ModelMetadata(version="0.1.0")
        self.assertEqual(minimal.version, "0.1.0")
        self.assertEqual(len(minimal.authors), 0)
        self.assertEqual(minimal.description, "")

    def test_network_metrics_creation(self):
        """Test creation of NetworkMetrics objects."""
        self.assertEqual(self.network_metrics.label, "Test Network Metrics")
        self.assertEqual(self.network_metrics.centrality_measures["betweenness"], 0.5)
        self.assertEqual(self.network_metrics.centrality_measures["closeness"], 0.7)
        self.assertEqual(self.network_metrics.centrality_measures["degree"], 3.0)
        self.assertEqual(self.network_metrics.clustering_coefficient, 0.4)
        self.assertEqual(self.network_metrics.community_assignment, "cluster_1")

    def test_network_metrics_required_fields(self):
        """Test that NetworkMetrics requires certain fields."""
        # Test with minimal required fields
        minimal = NetworkMetrics(label="Minimal Metrics")
        self.assertEqual(minimal.label, "Minimal Metrics")
        self.assertEqual(len(minimal.centrality_measures), 0)
        self.assertIsNone(minimal.clustering_coefficient)


class TestEnhancedNodeFields(unittest.TestCase):
    """Test suite for enhanced Node class with new fields"""

    def setUp(self):
        """Set up test fixtures."""
        # Create a node with enhanced fields
        self.enhanced_node = Actor(
            label="Enhanced Actor",
            version=2,
            certainty=0.8,
            data_quality="high",
            previous_version_id=uuid.uuid4()
        )

    def test_node_version_field(self):
        """Test version field in Node."""
        self.assertEqual(self.enhanced_node.version, 2)

        # Test default version
        default_node = Actor(label="Default Actor")
        self.assertEqual(default_node.version, 1)

    def test_node_certainty_field(self):
        """Test certainty field in Node."""
        self.assertEqual(self.enhanced_node.certainty, 0.8)

        # Test default certainty
        default_node = Actor(label="Default Actor")
        self.assertEqual(default_node.certainty, 1.0)

    def test_node_data_quality_field(self):
        """Test data_quality field in Node."""
        self.assertEqual(self.enhanced_node.data_quality, "high")

        # Test default data quality
        default_node = Actor(label="Default Actor")
        self.assertIsNone(default_node.data_quality)

    def test_node_previous_version_id_field(self):
        """Test previous_version_id field in Node."""
        self.assertIsNotNone(self.enhanced_node.previous_version_id)

        # Test default previous version id
        default_node = Actor(label="Default Actor")
        self.assertIsNone(default_node.previous_version_id)

    def test_node_timestamps(self):
        """Test timestamp fields in Node."""
        self.assertIsInstance(self.enhanced_node.created_at, datetime)
        self.assertIsNone(self.enhanced_node.modified_at)

    def test_node_certainty_validation(self):
        """Test that certainty is within valid range."""
        # Valid certainty values
        valid_node = Actor(label="Valid", certainty=0.5)
        self.assertEqual(valid_node.certainty, 0.5)

        # Edge cases
        edge_node_low = Actor(label="Edge Low", certainty=0.0)
        self.assertEqual(edge_node_low.certainty, 0.0)

        edge_node_high = Actor(label="Edge High", certainty=1.0)
        self.assertEqual(edge_node_high.certainty, 1.0)

    def test_node_data_quality_string(self):
        """Test that data_quality accepts string values."""
        # Valid data quality values
        valid_node = Actor(label="Valid", data_quality="medium")
        self.assertEqual(valid_node.data_quality, "medium")

        # Various quality descriptions
        low_quality = Actor(label="Low Quality", data_quality="low - incomplete data")
        self.assertEqual(low_quality.data_quality, "low - incomplete data")


class TestEnhancedRelationshipFields(unittest.TestCase):
    """Test suite for enhanced Relationship class with new fields"""

    def setUp(self):
        """Set up test fixtures."""
        start_time = TimeSlice(label="test_start")
        self.temporal_dynamics = TemporalDynamics(
            start_time=start_time,
            function_type=TemporalFunctionType.EXPONENTIAL,
            parameters={"growth_rate": 0.3}
        )

        # Create nodes for relationships
        self.source_node = Actor(label="Source Actor")
        self.target_node = Actor(label="Target Actor")

        # Create enhanced relationship
        self.enhanced_relationship = Relationship(
            source_id=self.source_node.id,
            target_id=self.target_node.id,
            kind=RelationshipKind.GOVERNS,
            version=2,
            certainty=0.7,
            data_quality="good",
            previous_version_id=uuid.uuid4(),
            temporal_dynamics=self.temporal_dynamics
        )

    def test_relationship_version_field(self):
        """Test version field in Relationship."""
        self.assertEqual(self.enhanced_relationship.version, 2)

        # Test default version
        default_rel = Relationship(
            source_id=self.source_node.id,
            target_id=self.target_node.id,
            kind=RelationshipKind.USES
        )
        self.assertEqual(default_rel.version, 1)

    def test_relationship_certainty_field(self):
        """Test certainty field in Relationship."""
        self.assertEqual(self.enhanced_relationship.certainty, 0.7)

        # Test default certainty
        default_rel = Relationship(
            source_id=self.source_node.id,
            target_id=self.target_node.id,
            kind=RelationshipKind.USES
        )
        self.assertEqual(default_rel.certainty, 1.0)

    def test_relationship_data_quality_field(self):
        """Test data_quality field in Relationship."""
        self.assertEqual(self.enhanced_relationship.data_quality, "good")

        # Test default data quality
        default_rel = Relationship(
            source_id=self.source_node.id,
            target_id=self.target_node.id,
            kind=RelationshipKind.USES
        )
        self.assertIsNone(default_rel.data_quality)

    def test_relationship_previous_version_id_field(self):
        """Test previous_version_id field in Relationship."""
        self.assertIsNotNone(self.enhanced_relationship.previous_version_id)

        # Test default previous version id
        default_rel = Relationship(
            source_id=self.source_node.id,
            target_id=self.target_node.id,
            kind=RelationshipKind.USES
        )
        self.assertIsNone(default_rel.previous_version_id)

    def test_relationship_temporal_dynamics_field(self):
        """Test temporal_dynamics field in Relationship."""
        td = self.enhanced_relationship.temporal_dynamics
        self.assertIsNotNone(td)
        if td is not None:
            expected_type = getattr(td.function_type, 'value', td.function_type)
            self.assertEqual(expected_type, TemporalFunctionType.EXPONENTIAL.value)
            self.assertEqual(td.parameters["growth_rate"], 0.3)

        # Test default temporal dynamics
        default_rel = Relationship(
            source_id=self.source_node.id,
            target_id=self.target_node.id,
            kind=RelationshipKind.USES
        )
        self.assertIsNone(default_rel.temporal_dynamics)


class TestEnhancedSFMGraph(unittest.TestCase):
    """Test suite for enhanced SFMGraph class with new fields"""

    def setUp(self):
        """Set up test fixtures."""
        self.model_metadata = ModelMetadata(
            version="2.0.0",
            authors=["test_enhanced"]
        )

        self.validation_rule = ValidationRule(
            rule_type=ValidationRuleType.REQUIRED,
            target_field="label"
        )

        # Create enhanced graph
        self.enhanced_graph = SFMGraph(
            model_metadata=self.model_metadata,
            validation_rules=[self.validation_rule]
        )

    def test_sfm_graph_model_metadata_field(self):
        """Test model_metadata field in SFMGraph."""
        self.assertIsNotNone(self.enhanced_graph.model_metadata)
        self.assertEqual(self.enhanced_graph.model_metadata.version, "2.0.0") #type: ignore check in previous step for none
        self.assertIn("test_enhanced", self.enhanced_graph.model_metadata.authors) #type: ignore check in previous step for none

        # Test default model metadata
        default_graph = SFMGraph()
        self.assertIsNone(default_graph.model_metadata)

    def test_sfm_graph_validation_rules_field(self):
        """Test validation_rules field in SFMGraph."""
        self.assertIsNotNone(self.enhanced_graph.validation_rules)
        self.assertEqual(len(self.enhanced_graph.validation_rules), 1)
        self.assertEqual(self.enhanced_graph.validation_rules[0].rule_type, ValidationRuleType.REQUIRED)
        self.assertEqual(self.enhanced_graph.validation_rules[0].target_field, "label")

        # Test default validation rules
        default_graph = SFMGraph()
        self.assertEqual(len(default_graph.validation_rules), 0)

    def test_sfm_graph_network_metrics_collection(self):
        """Test network_metrics collection in SFMGraph."""
        self.assertIsInstance(self.enhanced_graph.network_metrics, dict)
        self.assertEqual(len(self.enhanced_graph.network_metrics), 0)

        # Add a network metrics node
        metrics = NetworkMetrics(label="Test Metrics")
        self.enhanced_graph.add_node(metrics)

        self.assertEqual(len(self.enhanced_graph.network_metrics), 1)
        self.assertIn(metrics.id, self.enhanced_graph.network_metrics)

    def test_sfm_graph_versioning_fields(self):
        """Test versioning fields in SFMGraph."""
        self.assertEqual(self.enhanced_graph.version, 1)
        self.assertIsInstance(self.enhanced_graph.created_at, datetime)
        self.assertIsNone(self.enhanced_graph.modified_at)
        self.assertIsNone(self.enhanced_graph.data_quality)
        self.assertIsNone(self.enhanced_graph.previous_version_id)


class TestTemporalDynamicsIntegration(unittest.TestCase):
    """Test suite for integration of temporal dynamics with other classes"""

    def setUp(self):
        """Set up test fixtures."""
        start_time = TimeSlice(label="integration_start")
        self.temporal_dynamics = TemporalDynamics(
            start_time=start_time,
            function_type=TemporalFunctionType.LOGISTIC,
            parameters={"rate": 0.4, "capacity": 100.0}
        )

    def test_flow_with_temporal_dynamics(self):
        """Test Flow class with temporal_dynamics field."""
        flow = Flow(
            label="Dynamic Flow",
            nature=FlowNature.TRANSFER,
            temporal_dynamics=self.temporal_dynamics
        )

        td = flow.temporal_dynamics
        self.assertIsNotNone(td)
        if td is not None:
            expected_type = getattr(td.function_type, 'value', td.function_type)
            self.assertEqual(expected_type, TemporalFunctionType.LOGISTIC.value)
            self.assertEqual(td.parameters["rate"], 0.4)

    def test_indicator_with_temporal_dynamics(self):
        """Test Indicator class with temporal_dynamics field."""
        indicator = Indicator(
            label="Dynamic Indicator",
            temporal_dynamics=self.temporal_dynamics
        )

        td = indicator.temporal_dynamics
        self.assertIsNotNone(td)
        if td is not None:
            self.assertEqual(td.parameters["capacity"], 100.0)

    def test_relationship_with_temporal_dynamics(self):
        """Test Relationship class with temporal_dynamics field."""
        source_node = Actor(label="Source")
        target_node = Actor(label="Target")

        relationship = Relationship(
            source_id=source_node.id,
            target_id=target_node.id,
            kind=RelationshipKind.AFFECTS,
            temporal_dynamics=self.temporal_dynamics
        )

        td = relationship.temporal_dynamics
        self.assertIsNotNone(td)
        if td is not None:
            self.assertEqual(td.start_time.label, "integration_start")
            expected_type = getattr(td.function_type, 'value', td.function_type)
            self.assertEqual(expected_type,TemporalFunctionType.LOGISTIC.value)


class TestValidationRulesIntegration(unittest.TestCase):
    """Test suite for integration of validation rules with other classes"""

    def setUp(self):
        """Set up test fixtures."""
        self.validation_rule1 = ValidationRule(
            rule_type=ValidationRuleType.RANGE,
            target_field="data_quality",
            parameters={"min_value": 0.7},
            error_message="Data quality must be >= 0.7"
        )

        self.validation_rule2 = ValidationRule(
            rule_type=ValidationRuleType.REQUIRED,
            target_field="label",
            error_message="Label is required"
        )

    def test_analytical_context_with_validation_rules(self):
        """Test AnalyticalContext class with validation_rules field."""
        context = AnalyticalContext(label="Validated Context")
        context.validation_rules = [self.validation_rule1, self.validation_rule2]

        self.assertEqual(len(context.validation_rules), 2)
        self.assertEqual(context.validation_rules[0].rule_type, ValidationRuleType.RANGE)
        self.assertEqual(context.validation_rules[1].rule_type, ValidationRuleType.REQUIRED)

    def test_sfm_graph_with_validation_rules(self):
        """Test SFMGraph class with validation_rules field."""
        graph = SFMGraph(validation_rules=[self.validation_rule1])

        self.assertEqual(len(graph.validation_rules), 1)
        self.assertEqual(graph.validation_rules[0].target_field, "data_quality")
        self.assertEqual(graph.validation_rules[0].error_message, "Data quality must be >= 0.7")
