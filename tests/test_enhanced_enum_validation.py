"""
Test suite for enhanced SFM enum validation features.

This module tests the new validation methods added to the EnumValidator class,
including policy instrument validation, value category context validation,
cross-enum dependencies, and required enum context validation.
"""

import unittest
from models.sfm_enums import (
    IncompatibleEnumError,
    InvalidEnumOperationError,
    EnumValidator,
    FlowNature,
    FlowType,
    PolicyInstrumentType,
    ValueCategory,
    InstitutionLayer,
)


class TestEnhancedFlowValidation(unittest.TestCase):
    """Test suite for enhanced flow combination validation."""
    
    def test_enhanced_invalid_flow_combinations(self):
        """Test enhanced invalid flow nature and type combinations."""
        enhanced_invalid_combinations = [
            # Physical flows cannot be purely informational
            (FlowNature.MATERIAL, FlowType.INFORMATION),
            (FlowNature.MATERIAL, FlowType.SOCIAL),
            # Financial flows cannot be material or energy
            (FlowNature.FINANCIAL, FlowType.MATERIAL),
            (FlowNature.FINANCIAL, FlowType.ENERGY),
            # Information flows cannot be material or energy
            (FlowNature.INFORMATION, FlowType.MATERIAL),
            # Energy flows cannot be informational or social
            (FlowNature.ENERGY, FlowType.SOCIAL),
            # Social flows are not material or energy based
            (FlowNature.SOCIAL, FlowType.MATERIAL),
            (FlowNature.SOCIAL, FlowType.ENERGY),
            # Service flows are not typically material
            (FlowNature.SERVICE, FlowType.MATERIAL),
            (FlowNature.SERVICE, FlowType.ENERGY),
            # Cultural flows are not material or energy based
            (FlowNature.CULTURAL, FlowType.MATERIAL),
            (FlowNature.CULTURAL, FlowType.ENERGY),
            # Regulatory flows are primarily informational
            (FlowNature.REGULATORY, FlowType.MATERIAL),
            (FlowNature.REGULATORY, FlowType.ENERGY),
        ]
        
        for nature, flow_type in enhanced_invalid_combinations:
            with self.subTest(nature=nature, flow_type=flow_type):
                with self.assertRaises(IncompatibleEnumError) as context:
                    EnumValidator.validate_flow_combination(nature, flow_type)
                
                error_message = str(context.exception)
                self.assertIn("incompatible", error_message)
                self.assertIn(nature.name, error_message)
                self.assertIn(flow_type.name, error_message)
    
    def test_valid_enhanced_flow_combinations(self):
        """Test that valid flow combinations still pass validation."""
        valid_combinations = [
            (FlowNature.FINANCIAL, FlowType.FINANCIAL),
            (FlowNature.MATERIAL, FlowType.MATERIAL),
            (FlowNature.ENERGY, FlowType.ENERGY),
            (FlowNature.INFORMATION, FlowType.INFORMATION),
            (FlowNature.SOCIAL, FlowType.SOCIAL),
            (FlowNature.CULTURAL, FlowType.INFORMATION),  # Cultural info flows
            (FlowNature.SERVICE, FlowType.SOCIAL),  # Service social flows
        ]
        
        for nature, flow_type in valid_combinations:
            with self.subTest(nature=nature, flow_type=flow_type):
                # Should not raise an exception
                EnumValidator.validate_flow_combination(nature, flow_type)


class TestPolicyInstrumentValidation(unittest.TestCase):
    """Test suite for policy instrument validation."""
    
    def test_valid_policy_instrument_combinations(self):
        """Test valid policy instrument combinations."""
        valid_combinations = [
            (PolicyInstrumentType.REGULATORY, 'mandatory'),
            (PolicyInstrumentType.ECONOMIC, 'market_incentive'),
            (PolicyInstrumentType.VOLUNTARY, 'voluntary'),
            (PolicyInstrumentType.INFORMATION, 'information_provision'),
            (PolicyInstrumentType.INFORMATION, 'awareness_building'),
        ]
        
        for instrument_type, context in valid_combinations:
            with self.subTest(instrument_type=instrument_type, context=context):
                # Should not raise an exception
                EnumValidator.validate_policy_instrument_combination(instrument_type, context)
    
    def test_invalid_policy_instrument_combinations(self):
        """Test invalid policy instrument combinations."""
        invalid_combinations = [
            (PolicyInstrumentType.REGULATORY, 'voluntary'),
            (PolicyInstrumentType.REGULATORY, 'market_based'),
            (PolicyInstrumentType.ECONOMIC, 'information_provision'),
            (PolicyInstrumentType.ECONOMIC, 'awareness_building'),
        ]
        
        for instrument_type, context in invalid_combinations:
            with self.subTest(instrument_type=instrument_type, context=context):
                with self.assertRaises(IncompatibleEnumError) as error_context:
                    EnumValidator.validate_policy_instrument_combination(instrument_type, context)
                
                error_message = str(error_context.exception)
                self.assertIn("may not be appropriate", error_message)
                self.assertIn(instrument_type.name, error_message)
                self.assertIn(context, error_message)
    
    def test_policy_instrument_validation_with_invalid_types(self):
               
        with self.assertRaises(InvalidEnumOperationError):
            EnumValidator.validate_policy_instrument_combination(PolicyInstrumentType.REGULATORY, "")


