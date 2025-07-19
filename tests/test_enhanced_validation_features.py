"""
Test suite for enhanced enum validation features.

This module tests the new validation enhancements including:
- Enhanced suggestion algorithms
- Cross-entity consistency validation
- Business rule constraint validation
- Extended relationship validation rules
"""

import unittest
from models.sfm_enums import (
    EnumValidator,
    RelationshipKind,
    IncompatibleEnumError,
    InvalidEnumOperationError
)


class TestEnhancedSuggestions(unittest.TestCase):
    """Test suite for enhanced suggestion algorithms."""
    
    def test_semantic_suggestions_for_governance_relationships(self):
        """Test semantic suggestions for governance relationship types."""
        # Test governance relationship with invalid source
        suggestions = EnumValidator._generate_suggestions(
            RelationshipKind.REGULATES, 'Resource', 'Actor'
        )
        
        self.assertIn('Governance relationships like REGULATES', suggestions)
        self.assertIn('typically require Actor, Institution, or Policy', suggestions)
    
    def test_business_logic_suggestions_for_transforms(self):
        """Test business logic suggestions for transformation relationships."""
        suggestions = EnumValidator._generate_suggestions(
            RelationshipKind.TRANSFORMS, 'Resource', 'Actor'
        )
        
        self.assertIn('Transformation typically requires active change agents', suggestions)
        self.assertIn('Process, TechnologySystem, or PolicyInstrument', suggestions)
    
    def test_entity_compatibility_suggestions(self):
        """Test entity compatibility suggestions."""
        suggestions = EnumValidator._generate_suggestions(
            RelationshipKind.INFLUENCES, 'Actor', 'Resource'
        )
        
        self.assertIn('Social entities (Actor, Institution)', suggestions)
        self.assertIn('structural entities (Resource, TechnologySystem)', suggestions)
    
    def test_suggestions_for_covered_relationships(self):
        """Test that existing covered relationships provide enhanced suggestions."""
        suggestions = EnumValidator._generate_suggestions(
            RelationshipKind.GOVERNS, 'Resource', 'Actor'
        )
        
        # Should include both original suggestions and enhanced suggestions
        self.assertIn('For Actor targets', suggestions)
        self.assertIn('Governance relationships like GOVERNS', suggestions)


class TestCrossEntityConsistency(unittest.TestCase):
    """Test suite for cross-entity consistency validation."""
    
    def test_authority_consistency_valid(self):
        """Test valid authority relationships."""
        # Should not raise exception
        EnumValidator.validate_cross_entity_consistency(
            'Actor', 'Institution', RelationshipKind.GOVERNS
        )
        
        EnumValidator.validate_cross_entity_consistency(
            'Institution', 'Resource', RelationshipKind.REGULATES
        )
    
    def test_authority_consistency_invalid(self):
        """Test invalid authority relationships."""
        # The basic relationship validation will catch this first,
        # but enhanced suggestions should be provided
        with self.assertRaises(IncompatibleEnumError) as context:
            EnumValidator.validate_cross_entity_consistency(
                'Resource', 'Actor', RelationshipKind.GOVERNS
            )
        
        error_msg = str(context.exception)
        # Should get the basic validation message with enhanced suggestions
        self.assertIn('GOVERNS relationship requires authority-capable entities', error_msg)
        self.assertIn('Governance relationships like GOVERNS', error_msg)
    
    def test_economic_consistency_valid(self):
        """Test valid economic relationships."""
        # Should not raise exception
        EnumValidator.validate_cross_entity_consistency(
            'Actor', 'Institution', RelationshipKind.FUNDS
        )
        
        EnumValidator.validate_cross_entity_consistency(
            'Institution', 'Actor', RelationshipKind.PAYS
        )
    
    def test_economic_consistency_invalid(self):
        """Test invalid economic relationships."""
        with self.assertRaises(IncompatibleEnumError) as context:
            EnumValidator.validate_cross_entity_consistency(
                'Flow', 'Actor', RelationshipKind.PAYS
            )
        
        error_msg = str(context.exception)
        self.assertIn('Economic inconsistency', error_msg)
        self.assertIn('requires economic actors', error_msg)
    
    def test_spatial_consistency_invalid(self):
        """Test invalid spatial relationships."""
        with self.assertRaises(IncompatibleEnumError) as context:
            EnumValidator.validate_cross_entity_consistency(
                'Flow', 'ValueFlow', RelationshipKind.CONNECTS, 'spatial'
            )
        
        error_msg = str(context.exception)
        self.assertIn('Spatial inconsistency', error_msg)
        self.assertIn('spatial anchor entities', error_msg)
    
    def test_invalid_parameters(self):
        """Test validation with invalid parameters."""
        with self.assertRaises(InvalidEnumOperationError):
            EnumValidator.validate_cross_entity_consistency(
                '', 'Actor', RelationshipKind.GOVERNS
            )


