"""
Test suite for Hayden SFM Framework alignment enhancements.

Tests the new ceremonial/instrumental categorization, power dynamics,
tool-skill-technology complex, and path dependency features.
"""

import unittest
import sys
import os

# Add the current directory to the path to import directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import directly from the sfm_enums file to avoid networkx dependency
from models.sfm_enums import (
    RelationshipKind,
    PowerResourceType,
    ToolSkillTechnologyType,
    PathDependencyType, 
    InstitutionalChangeType
)


class TestCeremonialInstrumentalAlignment(unittest.TestCase):
    """Test suite for ceremonial vs instrumental categorization."""
    
    def test_ceremonial_tendency_property_exists(self):
        """Test that ceremonial_tendency property exists on RelationshipKind."""
        # Test some relationships that should have the property
        relationship = RelationshipKind.CEREMONIALLY_REINFORCES
        self.assertTrue(hasattr(relationship, 'ceremonial_tendency'))
        
    def test_ceremonial_tendency_returns_float(self):
        """Test that ceremonial_tendency returns a float between 0.0 and 1.0."""
        relationship = RelationshipKind.CEREMONIALLY_REINFORCES
        tendency = relationship.ceremonial_tendency
        self.assertIsInstance(tendency, float)
        self.assertGreaterEqual(tendency, 0.0)
        self.assertLessEqual(tendency, 1.0)
        
    def test_ceremonially_reinforces_high_ceremonial(self):
        """Test that CEREMONIALLY_REINFORCES has high ceremonial tendency."""
        tendency = RelationshipKind.CEREMONIALLY_REINFORCES.ceremonial_tendency
        self.assertGreater(tendency, 0.7)  # Should be highly ceremonial
        
    def test_instrumentally_adapts_low_ceremonial(self):
        """Test that INSTRUMENTALLY_ADAPTS has low ceremonial tendency."""
        tendency = RelationshipKind.INSTRUMENTALLY_ADAPTS.ceremonial_tendency
        self.assertLess(tendency, 0.3)  # Should be highly instrumental (low ceremonial)
        
    def test_mixed_relationships_have_intermediate_values(self):
        """Test that mixed relationships have intermediate ceremonial tendency values."""
        # Test some relationships that should be in the middle
        governs_tendency = RelationshipKind.GOVERNS.ceremonial_tendency
        produces_tendency = RelationshipKind.PRODUCES.ceremonial_tendency
        
        # GOVERNS should be somewhat ceremonial (institutional authority)
        self.assertGreater(governs_tendency, 0.4)
        self.assertLess(governs_tendency, 0.8)
        
        # PRODUCES should be more instrumental (productive activity)
        self.assertGreater(produces_tendency, 0.1)
        self.assertLess(produces_tendency, 0.6)


class TestPowerResourceType(unittest.TestCase):
    """Test suite for PowerResourceType enum."""
    
    def test_power_resource_types_exist(self):
        """Test that all required power resource types exist."""
        required_types = [
            'INSTITUTIONAL_AUTHORITY',
            'ECONOMIC_CONTROL', 
            'INFORMATION_ACCESS',
            'NETWORK_POSITION',
            'CULTURAL_LEGITIMACY'
        ]
        
        for power_type in required_types:
            self.assertTrue(
                hasattr(PowerResourceType, power_type),
                f"PowerResourceType.{power_type} should exist"
            )
            
    def test_power_resource_type_enum_properties(self):
        """Test basic enum properties of PowerResourceType."""
        # Test that it's an enum with auto() values
        self.assertTrue(hasattr(PowerResourceType, '__members__'))
        self.assertGreater(len(PowerResourceType.__members__), 0)
        
        # Test a specific member
        authority = PowerResourceType.INSTITUTIONAL_AUTHORITY
        self.assertIsInstance(authority, PowerResourceType)


