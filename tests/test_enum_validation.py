"""
Test suite for SFM enum validation and error handling.

This module tests the error handling and validation utilities for SFM enums,
including custom exceptions, enum combination validation, and context-aware
relationship validation.
"""

import unittest
from models.sfm_enums import (
    SFMEnumError,
    IncompatibleEnumError, 
    InvalidEnumOperationError,
    EnumValidator,
    RelationshipKind,
    FlowNature,
    FlowType,
    InstitutionLayer,
    validate_enum_operation
)


class TestSFMEnumExceptions(unittest.TestCase):
    """Test suite for SFM enum exception hierarchy."""
    
    def test_exception_hierarchy(self):
        """Test that exception hierarchy is correctly structured."""
        # Test inheritance
        self.assertTrue(issubclass(IncompatibleEnumError, SFMEnumError))
        self.assertTrue(issubclass(InvalidEnumOperationError, SFMEnumError))
        self.assertTrue(issubclass(SFMEnumError, Exception))
        
        # Test exception creation
        base_error = SFMEnumError("Base error")
        self.assertEqual(str(base_error), "Base error")
        
        incompatible_error = IncompatibleEnumError("Incompatible enums")
        self.assertEqual(str(incompatible_error), "Incompatible enums")
        
        invalid_op_error = InvalidEnumOperationError("Invalid operation")
        self.assertEqual(str(invalid_op_error), "Invalid operation")


class TestRelationshipValidation(unittest.TestCase):
    """Test suite for relationship context validation."""
    
    def test_valid_governs_relationships(self):
        """Test valid GOVERNS relationship combinations."""
        valid_combinations = [
            ('Actor', 'Actor'),
            ('Actor', 'Institution'),
            ('Actor', 'Policy'),
            ('Actor', 'Resource'),
            ('Institution', 'Institution'),
            ('Institution', 'Actor'),
            ('Institution', 'Policy'),
            ('Institution', 'Resource'),
            ('Policy', 'Actor'),
            ('Policy', 'Institution'),
            ('Policy', 'Resource')
        ]
        
        for source_type, target_type in valid_combinations:
            with self.subTest(source=source_type, target=target_type):
                try:
                    EnumValidator.validate_relationship_context(
                        RelationshipKind.GOVERNS, source_type, target_type
                    )
                except Exception as e:
                    self.fail(f"Valid combination {source_type}->{target_type} raised {e}")
    
    def test_invalid_governs_relationships(self):
        """Test invalid GOVERNS relationship combinations."""
        invalid_combinations = [
            ('Resource', 'Actor'),
            ('Process', 'Resource'),
            ('Flow', 'Actor'),
            ('Resource', 'Resource'),
            ('Flow', 'Flow')
        ]
        
        for source_type, target_type in invalid_combinations:
            with self.subTest(source=source_type, target=target_type):
                with self.assertRaises(IncompatibleEnumError) as context:
                    EnumValidator.validate_relationship_context(
                        RelationshipKind.GOVERNS, source_type, target_type
                    )
                
                error_message = str(context.exception)
                self.assertIn("GOVERNS relationship requires", error_message)
                self.assertIn(f"{source_type}->{target_type}", error_message)
    
    def test_valid_employs_relationships(self):
        """Test valid EMPLOYS relationship combinations."""
        # Actor->Actor and Institution->Actor should be valid for EMPLOYS
        valid_combinations = [
            ('Actor', 'Actor'),
            ('Institution', 'Actor')
        ]
        
        for source_type, target_type in valid_combinations:
            with self.subTest(source=source_type, target=target_type):
                try:
                    EnumValidator.validate_relationship_context(
                        RelationshipKind.EMPLOYS, source_type, target_type
                    )
                except Exception as e:
                    self.fail(f"Valid EMPLOYS {source_type}->{target_type} raised {e}")
    
    def test_invalid_employs_relationships(self):
        """Test invalid EMPLOYS relationship combinations."""
        invalid_combinations = [
            ('Actor', 'Resource'),
            ('Process', 'Actor'),
            ('Actor', 'Institution'),
            ('Resource', 'Actor')
        ]
        
        for source_type, target_type in invalid_combinations:
            with self.subTest(source=source_type, target=target_type):
                with self.assertRaises(IncompatibleEnumError) as context:
                    EnumValidator.validate_relationship_context(
                        RelationshipKind.EMPLOYS, source_type, target_type
                    )
                
                error_message = str(context.exception)
                self.assertIn("EMPLOYS relationship requires", error_message)
    
    def test_valid_owns_relationships(self):
        """Test valid OWNS relationship combinations."""
        valid_combinations = [
            ('Actor', 'Resource'),
            ('Institution', 'Resource'),
            ('Actor', 'TechnologySystem'),
            ('Institution', 'TechnologySystem')
        ]
        
        for source_type, target_type in valid_combinations:
            with self.subTest(source=source_type, target=target_type):
                try:
                    EnumValidator.validate_relationship_context(
                        RelationshipKind.OWNS, source_type, target_type
                    )
                except Exception as e:
                    self.fail(f"Valid OWNS combination {source_type}->{target_type} raised {e}")
    
    def test_invalid_owns_relationships(self):
        """Test invalid OWNS relationship combinations."""
        invalid_combinations = [
            ('Resource', 'Actor'),
            ('Process', 'Resource'),
            ('Actor', 'Actor'),
            ('Flow', 'Resource')
        ]
        
        for source_type, target_type in invalid_combinations:
            with self.subTest(source=source_type, target=target_type):
                with self.assertRaises(IncompatibleEnumError) as context:
                    EnumValidator.validate_relationship_context(
                        RelationshipKind.OWNS, source_type, target_type
                    )
                
                error_message = str(context.exception)
                self.assertIn("OWNS relationship requires", error_message)
    
    
    
    def test_relationship_validation_with_empty_types(self):
        """Test relationship validation with empty or None types."""
        with self.assertRaises(InvalidEnumOperationError):
            EnumValidator.validate_relationship_context(
                RelationshipKind.GOVERNS, '', 'Actor'
            )
        
        with self.assertRaises(InvalidEnumOperationError):
            EnumValidator.validate_relationship_context(
                RelationshipKind.GOVERNS, 'Actor', None
            )
    
    def test_relationship_suggestions_generation(self):
        """Test that helpful suggestions are generated for invalid combinations."""
        with self.assertRaises(IncompatibleEnumError) as context:
            EnumValidator.validate_relationship_context(
                RelationshipKind.GOVERNS, 'Resource', 'Actor'  # Changed to invalid combination
            )
        
        error_message = str(context.exception)
        self.assertIn("Suggestions:", error_message)
        self.assertIn("Actor", error_message)