class TestBusinessRuleConstraints(unittest.TestCase):
    """Test suite for business rule constraint validation."""
    
    def test_environmental_domain_valid(self):
        """Test valid environmental domain constraints."""
        # Should not raise exception
        EnumValidator.validate_business_rule_constraints(
            RelationshipKind.REGULATES, 'Policy', 'Actor', 'environmental'
        )
        
        EnumValidator.validate_business_rule_constraints(
            RelationshipKind.REGULATES, 'Institution', 'Resource', 'environmental'
        )
    
    def test_environmental_domain_invalid(self):
        """Test invalid environmental domain constraints."""
        with self.assertRaises(IncompatibleEnumError) as context:
            EnumValidator.validate_business_rule_constraints(
                RelationshipKind.REGULATES, 'Policy', 'Flow', 'environmental'
            )
        
        error_msg = str(context.exception)
        self.assertIn('Environmental regulatory constraint', error_msg)
        self.assertIn('environmental impact', error_msg)
    
    def test_economic_domain_valid(self):
        """Test valid economic domain constraints."""
        # Should not raise exception
        EnumValidator.validate_business_rule_constraints(
            RelationshipKind.BUYS_FROM, 'Actor', 'Institution', 'economic'
        )
        
        EnumValidator.validate_business_rule_constraints(
            RelationshipKind.INVESTS_IN, 'Institution', 'Actor', 'economic'
        )
    
    def test_economic_domain_invalid(self):
        """Test invalid economic domain constraints."""
        with self.assertRaises(IncompatibleEnumError) as context:
            EnumValidator.validate_business_rule_constraints(
                RelationshipKind.BUYS_FROM, 'Resource', 'Actor', 'economic'
            )
        
        error_msg = str(context.exception)
        self.assertIn('Economic constraint', error_msg)
        self.assertIn('requires economic actors', error_msg)
    
    def test_social_domain_invalid(self):
        """Test invalid social domain constraints."""
        with self.assertRaises(IncompatibleEnumError) as context:
            EnumValidator.validate_business_rule_constraints(
                RelationshipKind.COLLABORATES_WITH, 'Resource', 'Actor', 'social'
            )
        
        error_msg = str(context.exception)
        self.assertIn('Social constraint', error_msg)
        self.assertIn('requires social entities', error_msg)
    
    def test_institutional_domain_invalid(self):
        """Test invalid institutional domain constraints."""
        with self.assertRaises(IncompatibleEnumError) as context:
            EnumValidator.validate_business_rule_constraints(
                RelationshipKind.IMPLEMENTS, 'Resource', 'Policy', 'institutional'
            )
        
        error_msg = str(context.exception)
        self.assertIn('Institutional constraint', error_msg)
        self.assertIn('Policy implementation requires', error_msg)
    
    def test_invalid_parameters(self):
        """Test validation with invalid parameters."""
        with self.assertRaises(InvalidEnumOperationError):
            EnumValidator.validate_business_rule_constraints(
                None, 'Actor', 'Institution', 'general'
            )


class TestExtendedRelationshipRules(unittest.TestCase):
    """Test suite for extended relationship validation rules."""
    
    def test_new_governance_relationships(self):
        """Test new governance relationship rules."""
        # REGULATES should work
        EnumValidator.validate_relationship_context(
            RelationshipKind.REGULATES, 'Institution', 'Actor'
        )
        
        # Should fail with invalid combination
        with self.assertRaises(IncompatibleEnumError):
            EnumValidator.validate_relationship_context(
                RelationshipKind.REGULATES, 'Flow', 'Resource'
            )
    
    def test_new_resource_flow_relationships(self):
        """Test new resource flow relationship rules."""
        # FUNDS should work
        EnumValidator.validate_relationship_context(
            RelationshipKind.FUNDS, 'Actor', 'Institution'
        )
        
        # SUPPLIES should work  
        EnumValidator.validate_relationship_context(
            RelationshipKind.SUPPLIES, 'Resource', 'Process'
        )
    
    def test_new_collaborative_relationships(self):
        """Test new collaborative relationship rules."""
        # COLLABORATES_WITH should work
        EnumValidator.validate_relationship_context(
            RelationshipKind.COLLABORATES_WITH, 'Actor', 'Actor'
        )
        
        # COORDINATES_WITH should work
        EnumValidator.validate_relationship_context(
            RelationshipKind.COORDINATES_WITH, 'Institution', 'Process'
        )
    
    def test_transformation_relationships(self):
        """Test transformation relationship rules."""
        # TRANSFORMS should work with valid combinations
        EnumValidator.validate_relationship_context(
            RelationshipKind.TRANSFORMS, 'Process', 'Resource'
        )
        
        # Should fail with invalid combinations
        with self.assertRaises(IncompatibleEnumError):
            EnumValidator.validate_relationship_context(
                RelationshipKind.TRANSFORMS, 'Resource', 'Flow'
            )
    
    def test_implementation_relationships(self):
        """Test implementation relationship rules."""
        # IMPLEMENTS should work with valid combinations
        EnumValidator.validate_relationship_context(
            RelationshipKind.IMPLEMENTS, 'Actor', 'Policy'
        )
        
        EnumValidator.validate_relationship_context(
            RelationshipKind.IMPLEMENTS, 'PolicyInstrument', 'Policy'
        )


if __name__ == '__main__':
    unittest.main()