class TestToolSkillTechnologyType(unittest.TestCase):
    """Test suite for ToolSkillTechnologyType enum."""
    
    def test_tool_skill_technology_types_exist(self):
        """Test that tool-skill-technology complex types exist."""
        # Basic categories that should exist
        expected_types = [
            'PHYSICAL_TOOL',
            'COGNITIVE_SKILL', 
            'TECHNOLOGY_SYSTEM',
            'TECHNIQUE',
            'METHODOLOGY'
        ]
        
        for tst_type in expected_types:
            self.assertTrue(
                hasattr(ToolSkillTechnologyType, tst_type),
                f"ToolSkillTechnologyType.{tst_type} should exist"
            )
            
    def test_tool_skill_technology_enum_properties(self):
        """Test basic enum properties of ToolSkillTechnologyType."""
        self.assertTrue(hasattr(ToolSkillTechnologyType, '__members__'))
        self.assertGreater(len(ToolSkillTechnologyType.__members__), 0)


class TestPathDependencyType(unittest.TestCase):
    """Test suite for PathDependencyType enum."""
    
    def test_path_dependency_types_exist(self):
        """Test that path dependency types exist."""
        expected_types = [
            'WEAK',
            'MODERATE', 
            'STRONG',
            'LOCKED_IN'
        ]
        
        for pd_type in expected_types:
            self.assertTrue(
                hasattr(PathDependencyType, pd_type),
                f"PathDependencyType.{pd_type} should exist"
            )
            
    def test_path_dependency_enum_properties(self):
        """Test basic enum properties of PathDependencyType."""
        self.assertTrue(hasattr(PathDependencyType, '__members__'))
        self.assertGreater(len(PathDependencyType.__members__), 0)


class TestInstitutionalChangeType(unittest.TestCase):
    """Test suite for InstitutionalChangeType enum."""
    
    def test_institutional_change_types_exist(self):
        """Test that institutional change mechanism types exist."""
        expected_types = [
            'INCREMENTAL',
            'TRANSFORMATIONAL',
            'REVOLUTIONARY', 
            'EVOLUTIONARY',
            'ADAPTIVE'
        ]
        
        for ic_type in expected_types:
            self.assertTrue(
                hasattr(InstitutionalChangeType, ic_type),
                f"InstitutionalChangeType.{ic_type} should exist"
            )
            
    def test_institutional_change_enum_properties(self):
        """Test basic enum properties of InstitutionalChangeType."""
        self.assertTrue(hasattr(InstitutionalChangeType, '__members__'))
        self.assertGreater(len(InstitutionalChangeType.__members__), 0)


class TestHaydenSFMIntegration(unittest.TestCase):
    """Test suite for integration of Hayden SFM concepts."""
    
    def test_all_new_enums_importable(self):
        """Test that all new enums can be imported successfully."""
        # All imports already done at module level
        
        # Basic validation that imports worked
        self.assertTrue(hasattr(PowerResourceType, 'INSTITUTIONAL_AUTHORITY'))
        self.assertTrue(hasattr(ToolSkillTechnologyType, 'PHYSICAL_TOOL'))
        self.assertTrue(hasattr(PathDependencyType, 'WEAK'))
        self.assertTrue(hasattr(InstitutionalChangeType, 'INCREMENTAL'))
        
    def test_ceremonial_tendency_comprehensive(self):
        """Test ceremonial tendency across different relationship categories."""
        # Sample different types of relationships
        governance_rel = RelationshipKind.GOVERNS
        economic_rel = RelationshipKind.PRODUCES
        ceremonial_rel = RelationshipKind.CEREMONIALLY_REINFORCES
        instrumental_rel = RelationshipKind.INSTRUMENTALLY_ADAPTS
        
        # All should have the property
        for rel in [governance_rel, economic_rel, ceremonial_rel, instrumental_rel]:
            self.assertTrue(hasattr(rel, 'ceremonial_tendency'))
            tendency = rel.ceremonial_tendency
            self.assertIsInstance(tendency, float)
            self.assertGreaterEqual(tendency, 0.0)
            self.assertLessEqual(tendency, 1.0)
            
        # Ceremonial should be higher than instrumental
        self.assertGreater(
            ceremonial_rel.ceremonial_tendency,
            instrumental_rel.ceremonial_tendency
        )


if __name__ == '__main__':
    unittest.main()