class TestFlowValidation(unittest.TestCase):
    """Test suite for flow combination validation."""
    
    def test_valid_flow_combinations(self):
        """Test valid flow nature and type combinations."""
        valid_combinations = [
            (FlowNature.FINANCIAL, FlowType.FINANCIAL),
            (FlowNature.MATERIAL, FlowType.MATERIAL),
            (FlowNature.ENERGY, FlowType.ENERGY),
            (FlowNature.INFORMATION, FlowType.INFORMATION),
            (FlowNature.INPUT, FlowType.SOCIAL),
            (FlowNature.OUTPUT, FlowType.SOCIAL)
        ]
        
        for nature, flow_type in valid_combinations:
            with self.subTest(nature=nature, flow_type=flow_type):
                try:
                    EnumValidator.validate_flow_combination(nature, flow_type)
                except Exception as e:
                    # Only expect errors for the specific incompatible combinations
                    if (nature, flow_type) not in [
                        (FlowNature.ENERGY, FlowType.INFORMATION),
                        (FlowNature.INFORMATION, FlowType.ENERGY)
                    ]:
                        self.fail(f"Valid combination {nature}->{flow_type} raised {e}")
    
    def test_invalid_flow_combinations(self):
        """Test invalid flow nature and type combinations."""
        invalid_combinations = [
            (FlowNature.ENERGY, FlowType.INFORMATION),
            (FlowNature.INFORMATION, FlowType.ENERGY)
        ]
        
        for nature, flow_type in invalid_combinations:
            with self.subTest(nature=nature, flow_type=flow_type):
                with self.assertRaises(IncompatibleEnumError) as context:
                    EnumValidator.validate_flow_combination(nature, flow_type)
                
                error_message = str(context.exception)
                self.assertIn("incompatible", error_message)
                self.assertIn(nature.name, error_message)
                self.assertIn(flow_type.name, error_message)
    
    