class TestValueCategoryValidation(unittest.TestCase):
    """Test suite for value category context validation."""
    
    def test_valid_value_category_contexts(self):
        """Test valid value category contexts."""
        valid_combinations = [
            (ValueCategory.ECONOMIC, 'quantitative'),
            (ValueCategory.PERFORMANCE, 'quantitative'),
            (ValueCategory.CULTURAL, 'qualitative'),
            (ValueCategory.SPIRITUAL, 'qualitative'),
            (ValueCategory.SOCIAL, 'mixed'),  # Should not raise error
        ]
        
        for category, context in valid_combinations:
            with self.subTest(category=category, context=context):
                # Should not raise an exception
                EnumValidator.validate_value_category_context(category, context)
    
    def test_invalid_value_category_contexts(self):
        """Test invalid value category contexts."""
        invalid_combinations = [
            (ValueCategory.CULTURAL, 'quantitative'),
            (ValueCategory.SPIRITUAL, 'quantitative'),
            (ValueCategory.AESTHETIC, 'quantitative'),
            (ValueCategory.ECONOMIC, 'qualitative'),
            (ValueCategory.PERFORMANCE, 'qualitative'),
        ]
        
        for category, context in invalid_combinations:
            with self.subTest(category=category, context=context):
                with self.assertRaises(IncompatibleEnumError) as error_context:
                    EnumValidator.validate_value_category_context(category, context)
                
                error_message = str(error_context.exception)
                self.assertIn(category.name, error_message)
                # Check that the error message mentions measurement approach
                self.assertTrue(
                    "quantitative" in error_message or "qualitative" in error_message,
                    f"Expected measurement approach mention in: {error_message}"
                )
    
    

class TestCrossEnumDependencyValidation(unittest.TestCase):
    """Test suite for cross-enum dependency validation."""
    
    def test_valid_cross_enum_dependencies(self):
        """Test valid cross-enum dependencies."""
        valid_combinations = [
            (FlowNature.FINANCIAL, InstitutionLayer.FORMAL_RULE, 'governance'),
            (FlowNature.CULTURAL, InstitutionLayer.CULTURAL_VALUE, 'governance'),
            (FlowNature.MATERIAL, InstitutionLayer.ORGANIZATION, 'governance'),
        ]
        
        for primary, dependent, relationship in valid_combinations:
            with self.subTest(primary=primary, dependent=dependent, relationship=relationship):
                # Should not raise an exception
                EnumValidator.validate_cross_enum_dependency(primary, dependent, relationship)
    
    def test_invalid_cross_enum_dependencies(self):
        """Test invalid cross-enum dependencies."""
        invalid_combinations = [
            (FlowNature.FINANCIAL, InstitutionLayer.INFORMAL_NORM, 'governance'),
            (FlowNature.CULTURAL, InstitutionLayer.FORMAL_RULE, 'governance'),
        ]
        
        for primary, dependent, relationship in invalid_combinations:
            with self.subTest(primary=primary, dependent=dependent, relationship=relationship):
                with self.assertRaises(IncompatibleEnumError) as error_context:
                    EnumValidator.validate_cross_enum_dependency(primary, dependent, relationship)
                
                error_message = str(error_context.exception)
                self.assertIn(primary.name, error_message)
                self.assertIn(dependent.name, error_message)
    
    def test_cross_enum_validation_with_invalid_types(self):
        """Test cross-enum validation with invalid types."""
        with self.assertRaises(InvalidEnumOperationError):
            EnumValidator.validate_cross_enum_dependency(
                FlowNature.FINANCIAL, InstitutionLayer.FORMAL_RULE, ""
            )


class TestRequiredEnumContextValidation(unittest.TestCase):
    """Test suite for required enum context validation."""
    
    def test_valid_required_enum_contexts(self):
        """Test valid required enum contexts."""
        valid_combinations = [
            (FlowNature.FINANCIAL, 'financial_transaction', True),
            (PolicyInstrumentType.REGULATORY, 'policy_implementation', True),
            (ValueCategory.ECONOMIC, 'value_measurement', True),
            (FlowNature.MATERIAL, 'optional_context', False),  # Optional usage
        ]
        
        for enum_value, context, is_required in valid_combinations:
            with self.subTest(enum_value=enum_value, context=context, is_required=is_required):
                # Should not raise an exception
                EnumValidator.validate_required_enum_context(enum_value, context, is_required)
    
    def test_invalid_required_enum_contexts(self):
        """Test invalid required enum contexts."""
        invalid_combinations = [
            (ValueCategory.ECONOMIC, 'financial_transaction', True),  # Wrong enum type for context
            (PolicyInstrumentType.REGULATORY, 'value_measurement', True),
        ]
        
        for enum_value, context, is_required in invalid_combinations:
            with self.subTest(enum_value=enum_value, context=context, is_required=is_required):
                with self.assertRaises(InvalidEnumOperationError) as error_context:
                    EnumValidator.validate_required_enum_context(enum_value, context, is_required)
                
                error_message = str(error_context.exception)
                self.assertIn("requires one of these enum types", error_message)
                self.assertIn(context, error_message)
    
    def test_required_enum_validation_with_invalid_types(self):
        """Test required enum validation with invalid types."""
        with self.assertRaises(InvalidEnumOperationError):
            EnumValidator.validate_required_enum_context(FlowNature.FINANCIAL, "", True)


if __name__ == '__main__':
    unittest.main()