class TestInstitutionLayerValidation(unittest.TestCase):
    """Test suite for institution layer validation."""
    
    def test_valid_institution_layer_combinations(self):
        """Test valid institution layer and type combinations."""
        valid_combinations = [
            (InstitutionLayer.FORMAL_RULE, 'Institution'),
            (InstitutionLayer.FORMAL_RULE, 'Policy'),
            (InstitutionLayer.CULTURAL_VALUE, 'BeliefSystem'),
            (InstitutionLayer.KNOWLEDGE_SYSTEM, 'ValueSystem'),
            (InstitutionLayer.ORGANIZATION, 'Institution')
        ]
        
        for layer, institution_type in valid_combinations:
            with self.subTest(layer=layer, institution_type=institution_type):
                try:
                    EnumValidator.validate_institution_layer_context(layer, institution_type)
                except Exception as e:
                    # Only expect errors for specific incompatible combinations
                    if not (layer == InstitutionLayer.FORMAL_RULE and 
                           institution_type in ['BeliefSystem', 'ValueSystem']):
                        self.fail(f"Valid combination {layer}->{institution_type} raised {e}")
    
    def test_invalid_institution_layer_combinations(self):
        """Test invalid institution layer and type combinations."""
        invalid_combinations = [
            (InstitutionLayer.FORMAL_RULE, 'BeliefSystem'),
            (InstitutionLayer.FORMAL_RULE, 'ValueSystem')
        ]
        
        for layer, institution_type in invalid_combinations:
            with self.subTest(layer=layer, institution_type=institution_type):
                with self.assertRaises(IncompatibleEnumError) as context:
                    EnumValidator.validate_institution_layer_context(layer, institution_type)
                
                error_message = str(context.exception)
                self.assertIn("FORMAL_RULE layer is typically not appropriate", error_message)
                self.assertIn("Consider using CULTURAL_VALUE or KNOWLEDGE_SYSTEM layers", error_message)
    
    

class TestValidationDecorator(unittest.TestCase):
    """Test suite for validation decorator."""
    
    def test_validation_decorator_success(self):
        """Test validation decorator with successful operation."""
        @validate_enum_operation("test_operation")
        def successful_function(x, y):
            return x + y
        
        result = successful_function(1, 2)
        self.assertEqual(result, 3)
    
    def test_validation_decorator_with_error(self):
        """Test validation decorator with error handling."""
        @validate_enum_operation("test_operation")
        def failing_function():
            raise ValueError("Original error")
        
        with self.assertRaises(InvalidEnumOperationError) as context:
            failing_function()
        
        error_message = str(context.exception)
        self.assertIn("Invalid test_operation operation", error_message)
        self.assertIn("Original error", error_message)


class TestEnumValidatorEdgeCases(unittest.TestCase):
    """Test edge cases and comprehensive scenarios."""
    
    def test_comprehensive_relationship_coverage(self):
        """Test that all defined relationship rules work correctly."""
        # Test each relationship kind that has rules defined
        relationship_rules = EnumValidator.RELATIONSHIP_RULES
        
        for kind in relationship_rules:
            rule = relationship_rules[kind]
            valid_combinations = rule['valid_combinations']
            
            # Test at least one valid combination for each rule
            if valid_combinations:
                source_type, target_type = valid_combinations[0]
                try:
                    EnumValidator.validate_relationship_context(kind, source_type, target_type)
                except Exception as e:
                    self.fail(f"First valid combination for {kind.name} failed: {e}")
    
    def test_error_message_quality(self):
        """Test that error messages are informative and helpful."""
        with self.assertRaises(IncompatibleEnumError) as context:
            EnumValidator.validate_relationship_context(
                RelationshipKind.GOVERNS, 'Resource', 'Actor'  # Changed to invalid combination
            )
        
        error_message = str(context.exception)
        
        # Check that error message contains key information
        self.assertIn("GOVERNS", error_message)
        self.assertIn("Resource->Actor", error_message)
        self.assertIn("Suggestions:", error_message)
        
        # Error message should be reasonably long (informative)
        self.assertGreater(len(error_message), 50)
    
    def test_suggestion_generation_for_different_scenarios(self):
        """Test suggestion generation for various invalid scenarios."""
        test_cases = [
            (RelationshipKind.EMPLOYS, 'Actor', 'Resource'),
            (RelationshipKind.OWNS, 'Process', 'Actor'),
            (RelationshipKind.USES, 'Resource', 'Actor')
        ]
        
        for kind, source_type, target_type in test_cases:
            with self.subTest(kind=kind, source=source_type, target=target_type):
                with self.assertRaises(IncompatibleEnumError) as context:
                    EnumValidator.validate_relationship_context(kind, source_type, target_type)
                
                error_message = str(context.exception)
                # Each error should have either suggestions or clear guidance
                self.assertTrue(
                    "Suggestions:" in error_message or "Check the relationship documentation" in error_message,
                    f"Error message should provide guidance: {error_message}"
                )


if __name__ == '__main__':
    unittest.main()